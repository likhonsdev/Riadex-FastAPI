from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from ...domain.entities.chat import MessageRole

class ChatSessionCreate(BaseModel):
    title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    messages: List['ChatMessageResponse'] = []
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    id: UUID
    chat_session_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class ChatMessageStreamResponse(BaseModel):
    type: str  # "message_chunk", "message_complete", "error"
    content: Optional[str] = None
    session_id: Optional[UUID] = None
    message: Optional[str] = None

# Forward reference resolution
ChatSessionResponse.model_rebuild()
