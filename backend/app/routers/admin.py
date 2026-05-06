"""
Admin endpoints: /api/admin/*
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Resource, User
from ..schemas import ReviewDecision
from ..auth import require_admin
from ..points_engine import award_upload


router = APIRouter(prefix="/api/admin", tags=["admin"])


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
