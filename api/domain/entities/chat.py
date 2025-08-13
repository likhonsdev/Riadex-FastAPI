from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: UUID = uuid4()
    chat_session_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class ChatSession(BaseModel):
    id: UUID = uuid4()
    user_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True
