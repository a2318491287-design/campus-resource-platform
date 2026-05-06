"""
Pydantic request/response schemas for API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# === Auth ===
class RegisterRequest(BaseModel):
    student_id: str = Field(min_length=8, max_length=20)
    username: str = Field(min_length=2, max_length=50)
    email: str = Field(max_length=100)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    student_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    student_id: str
    username: str
    email: str
    points_balance: int
    upload_count: int
    download_credits: int
    is_admin: bool


# === Resources ===
class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource_id: int
    title: str
    description: Optional[str]
    file_type: str
    file_size: int
    course_code: str
    academic_year: int
    resource_type: str
    status: str
    avg_rating: Optional[float]
    download_count: int
    uploader_id: int
    uploader_name: Optional[str] = None
    pinned: bool = False
    relevance_score: Optional[float] = None
    created_at: datetime


class SearchRequest(BaseModel):
    keyword: Optional[str] = None
    course_code: Optional[str] = None
    academic_year: Optional[int] = None
    resource_type: Optional[str] = None
    min_rating: Optional[float] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UploadMetadata(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    course_code: str
    academic_year: int = Field(ge=2018, le=2030)
    resource_type: str
    tags: list[str] = Field(min_length=2)


# === Points ===
class PointsBalanceResponse(BaseModel):
    points_balance: int
    download_credits: int
    free_downloads_today: int
    free_downloads_used: int


class PointRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int
    action_type: str
    points_delta: int
    balance_after: int
    resource_id: Optional[int]
    resource_title: Optional[str] = None
    created_at: datetime


class RedeemRequest(BaseModel):
    reward_type: str  # DOWNLOAD_CREDIT_10 | PIN_7DAYS
    resource_id: Optional[int] = None  # required for PIN


# === Ratings ===
class SubmitRatingRequest(BaseModel):
    resource_id: int
    stars: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=500)


class RatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating_id: int
    user_id: int
    stars: int
    comment: Optional[str]
    created_at: datetime


# === Admin ===
class ReviewDecision(BaseModel):
    decision: str  # APPROVE | REJECT
    rejection_reason: Optional[str] = None


# === Download ===
class DownloadResponse(BaseModel):
    download_url: str
    file_name: str
    points_charged: int
    new_balance: int
    free_used: bool
