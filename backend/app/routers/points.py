"""
Points endpoints: /api/points/*
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PointRecord, Resource, User
from ..schemas import PointsBalanceResponse, PointRecordResponse, RedeemRequest
from ..auth import get_current_user
from ..points_engine import redeem, get_free_downloads_today, InsufficientBalance
from ..config import settings


router = APIRouter(prefix="/api/points", tags=["points"])


@router.get("/balance", response_model=PointsBalanceResponse)
def balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    free_used = get_free_downloads_today(db, user.user_id)
    return PointsBalanceResponse(
        points_balance=user.points_balance,
        download_credits=user.download_credits,
        free_downloads_today=settings.DAILY_FREE_DOWNLOADS,
        free_downloads_used=free_used,
    )


@router.get("/history")
def history(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(PointRecord)
        .filter(PointRecord.user_id == user.user_id)
        .order_by(PointRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    out = []
    for r in records:
        title = None
        if r.resource_id:
            res = db.query(Resource).filter(Resource.resource_id == r.resource_id).first()
            if res:
                title = res.title
        out.append({
            "record_id": r.record_id,
            "action_type": r.action_type,
            "points_delta": r.points_delta,
            "balance_after": r.balance_after,
            "resource_id": r.resource_id,
            "resource_title": title,
            "created_at": r.created_at,
        })
    return out


@router.get("/leaderboard")
def leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    """Top contributors this month by total points earned."""
    from datetime import datetime
    from sqlalchemy import func

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    rows = (
        db.query(
            User.user_id,
            User.username,
            func.sum(PointRecord.points_delta).label("monthly_earned"),
        )
        .join(PointRecord, User.user_id == PointRecord.user_id)
        .filter(
            PointRecord.action_type.in_([
                "UPLOAD_APPROVED", "DOWNLOAD_RECEIVED", "RATING_RECEIVED"
            ]),
            PointRecord.created_at >= month_start,
        )
        .group_by(User.user_id, User.username)
        .order_by(func.sum(PointRecord.points_delta).desc())
        .limit(limit)
        .all()
    )
    return [
        {"rank": i + 1, "username": row.username, "monthly_earned": int(row.monthly_earned or 0)}
        for i, row in enumerate(rows)
    ]


@router.post("/redeem")
def redeem_endpoint(
    req: RedeemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_balance, info = redeem(db, user.user_id, req.reward_type, req.resource_id)
    except InsufficientBalance as e:
        db.rollback()
        raise HTTPException(402, str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    db.commit()
    return {"new_balance": new_balance, "reward": info}
