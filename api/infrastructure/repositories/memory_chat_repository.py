from typing import Optional, List, Dict
from uuid import UUID
import structlog

from ...domain.entities.chat import ChatSession, ChatMessage
from ...domain.repositories.chat_repository import ChatRepository

logger = structlog.get_logger()

class MemoryChatRepository(ChatRepository):
    """In-memory implementation of ChatRepository for development/testing"""
    
    def __init__(self):
        self.sessions: Dict[UUID, ChatSession] = {}
        self.messages: Dict[UUID, List[ChatMessage]] = {}
    
    async def create_session(self, session: ChatSession) -> ChatSession:
        self.sessions[session.id] = session
        self.messages[session.id] = []
        logger.info("Created chat session", session_id=str(session.id))
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        session = self.sessions.get(session_id)
        if session:
            # Load messages
            session.messages = self.messages.get(session_id, [])
        return session
    
    async def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        user_sessions = [
            session for session in self.sessions.values()
            if session.user_id == user_id
        ]
        # Load messages for each session
        for session in user_sessions:
            session.messages = self.messages.get(session.id, [])
        return user_sessions
    
    async def add_message(self, message: ChatMessage) -> ChatMessage:
        if message.chat_session_id not in self.messages:
            self.messages[message.chat_session_id] = []
        
        self.messages[message.chat_session_id].append(message)
        logger.info("Added message to session", 
                   session_id=str(message.chat_session_id),
                   role=message.role.value)
        return message
    
    async def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        return self.messages.get(session_id, [])
    
    async def delete_session(self, session_id: UUID) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.messages:
                del self.messages[session_id]
            logger.info("Deleted chat session", session_id=str(session_id))
            return True
        return False
