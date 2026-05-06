"""
SearchEngine — implements relevance-ranked search per SDD §3.2.

Composite relevance score:
  score = WEIGHT_MATCH * match_score
        + WEIGHT_DOWNLOADS * normalized_downloads
        + WEIGHT_RATING * normalized_rating

Match score:
  - On MariaDB/MySQL: native FULLTEXT MATCH ... AGAINST
  - On SQLite: simple LIKE-based scoring (sufficient for demo)
"""
from datetime import datetime
from sqlalchemy import or_, func, case, literal
from sqlalchemy.orm import Session

from .config import settings
from .models import Resource, User


def search_resources(
    db: Session,
    keyword: str | None = None,
    course_code: str | None = None,
    academic_year: int | None = None,
    resource_type: str | None = None,
    min_rating: float | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """
    Return (results, total_count).
    Each result dict contains resource fields + uploader_name + relevance_score
    + pinned flag.
    """
    is_sqlite = db.bind.dialect.name == "sqlite"

    # Base query — only PUBLISHED resources
    query = db.query(Resource, User.username).join(
        User, Resource.uploader_id == User.user_id
    ).filter(Resource.status == "PUBLISHED")

    # Apply filters
    if course_code:
        query = query.filter(Resource.course_code == course_code)
    if academic_year:
        query = query.filter(Resource.academic_year == academic_year)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if min_rating is not None:
        query = query.filter(
            or_(Resource.avg_rating >= min_rating, Resource.avg_rating.is_(None))
        )

    # Keyword filter (case-insensitive LIKE; works on both engines)
    if keyword:
        kw_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Resource.title.ilike(kw_pattern),
                Resource.description.ilike(kw_pattern),
            )
        )

    total = query.count()

    # Compute relevance & order
    rows = query.all()
    now = datetime.utcnow()
    scored: list[dict] = []
    for r, uploader_name in rows:
        # Match score: 1.0 if exact title contains keyword, 0.7 if description, 0.3 otherwise
        if keyword:
            kw_l = keyword.lower()
            if kw_l in r.title.lower():
                match_score = 1.0
            elif r.description and kw_l in r.description.lower():
                match_score = 0.7
            else:
                match_score = 0.3
        else:
            match_score = 0.5

        downloads_score = min(r.download_count / 1000.0, 1.0)
        rating_score = float(r.avg_rating or 0) / 5.0

        relevance = (
            settings.WEIGHT_MATCH * match_score
            + settings.WEIGHT_DOWNLOADS * downloads_score
            + settings.WEIGHT_RATING * rating_score
        )

        # Pinned resources get a +0.5 boost so they rise to the top
        pinned = bool(r.pinned_until and r.pinned_until > now)
        if pinned:
            relevance += 0.5

        scored.append({
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
            "uploader_name": uploader_name,
            "pinned": pinned,
            "relevance_score": round(relevance, 3),
            "created_at": r.created_at,
        })

    # Sort by relevance descending
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Paginate
    start = (page - 1) * page_size
    return scored[start:start + page_size], total


def get_related(db: Session, resource_id: int, limit: int = 3) -> list[dict]:
    """Return resources from the same course (excluding the source)."""
    src = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not src:
        return []
    rows = (
        db.query(Resource, User.username)
        .join(User, Resource.uploader_id == User.user_id)
        .filter(
            Resource.status == "PUBLISHED",
            Resource.course_code == src.course_code,
            Resource.resource_id != resource_id,
        )
        .order_by(Resource.download_count.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "resource_id": r.resource_id,
            "title": r.title,
            "course_code": r.course_code,
            "avg_rating": float(r.avg_rating) if r.avg_rating else None,
            "download_count": r.download_count,
            "uploader_name": uploader_name,
        }
        for r, uploader_name in rows
    ]
