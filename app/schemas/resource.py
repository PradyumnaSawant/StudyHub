from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.course import CourseSubjectResponse

class ResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str # notes, PYQ, question_bank, revision
    subject_id: int
    syllabus_tag: str # e.g. Unit 1: Trees & Graphs

class ResourceResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    subject_id: int
    uploader_id: int
    file_url: str
    file_size: Optional[str] = None
    syllabus_tag: str
    verification_status: str
    upload_date: datetime
    download_count: int
    ai_summary: Optional[str] = None

    subject: Optional[CourseSubjectResponse] = None
    uploader: Optional[UserResponse] = None
    is_bookmarked: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class ResourceFilter(BaseModel):
    query: Optional[str] = None
    department: Optional[str] = None
    subject_id: Optional[int] = None
    type: Optional[str] = None
    syllabus_version: Optional[str] = None
    verified_only: Optional[bool] = False
