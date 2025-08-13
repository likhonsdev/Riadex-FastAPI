from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class User(BaseModel):
    id: UUID = uuid4()
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
