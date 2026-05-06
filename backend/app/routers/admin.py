"""
Admin endpoints: /api/admin/*
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Resource, User, PointRecord, Redemption, Download
from ..schemas import ReviewDecision
from ..auth import require_admin
from ..points_engine import award_upload


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Aggregate dashboard counters."""
    return {
        "users_total": db.query(User).count(),
        "users_admin": db.query(User).filter(User.is_admin == True).count(),
        "resources_total": db.query(Resource).count(),
        "resources_published": db.query(Resource).filter(Resource.status == "PUBLISHED").count(),
        "resources_pending": db.query(Resource).filter(Resource.status == "PENDING").count(),
        "resources_rejected": db.query(Resource).filter(Resource.status == "REJECTED").count(),
        "downloads_total": db.query(Download).count(),
        "point_records_total": db.query(PointRecord).count(),
        "redemptions_total": db.query(Redemption).count(),
        "points_circulating": int(db.query(func.sum(User.points_balance)).scalar() or 0),
    }


@router.get("/users")
def admin_list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """All users (no password hashes)."""
    rows = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "user_id": u.user_id,
            "student_id": u.student_id,
            "username": u.username,
            "email": u.email,
            "points_balance": u.points_balance,
            "download_credits": u.download_credits,
            "upload_count": u.upload_count,
            "is_admin": bool(u.is_admin),
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in rows
    ]


@router.get("/resources")
def admin_list_resources(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """All resources regardless of status, with uploader name."""
    rows = (
        db.query(Resource, User.username)
        .join(User, Resource.uploader_id == User.user_id)
        .order_by(Resource.created_at.desc())
        .all()
    )
    return [
        {
            "resource_id": r.resource_id,
            "title": r.title,
            "course_code": r.course_code,
            "academic_year": r.academic_year,
            "type": r.resource_type,
            "status": r.status,
            "uploader_name": uname,
            "download_count": r.download_count,
            "avg_rating": float(r.avg_rating) if r.avg_rating else 0,
            "pinned_until": r.pinned_until.isoformat() if r.pinned_until else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r, uname in rows
    ]


@router.get("/points")
def admin_list_points(
    limit: int = 100,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Recent point ledger entries with user name."""
    rows = (
        db.query(PointRecord, User.username)
        .join(User, PointRecord.user_id == User.user_id)
        .order_by(PointRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.record_id,
            "user_name": uname,
            "action_type": p.action_type,
            "points_delta": p.points_delta,
            "balance_after": p.balance_after,
            "resource_id": p.resource_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p, uname in rows
    ]


@router.get("/queue")
def review_queue(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List pending resources awaiting review."""
    rows = (
        db.query(Resource, User.username)
        .join(User, Resource.uploader_id == User.user_id)
        .filter(Resource.status == "PENDING")
        .order_by(Resource.created_at)
        .all()
    )
    return [
        {
            "resource_id": r.resource_id,
            "title": r.title,
            "course_code": r.course_code,
            "uploader_name": uname,
            "created_at": r.created_at,
        }
        for r, uname in rows
    ]


@router.patch("/resources/{resource_id}/review")
def review_resource(
    resource_id: int,
    decision: ReviewDecision,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    r = db.query(Resource).filter(
        Resource.resource_id == resource_id,
        Resource.status == "PENDING",
    ).first()
    if not r:
        raise HTTPException(404, "Pending resource not found")

    if decision.decision.upper() == "APPROVE":
        r.status = "PUBLISHED"
        # Award uploader 10 pts
        award_upload(db, r.uploader_id, r.resource_id)
        action = "APPROVED"
    elif decision.decision.upper() == "REJECT":
        r.status = "REJECTED"
        r.rejection_reason = decision.rejection_reason or "No reason provided"
        action = "REJECTED"
    else:
        raise HTTPException(400, "decision must be APPROVE or REJECT")

    db.commit()
    return {"resource_id": resource_id, "new_status": r.status, "action": action}
