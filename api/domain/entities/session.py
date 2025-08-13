from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    STOPPED = "stopped"
    ERROR = "error"

class SessionEntity(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    title: str = Field(default="New Conversation", description="Session title")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="Session status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    latest_message: Optional[str] = Field(None, description="Latest message content")
    latest_message_at: Optional[datetime] = Field(None, description="Latest message timestamp")
    unread_message_count: int = Field(default=0, description="Unread message count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }

class SessionCreateRequest(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    title: str
    status: str
    created_at: int
    updated_at: int
    latest_message: Optional[str] = None
    latest_message_at: Optional[int] = None
    unread_message_count: int = 0

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
