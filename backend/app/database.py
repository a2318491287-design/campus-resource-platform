"""
SQLAlchemy database session management.
Supports both MariaDB/MySQL (production) and SQLite (local dev).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings


# Auto-detect SQLite for local dev (no need for connect_args otherwise)
connect_args = {}
pool_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # MySQL/MariaDB: tune connection pool for ~40-50 concurrent users
    pool_kwargs = dict(
        pool_size=20,         # baseline: 20 concurrent DB sessions
        max_overflow=20,      # burst headroom: up to 40 total
        pool_timeout=10,      # fail fast if pool exhausted
    )

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    **pool_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: provides a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
