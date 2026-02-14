import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User, PasswordResetToken
from backend.schemas import UserCreate, UserResponse, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from backend.middleware import limiter
from backend.services.email_service import send_welcome_email, send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
RESET_TOKEN_EXPIRY_MINUTES = 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/signup")
@limiter.limit("5/minute")
def signup(request: Request, body: UserCreate, db: Session = Depends(get_db)):
    if not body.email or not body.password or not body.name:
        raise HTTPException(status_code=400, detail="All fields are required")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
        plan="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_welcome_email(user.email, user.name)

    token = create_token(user.id)
    return {
        "access_token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name, "plan": user.plan},
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user.id)
    return {
        "access_token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name, "plan": user.plan},
    }


def _cleanup_expired_tokens(db: Session):
    """Remove expired and used reset tokens from the database."""
    now = datetime.now(timezone.utc)
    db.query(PasswordResetToken).filter(
        (PasswordResetToken.expires_at < now) | (PasswordResetToken.used == 1)
    ).delete(synchronize_session=False)
    db.commit()


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email."""
    _cleanup_expired_tokens(db)

    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        # Don't reveal whether email exists
        return {"message": "If that email is registered, we've sent a reset link."}

    # Invalidate any existing tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id, PasswordResetToken.used == 0
    ).update({"used": 1}, synchronize_session=False)
    db.commit()

    token_str = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        token=token_str,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES),
    )
    db.add(reset_token)
    db.commit()

    send_password_reset_email(user.email, token_str)
    return {"message": "If that email is registered, we've sent a reset link."}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token from email."""
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == body.token,
        PasswordResetToken.used == 0,
    ).first()

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if token_record.expires_at < datetime.now(timezone.utc):
        token_record.used = 1
        db.commit()
        raise HTTPException(status_code=400, detail="Reset token has expired")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Mark token as used and update password
    token_record.used = 1
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "Password reset successfully"}
