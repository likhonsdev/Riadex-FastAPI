from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from domain.entities.message import ChatRequest
from application.services.chat_service import ChatService
from application.services.session_service import SessionService

router = APIRouter()

async def get_chat_service():
    return ChatService()

async def get_session_service():
    return SessionService()

@router.post("/sessions/{session_id}/chat")
async def chat_with_session(
    session_id: str,
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service)
):
    """Send a message to the session and receive streaming response"""
    try:
        # Verify session exists
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create SSE stream
        async def generate_sse() -> AsyncGenerator[str, None]:
            async for chunk in chat_service.process_chat_message(session_id, request):
                yield chunk
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
