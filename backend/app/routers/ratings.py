"""
Rating endpoints: /api/ratings/*
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Rating, Resource, User
from ..schemas import SubmitRatingRequest
from ..auth import get_current_user
from ..points_engine import award_rating_received


router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.post("")
def submit_rating(
    req: SubmitRatingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(
        Resource.resource_id == req.resource_id,
        Resource.status == "PUBLISHED",
    ).first()
    if not resource:
        raise HTTPException(404, "Resource not found")

    rating = Rating(
        resource_id=req.resource_id,
        user_id=user.user_id,
        stars=req.stars,
        comment=req.comment,
    )
    try:
        db.add(rating)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You have already rated this resource")

    # Recompute resource average rating
    avg = (
        db.query(func.avg(Rating.stars))
        .filter(Rating.resource_id == req.resource_id)
        .scalar()
    )
    resource.avg_rating = float(avg) if avg else None

    # Award uploader if rating ≥ 4 stars and not self
    if req.stars >= 4 and resource.uploader_id != user.user_id:
        award_rating_received(db, resource.uploader_id, req.resource_id)

    db.commit()
    return {
        "rating_id": rating.rating_id,
        "stars": rating.stars,
        "new_avg_rating": float(avg) if avg else None,
    }


@router.get("/{resource_id}")
def list_ratings(resource_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Rating, User.username)
        .join(User, Rating.user_id == User.user_id)
        .filter(Rating.resource_id == resource_id)
        .order_by(Rating.created_at.desc())
        .all()
    )
    return [
        {
            "rating_id": r.rating_id,
            "stars": r.stars,
            "comment": r.comment,
            "username": uname,
            "created_at": r.created_at,
        }
        for r, uname in rows
    ]
