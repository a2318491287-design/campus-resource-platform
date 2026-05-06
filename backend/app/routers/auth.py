"""
Authentication endpoints: /api/auth/*
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, PointRecord
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from ..auth import (
    create_access_token, hash_password, verify_password,
    get_current_user,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])

WELCOME_BONUS = 100


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = User(
        student_id=req.student_id,
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        points_balance=WELCOME_BONUS,
    )
    try:
        db.add(user)
        db.flush()
        # Audit trail for the registration bonus
        db.add(PointRecord(
            user_id=user.user_id,
            resource_id=None,
            action_type="WELCOME_BONUS",
            points_delta=WELCOME_BONUS,
            balance_after=WELCOME_BONUS,
        ))
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student ID or email already registered",
        )

    token = create_access_token(user.user_id)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == req.student_id).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid student ID or password",
        )
    token = create_access_token(user.user_id)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
