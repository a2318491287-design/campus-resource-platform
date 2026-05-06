"""
SQLAlchemy ORM models — 1:1 mapping with the MySQL schema specified in
SDD v1.0 §8 (Database Design).
"""
from datetime import datetime
from sqlalchemy import (
    Integer, String, Text, BigInteger, ForeignKey, DateTime, Enum,
    Boolean, Numeric, UniqueConstraint, Index, CheckConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    points_balance: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    upload_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_credits: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("points_balance >= 0", name="ck_points_balance_nonneg"),
    )


class Resource(Base):
    __tablename__ = "resources"

    resource_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(
        Enum("PDF", "DOCX", "PPTX", "IMAGE", "OTHER", name="filetype"),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    course_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(
        Enum("NOTES", "PAST_PAPER", "ASSIGNMENT", "LECTURE", "GUIDE", "OTHER",
             name="resourcetype"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("PENDING", "PUBLISHED", "REJECTED", "REMOVED", name="resourcestatus"),
        default="PENDING", nullable=False, index=True,
    )
    avg_rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    uploader_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pinned_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(
        Enum("COURSE", "TYPE", "KEYWORD", name="tagcategory"),
        nullable=False, index=True,
    )


class ResourceTag(Base):
    __tablename__ = "resource_tags"

    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True
    )


class Rating(Base):
    __tablename__ = "ratings"

    rating_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.resource_id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource_rating"),
        CheckConstraint("stars BETWEEN 1 AND 5", name="ck_stars_range"),
    )


class PointRecord(Base):
    __tablename__ = "point_records"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.resource_id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(
        Enum(
            "UPLOAD_APPROVED", "DOWNLOAD_RECEIVED", "RATING_RECEIVED",
            "SPEND_DOWNLOAD", "REDEEM_DOWNLOAD_CREDIT", "REDEEM_PIN",
            "FREE_DOWNLOAD", "WELCOME_BONUS",
            name="pointactiontype",
        ),
        nullable=False,
    )
    points_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False, index=True
    )


class Download(Base):
    __tablename__ = "downloads"

    download_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.resource_id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)


class Redemption(Base):
    __tablename__ = "redemptions"

    redemption_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    reward_type: Mapped[str] = mapped_column(
        Enum("DOWNLOAD_CREDIT", "PIN", name="rewardtype"),
        nullable=False,
    )
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.resource_id", ondelete="SET NULL"), nullable=True
    )
    activated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
