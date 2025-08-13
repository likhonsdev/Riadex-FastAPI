from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from domain.entities.session import SessionCreateRequest, SessionResponse, SessionListResponse
from application.services.session_service import SessionService
from presentation.schemas.response import APIResponse

router = APIRouter()

async def get_session_service():
    return SessionService()

@router.put("/sessions", response_model=APIResponse)
async def create_session(
    request: Optional[SessionCreateRequest] = None,
    session_service: SessionService = Depends(get_session_service)
):
    """Create a new conversation session"""
    try:
        session = await session_service.create_session(request)
        return APIResponse(
            code=0,
            msg="success",
            data={"session_id": session.session_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=APIResponse)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Get session information including conversation history"""
    try:
        session_data = await session_service.get_session_with_events(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            code=0,
            msg="success",
            data=session_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=APIResponse)
async def list_sessions(
    session_service: SessionService = Depends(get_session_service)
):
    """Get list of all sessions"""
    try:
        sessions = await session_service.list_sessions()
        
        session_responses = [
            SessionResponse(
                session_id=session.session_id,
                title=session.title,
                status=session.status,
                created_at=int(session.created_at.timestamp()),
                updated_at=int(session.updated_at.timestamp()),
                latest_message=session.latest_message,
                latest_message_at=int(session.latest_message_at.timestamp()) if session.latest_message_at else None,
                unread_message_count=session.unread_message_count
            )
            for session in sessions
        ]
        
        return APIResponse(
            code=0,
            msg="success",
            data=SessionListResponse(sessions=session_responses).dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}", response_model=APIResponse)
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Delete a session"""
    try:
        success = await session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            code=0,
            msg="success",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/stop", response_model=APIResponse)
async def stop_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Stop an active session"""
    try:
        success = await session_service.stop_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            code=0,
            msg="success",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
