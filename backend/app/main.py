"""
Campus Academic Resource Sharing Platform — Backend API
FastAPI entry point.

Run locally:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

API docs:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base
from .routers import auth, resources, points, ratings, admin


# Create tables on startup (idempotent)
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Campus Resource Platform API",
    description="校园学术资源共享平台后端 API · System Analysis and Design Project",
    version="1.0.0",
)


# CORS — allow the prototype HTML to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount routers
app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(points.router)
app.include_router(ratings.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "service": "Campus Resource Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
