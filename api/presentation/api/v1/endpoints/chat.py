from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from uuid import UUID, uuid4
import json
import structlog

from ....application.services.chat_service import ChatService
from ....infrastructure.services.gemini_ai_service import GeminiAIService
from ....infrastructure.repositories.memory_chat_repository import MemoryChatRepository
from ....presentation.schemas.chat import (
    ChatSessionCreate, ChatSessionResponse, 
    ChatMessageCreate, ChatMessageResponse,
    ChatMessageStreamResponse
)

logger = structlog.get_logger()
router = APIRouter()

# Dependency injection - in production, use proper DI container
def get_chat_service() -> ChatService:
    chat_repository = MemoryChatRepository()
    ai_service = GeminiAIService()
    return ChatService(chat_repository, ai_service)

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    try:
        # For demo purposes, using a fixed user_id
        # In production, get this from authentication
        user_id = uuid4()
        
        session = await chat_service.create_session(
            user_id=user_id,
            title=session_data.title
        )
        return ChatSessionResponse.from_orm(session)
    except Exception as e:
        logger.error("Error creating chat session", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get a specific chat session with messages"""
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return ChatSessionResponse.from_orm(session)

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: UUID,
    message_data: ChatMessageCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message and get AI response"""
    try:
        # Verify session exists
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Send message and get response
        response_message = await chat_service.send_message(
            session_id=session_id,
            content=message_data.content
        )
        
        return ChatMessageResponse.from_orm(response_message)
    except Exception as e:
        logger.error("Error sending message", error=str(e), session_id=str(session_id))
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: UUID,
    message_data: ChatMessageCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message and get streaming AI response via SSE"""
    try:
        # Verify session exists
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        async def generate_sse():
            try:
                async for chunk in chat_service.send_message_stream(
                    session_id=session_id,
                    content=message_data.content
                ):
                    # Format as Server-Sent Events
                    sse_data = {
                        "type": "message_chunk",
                        "content": chunk,
                        "session_id": str(session_id)
                    }
                    yield f"data: {json.dumps(sse_data)}\n\n"
                
                # Send completion event
                completion_data = {
                    "type": "message_complete",
                    "session_id": str(session_id)
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                logger.error("Error in SSE stream", error=str(e))
                error_data = {
                    "type": "error",
                    "message": "An error occurred while processing your message"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error setting up message stream", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to setup message stream")
