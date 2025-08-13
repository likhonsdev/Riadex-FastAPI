from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ToolType(str, Enum):
    BROWSER = "browser"
    SHELL = "shell"
    FILE = "file"
    SEARCH = "search"
    VNC = "vnc"

class ToolStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ToolEntity(BaseModel):
    tool_id: str = Field(..., description="Unique tool identifier")
    session_id: str = Field(..., description="Session identifier")
    tool_type: ToolType = Field(..., description="Tool type")
    status: ToolStatus = Field(default=ToolStatus.PENDING, description="Tool status")
    input_data: Dict[str, Any] = Field(..., description="Tool input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Tool output data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }

class ShellRequest(BaseModel):
    session_id: str = Field(..., description="Shell session ID")

class ShellResponse(BaseModel):
    output: str = Field(..., description="Shell output content")
    session_id: str = Field(..., description="Shell session ID")
    console: List[Dict[str, str]] = Field(..., description="Console history")

class FileRequest(BaseModel):
    file: str = Field(..., description="File path")

class FileResponse(BaseModel):
    content: str = Field(..., description="File content")
    file: str = Field(..., description="File path")
