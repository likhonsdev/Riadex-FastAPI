from typing import AsyncGenerator
import uuid
import json
from datetime import datetime

from domain.entities.message import MessageEntity, MessageType, ChatRequest, ChatEvent
from domain.entities.session import SessionEntity
from domain.repositories.message_repository import MessageRepository
from infrastructure.repositories.mongodb_message_repository import MongoDBMessageRepository
from application.services.ai_service import AIService
from application.services.session_service import SessionService
import structlog

logger = structlog.get_logger()

class ChatService:
    def __init__(self):
        self.message_repo: MessageRepository = MongoDBMessageRepository()
        self.ai_service = AIService()
        self.session_service = SessionService()
    
    async def process_chat_message(self, session_id: str, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Process chat message and return SSE stream"""
        try:
            # Save user message
            user_message = MessageEntity(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                content=request.message,
                message_type=MessageType.USER,
                timestamp=datetime.utcnow(),
                event_id=request.event_id
            )
            await self.message_repo.create(user_message)
            
            # Update session with latest message
            await self.session_service.update_session_message(session_id, request.message)
            
            # Send title event (first message sets title)
            messages = await self.message_repo.get_by_session_id(session_id)
            if len(messages) <= 1:
                title = request.message[:50] + "..." if len(request.message) > 50 else request.message
                event = ChatEvent(event="title", data={"title": title})
                yield f"event: title\ndata: {json.dumps(event.dict())}\n\n"
            
            # Send plan event
            plan_event = ChatEvent(
                event="plan",
                data={
                    "steps": [
                        {"id": "analyze", "description": "Analyzing your request", "status": "running"},
                        {"id": "generate", "description": "Generating response", "status": "pending"},
                        {"id": "complete", "description": "Finalizing response", "status": "pending"}
                    ]
                }
            )
            yield f"event: plan\ndata: {json.dumps(plan_event.dict())}\n\n"
            
            # Update step status
            step_event = ChatEvent(
                event="step",
                data={"step_id": "analyze", "status": "completed"}
            )
            yield f"event: step\ndata: {json.dumps(step_event.dict())}\n\n"
            
            step_event = ChatEvent(
                event="step", 
                data={"step_id": "generate", "status": "running"}
            )
            yield f"event: step\ndata: {json.dumps(step_event.dict())}\n\n"
            
            # Generate AI response stream
            full_response = ""
            async for chunk in self.ai_service.generate_streaming_response(request.message):
                if chunk.get("type") == "message":
                    content = chunk.get("content", "")
                    full_response += content
                    
                    message_event = ChatEvent(
                        event="message",
                        data={"content": content, "partial": True}
                    )
                    yield f"event: message\ndata: {json.dumps(message_event.dict())}\n\n"
                elif chunk.get("type") == "error":
                    error_event = ChatEvent(
                        event="error",
                        data=chunk.get("data", {})
                    )
                    yield f"event: error\ndata: {json.dumps(error_event.dict())}\n\n"
                    return
            
            # Save AI response
            ai_message = MessageEntity(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                content=full_response,
                message_type=MessageType.ASSISTANT,
                timestamp=datetime.utcnow()
            )
            await self.message_repo.create(ai_message)
            
            # Update session with AI response
            await self.session_service.update_session_message(session_id, full_response)
            
            # Complete step
            step_event = ChatEvent(
                event="step",
                data={"step_id": "generate", "status": "completed"}
            )
            yield f"event: step\ndata: {json.dumps(step_event.dict())}\n\n"
            
            step_event = ChatEvent(
                event="step",
                data={"step_id": "complete", "status": "completed"}
            )
            yield f"event: step\ndata: {json.dumps(step_event.dict())}\n\n"
            
            # Send done event
            done_event = ChatEvent(
                event="done",
                data={"message": "Conversation completed successfully"}
            )
            yield f"event: done\ndata: {json.dumps(done_event.dict())}\n\n"
            
        except Exception as e:
            logger.error("Chat processing error", error=str(e))
            error_event = ChatEvent(
                event="error",
                data={"error": str(e)}
            )
            yield f"event: error\ndata: {json.dumps(error_event.dict())}\n\n"
