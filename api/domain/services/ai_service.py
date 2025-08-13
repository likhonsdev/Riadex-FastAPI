from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any

class AIService(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, Any]]) -> str:
        pass
    
    @abstractmethod
    async def generate_response_stream(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        pass
