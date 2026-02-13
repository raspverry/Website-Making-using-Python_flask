"""Plan enforcement service - checks user limits before allowing actions."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import User, Site, Scan

logger = logging.getLogger(__name__)


def get_plan_limits(plan: str) -> dict:
    """Return the limits for a given plan."""
    return settings.PLAN_LIMITS.get(plan, settings.PLAN_LIMITS["free"])


def check_site_limit(user: User, db: Session):
    """Raise 403 if user has reached their site limit."""
    limits = get_plan_limits(user.plan)
    site_count = db.query(Site).filter(Site.user_id == user.id).count()
    if site_count >= limits["sites"]:
        raise HTTPException(
            status_code=403,
            detail=f"Your {user.plan} plan allows {limits['sites']} site(s). Upgrade to add more.",
        )


def check_scan_limit(user: User, site: Site, db: Session):
    """Raise 403 if user has reached their monthly scan limit."""
    limits = get_plan_limits(user.plan)
    max_scans = limits["scans_per_month"]
    if max_scans == -1:  # unlimited
        return

    # Count scans this month
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    scan_count = (
        db.query(Scan)
        .join(Site)
        .filter(Site.user_id == user.id, Scan.created_at >= month_start)
        .count()
    )
    if scan_count >= max_scans:
        raise HTTPException(
            status_code=403,
            detail=f"Your {user.plan} plan allows {max_scans} scan(s) per month. Upgrade for more.",
        )


def get_max_pages(user: User) -> int:
    """Return the max pages allowed for scanning based on plan."""
    limits = get_plan_limits(user.plan)
    return limits["max_pages"]


def check_ai_access(user: User):
    """Raise 403 if user's plan doesn't include AI fix suggestions."""
    limits = get_plan_limits(user.plan)
    if not limits["ai_fixes"]:
        raise HTTPException(
            status_code=403,
            detail="AI fix suggestions are available on Starter plan and above. Upgrade to access.",
        )
