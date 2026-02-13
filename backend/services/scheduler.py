"""
Scheduled scan service for PageGuard.

Runs as a background daemon thread. Every 60 seconds, checks for sites
that are due for a recurring scan and queues them.

Plan schedule:
  - Free: no auto-scan
  - Starter: weekly (every 168 hours)
  - Pro: daily (every 24 hours)
  - Agency: daily (every 24 hours)
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from backend.config import settings
from backend.database import SessionLocal
from backend.models import Site, Scan, User
from backend.services.plan_service import get_plan_limits, get_max_pages

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60  # How often to check for due scans


def _calculate_next_scan(user_plan: str, from_time: datetime | None = None) -> datetime | None:
    """Calculate the next scan time based on user plan. Returns None if no auto-scan."""
    limits = get_plan_limits(user_plan)
    interval_hours = limits.get("scan_interval_hours", 0)
    if interval_hours <= 0:
        return None
    base = from_time or datetime.now(timezone.utc)
    return base + timedelta(hours=interval_hours)


def schedule_next_scan(site: Site, user_plan: str, db):
    """Set the next_scan_at on a site after a scan completes."""
    next_time = _calculate_next_scan(user_plan)
    site.next_scan_at = next_time
    db.commit()


def _run_scheduled_scans():
    """Check for and execute any due scheduled scans."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # Find sites due for scan (next_scan_at <= now, and no scan currently running)
        due_sites = (
            db.query(Site)
            .filter(Site.next_scan_at.isnot(None), Site.next_scan_at <= now)
            .all()
        )

        if not due_sites:
            return

        logger.info("Scheduler found %d site(s) due for scan", len(due_sites))

        for site in due_sites:
            try:
                user = db.query(User).filter(User.id == site.user_id).first()
                if not user:
                    continue

                # Skip if user plan no longer supports auto-scan
                limits = get_plan_limits(user.plan)
                if limits.get("scan_interval_hours", 0) <= 0:
                    site.next_scan_at = None
                    db.commit()
                    continue

                # Skip if a scan is already running for this site
                running = db.query(Scan).filter(
                    Scan.site_id == site.id,
                    Scan.status.in_(["pending", "running"]),
                ).first()
                if running:
                    # Push next_scan_at forward by 10 minutes to retry later
                    site.next_scan_at = now + timedelta(minutes=10)
                    db.commit()
                    continue

                # Check monthly scan limit
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                monthly_count = (
                    db.query(Scan)
                    .join(Site)
                    .filter(Site.user_id == user.id, Scan.created_at >= month_start)
                    .count()
                )
                max_scans = limits["scans_per_month"]
                if max_scans != -1 and monthly_count >= max_scans:
                    # Hit limit — schedule for next month
                    site.next_scan_at = _calculate_next_scan(user.plan, now + timedelta(days=1))
                    db.commit()
                    logger.info("Site %s hit monthly scan limit, deferring", site.uid)
                    continue

                # Create scan and queue it
                max_pages = limits["max_pages"]
                has_ai = limits["ai_fixes"]

                scan = Scan(site_id=site.id, status="pending")
                db.add(scan)
                db.commit()
                db.refresh(scan)

                from backend.services.task_runner import run_in_background
                from backend.services.scan_task import execute_scan

                run_in_background(execute_scan, scan.id, site.id, site.url, max_pages, has_ai)

                # Schedule next scan
                site.next_scan_at = _calculate_next_scan(user.plan)
                db.commit()

                logger.info(
                    "Scheduled scan started for %s (site=%s, next=%s)",
                    site.url, site.uid,
                    site.next_scan_at.isoformat() if site.next_scan_at else "none",
                )

            except Exception as e:
                logger.error("Error processing scheduled scan for site %s: %s", site.uid, e)
                # Push back to retry later
                site.next_scan_at = now + timedelta(minutes=30)
                db.commit()

    except Exception as e:
        logger.error("Scheduler error: %s", e, exc_info=True)
    finally:
        db.close()


def _scheduler_loop():
    """Main scheduler loop — runs forever as a daemon thread."""
    logger.info("Scan scheduler started (checking every %ds)", CHECK_INTERVAL_SECONDS)
    while True:
        try:
            _run_scheduled_scans()
        except Exception as e:
            logger.error("Scheduler loop error: %s", e, exc_info=True)
        time.sleep(CHECK_INTERVAL_SECONDS)


_scheduler_thread: threading.Thread | None = None


def start_scheduler():
    """Start the scheduler background thread. Safe to call multiple times."""
    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return

    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        name="scan-scheduler",
        daemon=True,
    )
    _scheduler_thread.start()
    logger.info("Scan scheduler thread started")
