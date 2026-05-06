"""
PointsEngine — encapsulates all points-related operations with atomic
database transactions. Implements SDD §3.2 PointsEngine module spec.
"""
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy import text, update
from sqlalchemy.orm import Session

from .config import settings
from .models import PointRecord, User, Resource, Redemption, Download


class InsufficientBalance(Exception):
    pass


class AlreadyRated(Exception):
    pass


def _record_transaction(
    db: Session, user_id: int, action_type: str, delta: int,
    balance_after: int, resource_id: int | None = None
):
    """Append to point_records audit log."""
    record = PointRecord(
        user_id=user_id,
        resource_id=resource_id,
        action_type=action_type,
        points_delta=delta,
        balance_after=balance_after,
    )
    db.add(record)


def get_balance(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.user_id == user_id).first()
    return user.points_balance if user else 0


def get_free_downloads_today(db: Session, user_id: int) -> int:
    """How many FREE_DOWNLOAD records exist for this user today?"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    count = (
        db.query(PointRecord)
        .filter(
            PointRecord.user_id == user_id,
            PointRecord.action_type == "FREE_DOWNLOAD",
            PointRecord.created_at >= today_start,
        )
        .count()
    )
    return count


def award_upload(db: Session, user_id: int, resource_id: int) -> int:
    """Award upload reward atomically. Returns new balance."""
    return _award(db, user_id, settings.UPLOAD_REWARD, "UPLOAD_APPROVED", resource_id)


def award_download_received(db: Session, uploader_id: int, resource_id: int) -> int:
    return _award(db, uploader_id, settings.DOWNLOAD_RECEIVED_REWARD,
                  "DOWNLOAD_RECEIVED", resource_id)


def award_rating_received(db: Session, uploader_id: int, resource_id: int) -> int:
    return _award(db, uploader_id, settings.RATING_RECEIVED_REWARD,
                  "RATING_RECEIVED", resource_id)


def _award(db: Session, user_id: int, delta: int, action: str,
           resource_id: int | None = None) -> int:
    """
    Atomic credit operation. Uses a single SQL UPDATE with WHERE-guard so
    the read-modify-write happens atomically on BOTH MariaDB (with FOR UPDATE
    row-lock semantics) and SQLite (which serializes writers via DB lock).
    """
    result = db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(points_balance=User.points_balance + delta)
    )
    if result.rowcount == 0:
        raise ValueError(f"User {user_id} not found")
    db.flush()
    user = db.query(User).filter(User.user_id == user_id).first()
    new_balance = user.points_balance
    _record_transaction(db, user_id, action, delta, new_balance, resource_id)
    return new_balance


def charge_download(
    db: Session, user_id: int, resource_id: int
) -> Tuple[int, bool, bool]:
    """
    Charge a download. Returns (new_balance, used_free, success).

    Implements SDD §3.4 / FR-14 with database-level atomicity:
    1. Try atomic UPDATE with WHERE balance>=5 guard. If rowcount==1, success.
    2. Else fall back to free-download budget check.
    3. Else raise InsufficientBalance.

    The WHERE-guard pattern is concurrency-safe on BOTH MariaDB and SQLite
    because the entire condition is evaluated inside the storage engine's
    write lock, eliminating read-modify-write races.
    """
    cost = settings.DOWNLOAD_COST

    # Attempt atomic deduction
    result = db.execute(
        update(User)
        .where(User.user_id == user_id, User.points_balance >= cost)
        .values(points_balance=User.points_balance - cost)
    )

    used_free = False
    if result.rowcount == 1:
        # Charge succeeded
        db.flush()
        user = db.query(User).filter(User.user_id == user_id).first()
        new_balance = user.points_balance
        _record_transaction(
            db, user_id, "SPEND_DOWNLOAD", -cost, new_balance, resource_id
        )
    else:
        # Insufficient balance — try free download
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        free_used = get_free_downloads_today(db, user_id)
        if free_used >= settings.DAILY_FREE_DOWNLOADS:
            raise InsufficientBalance(
                f"Insufficient balance ({user.points_balance}) and "
                f"daily free downloads exhausted ({free_used}/{settings.DAILY_FREE_DOWNLOADS})"
            )
        new_balance = user.points_balance
        _record_transaction(
            db, user_id, "FREE_DOWNLOAD", 0, new_balance, resource_id
        )
        used_free = True

    # Atomic increment of resource download count
    db.execute(
        update(Resource)
        .where(Resource.resource_id == resource_id)
        .values(download_count=Resource.download_count + 1)
    )

    # Log the download
    db.add(Download(resource_id=resource_id, user_id=user_id))

    return new_balance, used_free, True


def redeem(
    db: Session, user_id: int, reward_type: str,
    resource_id: int | None = None
) -> Tuple[int, dict]:
    """
    Redeem points for a reward.
    Returns (new_balance, reward_info).

    Supported reward_type:
    - DOWNLOAD_CREDIT_10: 50 pts -> +10 download_credits
    - PIN_7DAYS: 100 pts -> resource pinned for 7 days (resource_id required)
    """
    if reward_type == "DOWNLOAD_CREDIT_10":
        cost = settings.REDEEM_DOWNLOAD_CREDIT_10_COST
        action = "REDEEM_DOWNLOAD_CREDIT"
        reward_db_type = "DOWNLOAD_CREDIT"
    elif reward_type == "PIN_7DAYS":
        cost = settings.REDEEM_PIN_7DAYS_COST
        action = "REDEEM_PIN"
        reward_db_type = "PIN"
        if not resource_id:
            raise ValueError("resource_id required for PIN_7DAYS reward")
    else:
        raise ValueError(f"Unknown reward type: {reward_type}")

    # Atomic deduction with WHERE-guard (race-safe on both MariaDB and SQLite)
    if reward_type == "DOWNLOAD_CREDIT_10":
        result = db.execute(
            update(User)
            .where(User.user_id == user_id, User.points_balance >= cost)
            .values(
                points_balance=User.points_balance - cost,
                download_credits=User.download_credits + 10,
            )
        )
    else:
        result = db.execute(
            update(User)
            .where(User.user_id == user_id, User.points_balance >= cost)
            .values(points_balance=User.points_balance - cost)
        )

    if result.rowcount == 0:
        # Insufficient balance OR user missing
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        raise InsufficientBalance(f"Need {cost} pts, have {user.points_balance}")

    db.flush()
    user = db.query(User).filter(User.user_id == user_id).first()
    new_balance = user.points_balance
    _record_transaction(db, user_id, action, -cost, new_balance, resource_id)

    # Apply reward
    expires_at = None
    reward_info = {"type": reward_db_type, "cost": cost}

    if reward_type == "DOWNLOAD_CREDIT_10":
        reward_info["download_credits_added"] = 10
        reward_info["new_total_credits"] = user.download_credits
    elif reward_type == "PIN_7DAYS":
        expires_at = datetime.utcnow() + timedelta(days=7)
        db.execute(
            update(Resource)
            .where(Resource.resource_id == resource_id)
            .values(pinned_until=expires_at)
        )
        reward_info["expires_at"] = expires_at.isoformat()

    redemption = Redemption(
        user_id=user_id,
        reward_type=reward_db_type,
        points_cost=cost,
        resource_id=resource_id,
        expires_at=expires_at,
    )
    db.add(redemption)

    return new_balance, reward_info
