from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.message import MessageEntity

class MessageRepository(ABC):
    @abstractmethod
    async def create(self, message: MessageEntity) -> MessageEntity:
        pass
    
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> List[MessageEntity]:
        pass
    
    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        pass
    
    @abstractmethod
    async def delete_by_session_id(self, session_id: str) -> bool:
        pass
