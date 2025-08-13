from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from ..entities.chat import ChatSession, ChatMessage

class ChatRepository(ABC):
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        pass
    
    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        pass
    
    @abstractmethod
    async def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        pass
    
    @abstractmethod
    async def add_message(self, message: ChatMessage) -> ChatMessage:
        pass
    
    @abstractmethod
    async def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: UUID) -> bool:
        pass
