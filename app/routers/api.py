from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Resource, CourseSubject, User
from app.schemas import ResourceResponse, CourseSubjectResponse, UserResponse
from app.services.search import SearchService

router = APIRouter(prefix="/api", tags=["REST API"])

@router.get("/resources", response_model=List[ResourceResponse])
def api_list_resources(
    query: Optional[str] = None,
    department: Optional[str] = None,
    subject_id: Optional[int] = None,
    type: Optional[str] = None,
    syllabus_version: Optional[str] = None,
    verified_only: bool = True,
    db: Session = Depends(get_db)
):
    resources = SearchService.search_resources(
        db=db,
        query=query,
        department=department,
        subject_id=subject_id,
        resource_type=type,
        syllabus_version=syllabus_version,
        verified_only=verified_only
    )
    return resources

@router.get("/subjects", response_model=List[CourseSubjectResponse])
def api_list_subjects(
    department: Optional[str] = None,
    semester: Optional[int] = None,
    db: Session = Depends(get_db)
):
    q = db.query(CourseSubject)
    if department:
        q = q.filter(CourseSubject.department == department)
    if semester:
        q = q.filter(CourseSubject.semester == semester)
    return q.all()

@router.get("/me", response_model=UserResponse)
def api_get_profile(user: User = Depends(get_current_user)):
    return user
