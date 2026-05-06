"""
Resource endpoints: /api/resources/*
"""
import os
import shutil
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Resource, ResourceTag, Tag, User
from ..schemas import ResourceResponse, DownloadResponse
from ..auth import get_current_user, get_current_user_optional
from ..points_engine import charge_download, award_upload, InsufficientBalance
from ..search_engine import search_resources, get_related


router = APIRouter(prefix="/api/resources", tags=["resources"])


ALLOWED_EXT = {".pdf": "PDF", ".docx": "DOCX", ".pptx": "PPTX",
               ".png": "IMAGE", ".jpg": "IMAGE", ".jpeg": "IMAGE"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _ensure_or_create_tag(db: Session, name: str, category: str = "KEYWORD") -> Tag:
    tag = db.query(Tag).filter(Tag.tag_name == name).first()
    if not tag:
        tag = Tag(tag_name=name, category=category)
        db.add(tag)
        db.flush()
    return tag


@router.get("/search")
def search(
    keyword: Optional[str] = None,
    course_code: Optional[str] = None,
    academic_year: Optional[int] = None,
    resource_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results, total = search_resources(
        db, keyword, course_code, academic_year,
        resource_type, min_rating, page, page_size
    )
    return {"total": total, "page": page, "page_size": page_size, "results": results}


@router.get("/{resource_id}")
def get_resource_detail(resource_id: int, db: Session = Depends(get_db)):
    r = db.query(Resource).filter(
        Resource.resource_id == resource_id,
        Resource.status == "PUBLISHED",
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Resource not found")
    uploader = db.query(User).filter(User.user_id == r.uploader_id).first()
    related = get_related(db, resource_id, limit=3)
    now = datetime.utcnow()
    return {
        "resource_id": r.resource_id,
        "title": r.title,
        "description": r.description,
        "file_type": r.file_type,
        "file_size": r.file_size,
        "course_code": r.course_code,
        "academic_year": r.academic_year,
        "resource_type": r.resource_type,
        "status": r.status,
        "avg_rating": float(r.avg_rating) if r.avg_rating else None,
        "download_count": r.download_count,
        "uploader_id": r.uploader_id,
        "uploader_name": uploader.username if uploader else "unknown",
        "pinned": bool(r.pinned_until and r.pinned_until > now),
        "created_at": r.created_at,
        "related": related,
    }


@router.post("/upload")
async def upload_resource(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    course_code: str = Form(...),
    academic_year: int = Form(...),
    resource_type: str = Form(...),
    tags: str = Form(...),  # comma-separated
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"File type {ext} not allowed. Allowed: PDF/DOCX/PPTX/PNG/JPG")

    # Save file
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    safe_name = f"{int(datetime.utcnow().timestamp())}_{file.filename}".replace(" ", "_")
    save_path = os.path.join(settings.STORAGE_DIR, safe_name)

    size = 0
    with open(save_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                out.close()
                os.remove(save_path)
                raise HTTPException(413, "File exceeds 50MB limit")
            out.write(chunk)

    # Validate tag count
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if len(tag_list) < 2:
        os.remove(save_path)
        raise HTTPException(400, "At least 2 tags required")

    # Create resource (PENDING by default)
    resource = Resource(
        title=title,
        description=description,
        file_path=save_path,
        file_type=ALLOWED_EXT[ext],
        file_size=size,
        course_code=course_code,
        academic_year=academic_year,
        resource_type=resource_type,
        status="PENDING",
        uploader_id=user.user_id,
    )
    db.add(resource)
    db.flush()

    # Link tags
    for tname in tag_list:
        tag = _ensure_or_create_tag(db, tname)
        db.add(ResourceTag(resource_id=resource.resource_id, tag_id=tag.tag_id))

    user.upload_count += 1
    db.commit()
    db.refresh(resource)

    return {
        "message": "Upload submitted, awaiting admin review",
        "resource_id": resource.resource_id,
        "status": resource.status,
        "info": "You will earn +10 points after admin approval",
    }


@router.post("/{resource_id}/download", response_model=DownloadResponse)
def download(
    resource_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    r = db.query(Resource).filter(
        Resource.resource_id == resource_id,
        Resource.status == "PUBLISHED",
    ).first()
    if not r:
        raise HTTPException(404, "Resource not found")

    try:
        new_balance, used_free, _ = charge_download(db, user.user_id, resource_id)
    except InsufficientBalance as e:
        db.rollback()
        raise HTTPException(402, str(e))  # 402 Payment Required

    # Award uploader (if different person and not self-download)
    if r.uploader_id != user.user_id:
        from ..points_engine import award_download_received
        award_download_received(db, r.uploader_id, resource_id)

    db.commit()

    file_name = os.path.basename(r.file_path)
    return DownloadResponse(
        download_url=f"/api/resources/{resource_id}/file",
        file_name=file_name,
        points_charged=0 if used_free else settings.DOWNLOAD_COST,
        new_balance=new_balance,
        free_used=used_free,
    )


@router.get("/{resource_id}/file")
def serve_file(
    resource_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Serve the actual file. Auth-gated — only authenticated users who have
    a download record for this resource can access.
    """
    from ..models import Download as DownloadModel

    # Verify the user has actually paid/recorded a download
    has_download = db.query(DownloadModel).filter(
        DownloadModel.resource_id == resource_id,
        DownloadModel.user_id == user.user_id,
    ).first()
    if not has_download:
        raise HTTPException(403, "You must initiate a download via POST /api/resources/{id}/download first")

    r = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not r or not os.path.exists(r.file_path):
        raise HTTPException(404, "File not found on disk")

    return FileResponse(
        path=r.file_path,
        filename=os.path.basename(r.file_path),
        media_type="application/octet-stream",
    )


@router.get("")
def list_my_resources(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(Resource).filter(Resource.uploader_id == user.user_id).all()
    return [
        {
            "resource_id": r.resource_id,
            "title": r.title,
            "course_code": r.course_code,
            "status": r.status,
            "avg_rating": float(r.avg_rating) if r.avg_rating else None,
            "download_count": r.download_count,
            "created_at": r.created_at,
        }
        for r in rows
    ]
