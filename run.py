import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings, BASE_DIR
from app.core.database import Base, engine
from app.routers import auth, dashboard, resources, verifications, admin, api

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Centralized Syllabus-Aligned Study Material Platform for Engineering Students",
    version="1.0.0"
)

# Mount static files with absolute path
static_dir = os.path.join(BASE_DIR, "app", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(resources.router)
app.include_router(verifications.router)
app.include_router(admin.router)
app.include_router(api.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[ERROR] Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)}
    )

if __name__ == "__main__":
    print(f"[INFO] Starting {settings.PROJECT_NAME} server on http://127.0.0.1:8000 ...")
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)
