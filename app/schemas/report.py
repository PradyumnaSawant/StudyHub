from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class ReportCreate(BaseModel):
    resource_id: int
    reason: str

class ReportResponse(BaseModel):
    id: int
    resource_id: int
    reporter_id: int
    reason: str
    status: str # pending, resolved, dismissed
    created_at: datetime
    reporter: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
