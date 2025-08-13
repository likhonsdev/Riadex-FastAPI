from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[Any] = None
    
    class Config:
        json_encoders = {
            # Add custom encoders if needed
        }
