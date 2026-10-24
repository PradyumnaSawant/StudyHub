import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.models import Resource, Verification

templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)
router = APIRouter(prefix="/verification", tags=["Verification Hub"])

@router.get("", response_class=HTMLResponse)
def verification_hub(
    request: Request,
    status_filter: Optional[str] = "pending",
    db: Session = Depends(get_db)
):
    user = require_role(["Verifier", "Admin"])(request, db)

    query = db.query(Resource)
    if status_filter != "all":
        query = query.filter(Resource.verification_status == status_filter)

    resources = query.order_by(Resource.upload_date.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="verification.html",
        context={"user": user, "resources": resources, "status_filter": status_filter}
    )

@router.post("/{resource_id}/review")
def review_resource(
    resource_id: int,
    request: Request,
    status: str = Form(...), # verified, outdated, rejected
    comments: str = Form(None),
    db: Session = Depends(get_db)
):
    user = require_role(["Verifier", "Admin"])(request, db)

    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.verification_status = status

    verification = Verification(
        resource_id=resource_id,
        verifier_id=user.id,
        status=status,
        comments=comments.strip() if comments else None
    )
    db.add(verification)
    db.commit()

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request=request,
            name="components/verification_row.html",
            context={"resource": resource, "user": user}
        )

    return RedirectResponse(url="/verification", status_code=302)
