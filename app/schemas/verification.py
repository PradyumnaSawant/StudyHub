from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class VerificationCreate(BaseModel):
    resource_id: int
    status: str # verified, outdated, rejected
    comments: Optional[str] = None

class VerificationResponse(BaseModel):
    id: int
    resource_id: int
    verifier_id: int
    status: str
    comments: Optional[str] = None
    timestamp: datetime
    verifier: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
