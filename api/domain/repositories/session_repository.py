from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.session import SessionEntity

class SessionRepository(ABC):
    @abstractmethod
    async def create(self, session: SessionEntity) -> SessionEntity:
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[SessionEntity]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[SessionEntity]:
        pass
    
    @abstractmethod
    async def update(self, session: SessionEntity) -> SessionEntity:
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        pass
    
    @abstractmethod
    async def update_status(self, session_id: str, status: str) -> bool:
        pass
