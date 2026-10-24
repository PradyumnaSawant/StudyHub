import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import get_current_user_optional, get_current_user
from app.models import Resource, CourseSubject, Bookmark, Report, User
from app.services.storage import get_storage_service
from app.services.search import SearchService
from app.services.ai_summary import AISummarizerService

templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)
router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get("", response_class=HTMLResponse)
def list_resources(
    request: Request,
    query: Optional[str] = None,
    department: Optional[str] = "All",
    subject_id: Optional[int] = 0,
    type: Optional[str] = "All",
    syllabus_version: Optional[str] = "All",
    verified_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    user = get_current_user_optional(request, db)

    resources = SearchService.search_resources(
        db=db,
        query=query,
        department=department,
        subject_id=subject_id,
        resource_type=type,
        syllabus_version=syllabus_version,
        verified_only=verified_only
    )

    # Attach bookmark flags if user is logged in
    bookmarked_ids = set()
    if user:
        b_records = db.query(Bookmark.resource_id).filter(Bookmark.user_id == user.id).all()
        bookmarked_ids = {r[0] for r in b_records}

    for res in resources:
        res.is_bookmarked = res.id in bookmarked_ids

    subjects = db.query(CourseSubject).all()
    departments = sorted(list(set(s.department for s in subjects)))

    context = {
        "user": user,
        "resources": resources,
        "subjects": subjects,
        "departments": departments,
        "query": query or "",
        "selected_department": department or "All",
        "selected_subject_id": subject_id or 0,
        "selected_type": type or "All",
        "selected_syllabus_version": syllabus_version or "All",
        "verified_only": verified_only
    }

    # If request is from HTMX, render partial search results component
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request=request, name="components/search_results.html", context=context)

    return templates.TemplateResponse(request=request, name="resources.html", context=context)

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db) # Auth required
    subjects = db.query(CourseSubject).all()
    return templates.TemplateResponse(request=request, name="upload.html", context={"user": user, "subjects": subjects, "error": None})

@router.post("/upload")
async def process_upload(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    type: str = Form(...),
    subject_id: int = Form(...),
    syllabus_tag: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    storage_service = get_storage_service()
    file_url, file_size = await storage_service.save_file(file)

    # Initial status: Verifiers/Admins get auto-verified, students get "pending"
    initial_status = "verified" if user.role in ["Verifier", "Admin"] else "pending"

    new_resource = Resource(
        title=title.strip(),
        description=description.strip() if description else None,
        type=type,
        subject_id=subject_id,
        uploader_id=user.id,
        file_url=file_url,
        file_size=file_size,
        syllabus_tag=syllabus_tag.strip(),
        verification_status=initial_status
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return RedirectResponse(url=f"/resources/{new_resource.id}", status_code=302)

@router.get("/{resource_id}", response_class=HTMLResponse)
def get_resource_detail(resource_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Study resource not found")

    is_bookmarked = False
    if user:
        b = db.query(Bookmark).filter(Bookmark.user_id == user.id, Bookmark.resource_id == res.id).first()
        is_bookmarked = b is not None

    res.is_bookmarked = is_bookmarked

    return templates.TemplateResponse(
        request=request,
        name="resource_detail.html",
        context={"user": user, "resource": res}
    )

@router.get("/{resource_id}/download")
def download_resource(resource_id: int, db: Session = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")

    res.download_count += 1
    db.commit()

    # Serve file from local storage path.
    # file_url is stored as /static/uploads/... but files live under app/static/uploads/
    relative = res.file_url.lstrip("/")          # e.g. "static/uploads/abc.pdf"
    relative = "app/" + relative                  # e.g. "app/static/uploads/abc.pdf"
    local_path = os.path.join(BASE_DIR, relative)
    return FileResponse(path=local_path, filename=f"{res.title.replace(' ', '_')}.pdf")

@router.post("/{resource_id}/bookmark", response_class=HTMLResponse)
def toggle_bookmark(resource_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.resource_id == resource_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        is_bookmarked = False
    else:
        new_b = Bookmark(user_id=user.id, resource_id=resource_id)
        db.add(new_b)
        db.commit()
        is_bookmarked = True

    # Render small HTMX button replacement snippet
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    res.is_bookmarked = is_bookmarked
    return templates.TemplateResponse(
        request=request,
        name="components/bookmark_btn.html",
        context={"resource": res, "user": user}
    )

@router.post("/{resource_id}/ai-summary", response_class=HTMLResponse)
async def generate_ai_summary(resource_id: int, request: Request, db: Session = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Return cached AI summary if already generated
    if not res.ai_summary:
        summary = await AISummarizerService.generate_summary(
            title=res.title,
            subject_name=res.subject.name if res.subject else "General Engineering",
            resource_type=res.type,
            syllabus_tag=res.syllabus_tag,
            description=res.description
        )
        res.ai_summary = summary
        db.commit()

    return templates.TemplateResponse(
        request=request,
        name="components/summary_modal.html",
        context={"resource": res, "summary": res.ai_summary}
    )

@router.post("/{resource_id}/report")
def report_resource(
    resource_id: int,
    request: Request,
    reason: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    report = Report(resource_id=resource_id, reporter_id=user.id, reason=reason.strip())
    db.add(report)
    db.commit()
    return RedirectResponse(url=f"/resources/{resource_id}?reported=true", status_code=302)
