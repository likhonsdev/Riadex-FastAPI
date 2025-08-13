from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class MessageEntity(BaseModel):
    message_id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    event_id: Optional[str] = Field(None, description="Event identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message content")
    timestamp: Optional[int] = Field(None, description="Message timestamp")
    event_id: Optional[str] = Field(None, description="Event identifier")

class ChatEvent(BaseModel):
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
