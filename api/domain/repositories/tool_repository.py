from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.tool import ToolEntity

class ToolRepository(ABC):
    @abstractmethod
    async def create(self, tool: ToolEntity) -> ToolEntity:
        pass
    
    @abstractmethod
    async def get_by_id(self, tool_id: str) -> Optional[ToolEntity]:
        pass
    
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> List[ToolEntity]:
        pass
    
    @abstractmethod
    async def update(self, tool: ToolEntity) -> ToolEntity:
        pass
    
    @abstractmethod
    async def delete(self, tool_id: str) -> bool:
        pass
