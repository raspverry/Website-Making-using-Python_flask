"""Account management endpoints - profile, password, deletion (GDPR)."""
import logging

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_authenticated_user
from backend.models import User, Site, Subscription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/account", tags=["account"])


class UpdateProfile(BaseModel):
    name: str | None = None
    email: str | None = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


@router.get("/me")
def get_profile(current_user: User = Depends(get_authenticated_user)):
    """Get current user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "plan": current_user.plan,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.patch("/me")
def update_profile(
    body: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Update user profile (name, email)."""
    if body.name is not None:
        current_user.name = body.name.strip()
    if body.email is not None:
        email = body.email.strip().lower()
        existing = db.query(User).filter(User.email == email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        current_user.email = email
    db.commit()
    return {"status": "updated", "name": current_user.name, "email": current_user.email}


@router.post("/change-password")
def change_password(
    body: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Change password (requires current password)."""
    if not bcrypt.checkpw(body.current_password.encode(), current_user.password_hash.encode()):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    current_user.password_hash = bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt()).decode()
    db.commit()
    return {"status": "password_changed"}


@router.delete("/me")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Delete user account and all associated data (GDPR right to erasure)."""
    # Cancel Stripe subscription if exists
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if sub and sub.stripe_subscription_id:
        try:
            import stripe
            from backend.config import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            if settings.STRIPE_SECRET_KEY:
                stripe.Subscription.cancel(sub.stripe_subscription_id)
        except Exception as e:
            logger.warning("Failed to cancel Stripe subscription on account deletion: %s", e)

    # Delete user (cascade deletes sites, scans, violations, subscription)
    db.delete(current_user)
    db.commit()
    logger.info("User account deleted (GDPR erasure): user_id=%s", current_user.id)
    return {"status": "account_deleted"}
