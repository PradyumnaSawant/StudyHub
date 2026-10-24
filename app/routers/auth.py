import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user_optional
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse

templates_dir = os.path.join(BASE_DIR, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)
router = APIRouter(tags=["Authentication"])

@router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={"user": user, "error": None})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not db_user or not verify_password(password, db_user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"user": None, "error": "Invalid email or password"},
            status_code=400
        )

    access_token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role})
    
    redirect_res = RedirectResponse(url="/dashboard", status_code=302)
    redirect_res.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
    return redirect_res

@router.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="register.html", context={"user": user, "error": None})

@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("Student"),
    college: str = Form(None),
    course: str = Form("CSE"),
    semester: int = Form(1),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email.strip().lower()).first()
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"user": None, "error": "An account with this email already exists."},
            status_code=400
        )

    new_user = User(
        name=name.strip(),
        email=email.strip().lower(),
        password_hash=hash_password(password),
        role=role,
        college=college.strip() if college else "Engineering Institute",
        course=course,
        semester=semester
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    redirect_res = RedirectResponse(url="/dashboard", status_code=302)
    redirect_res.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
    return redirect_res

@router.get("/logout")
def logout(response: Response):
    redirect_res = RedirectResponse(url="/login", status_code=302)
    redirect_res.delete_cookie(key="access_token")
    return redirect_res

# JSON API Endpoints for Headless/SPA Clients
@router.post("/api/auth/register", response_model=TokenResponse)
def api_register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        college=payload.college,
        course=payload.course,
        semester=payload.semester
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

@router.post("/api/auth/login", response_model=TokenResponse)
def api_login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
