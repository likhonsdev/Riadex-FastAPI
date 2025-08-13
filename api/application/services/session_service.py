from typing import List, Optional
import uuid
from datetime import datetime

from domain.entities.session import SessionEntity, SessionStatus, SessionCreateRequest
from domain.repositories.session_repository import SessionRepository
from domain.repositories.message_repository import MessageRepository
from infrastructure.repositories.mongodb_session_repository import MongoDBSessionRepository
from infrastructure.repositories.mongodb_message_repository import MongoDBMessageRepository

class SessionService:
    def __init__(self):
        self.session_repo: SessionRepository = MongoDBSessionRepository()
        self.message_repo: MessageRepository = MongoDBMessageRepository()
    
    async def create_session(self, request: Optional[SessionCreateRequest] = None) -> SessionEntity:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        session = SessionEntity(
            session_id=session_id,
            title=request.title if request and request.title else "New Conversation",
            status=SessionStatus.ACTIVE,
            metadata=request.metadata if request and request.metadata else {}
        )
        
        return await self.session_repo.create(session)
    
    async def get_session(self, session_id: str) -> Optional[SessionEntity]:
        """Get session by ID"""
        return await self.session_repo.get_by_id(session_id)
    
    async def get_session_with_events(self, session_id: str) -> Optional[dict]:
        """Get session with message history"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return None
        
        messages = await self.message_repo.get_by_session_id(session_id)
        
        return {
            "session_id": session.session_id,
            "title": session.title,
            "events": [
                {
                    "type": msg.message_type,
                    "content": msg.content,
                    "timestamp": int(msg.timestamp.timestamp()),
                    "event_id": msg.event_id
                }
                for msg in messages
            ]
        }
    
    async def list_sessions(self) -> List[SessionEntity]:
        """List all sessions"""
        return await self.session_repo.get_all()
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and its messages"""
        # Delete messages first
        await self.message_repo.delete_by_session_id(session_id)
        
        # Delete session
        return await self.session_repo.delete(session_id)
    
    async def stop_session(self, session_id: str) -> bool:
        """Stop an active session"""
        return await self.session_repo.update_status(session_id, SessionStatus.STOPPED)
    
    async def update_session_message(self, session_id: str, message: str) -> bool:
        """Update session's latest message"""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return False
        
        session.latest_message = message
        session.latest_message_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        await self.session_repo.update(session)
        return True
