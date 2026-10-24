import os
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import require_role
from app.models import User, CourseSubject, Resource, Report, Verification

templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)
router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.get("", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    admin_user = require_role(["Admin"])(request, db)

    users = db.query(User).order_by(User.id.desc()).all()
    subjects = db.query(CourseSubject).order_by(CourseSubject.department, CourseSubject.code).all()
    reports = db.query(Report).filter(Report.status == "pending").order_by(Report.created_at.desc()).all()
    stats = {
        "users": len(users),
        "verified_resources": db.query(Resource).filter(Resource.verification_status == "verified").count(),
        "pending_verifications": db.query(Resource).filter(Resource.verification_status == "pending").count(),
        "reports": len(reports)
    }

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": admin_user,
            "users": users,
            "subjects": subjects,
            "reports": reports,
            "stats": stats
        }
    )

@router.post("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    request: Request,
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(request, db)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
    return RedirectResponse(url="/admin#users", status_code=302)

@router.post("/subjects/create")
def create_subject(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    syllabus_version: str = Form("2024"),
    department: str = Form(...),
    semester: int = Form(1),
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(request, db)
    new_subject = CourseSubject(
        name=name.strip(),
        code=code.strip().upper(),
        syllabus_version=syllabus_version.strip(),
        department=department.strip().upper(),
        semester=semester
    )
    db.add(new_subject)
    db.commit()
    return RedirectResponse(url="/admin#subjects", status_code=302)

@router.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    request: Request,
    action: str = Form(...), # resolve, delete_resource, dismiss
    db: Session = Depends(get_db)
):
    require_role(["Admin"])(request, db)
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        if action == "delete_resource":
            db.delete(report.resource)
            report.status = "resolved"
        elif action == "resolve":
            report.status = "resolved"
        else:
            report.status = "dismissed"
        db.commit()
    return RedirectResponse(url="/admin#reports", status_code=302)
