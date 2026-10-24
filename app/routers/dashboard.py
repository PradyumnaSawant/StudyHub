import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import get_current_user_optional, get_current_user
from app.models import Resource, CourseSubject, Bookmark, Verification, Report, User

templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter(tags=["Dashboard"])

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    # Fetch high level platform stats
    total_resources = db.query(Resource).filter(Resource.verification_status == "verified").count()
    total_subjects = db.query(CourseSubject).count()
    total_students = db.query(User).filter(User.role == "Student").count()
    recent_resources = (
        db.query(Resource)
        .filter(Resource.verification_status == "verified")
        .order_by(Resource.upload_date.desc())
        .limit(6)
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            "total_resources": total_resources or 124,
            "total_subjects": total_subjects or 18,
            "total_students": total_students or 450,
            "recent_resources": recent_resources
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # 1. Enrolled/Personalized Department Subjects
    user_branch = user.course or "CSE"
    user_sem = user.semester or 1

    subjects = db.query(CourseSubject).filter(
        CourseSubject.department == user_branch,
        CourseSubject.semester == user_sem
    ).all()

    # Fallback to all subjects if specific sem is empty
    if not subjects:
        subjects = db.query(CourseSubject).filter(CourseSubject.department == user_branch).limit(6).all()

    # 2. Recommended Verified Resources for student
    subj_ids = [s.id for s in subjects]
    recommended_resources = []
    if subj_ids:
        recommended_resources = db.query(Resource).filter(
            Resource.subject_id.in_(subj_ids),
            Resource.verification_status == "verified"
        ).order_by(Resource.download_count.desc()).limit(8).all()
    else:
        recommended_resources = db.query(Resource).filter(
            Resource.verification_status == "verified"
        ).order_by(Resource.download_count.desc()).limit(8).all()

    # 3. User Bookmarks
    bookmarked_items = (
        db.query(Resource)
        .join(Bookmark, Bookmark.resource_id == Resource.id)
        .filter(Bookmark.user_id == user.id)
        .all()
    )
    bookmarked_ids = {r.id for r in bookmarked_items}

    # Attach bookmark flags
    for r in recommended_resources:
        r.is_bookmarked = r.id in bookmarked_ids

    # 4. Role specific metrics
    pending_verifications = 0
    pending_reports = 0
    if user.role in ["Verifier", "Admin"]:
        pending_verifications = db.query(Resource).filter(Resource.verification_status == "pending").count()
        pending_reports = db.query(Report).filter(Report.status == "pending").count()

    user_uploads = db.query(Resource).filter(Resource.uploader_id == user.id).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "subjects": subjects,
            "recommended_resources": recommended_resources,
            "bookmarked_resources": bookmarked_items,
            "user_uploads": user_uploads,
            "pending_verifications": pending_verifications,
            "pending_reports": pending_reports
        }
    )
