"""Background scan task - runs website scan and saves results."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Scan, Site, User, Violation
from backend.services.scanner import run_scan
from backend.services.ai_service import generate_fix
from backend.services.email_service import send_scan_complete_email

logger = logging.getLogger(__name__)


def execute_scan(scan_id: int, site_id: int, site_url: str, max_pages: int = 5, ai_fixes: bool = True):
    """Execute a scan in the background. Uses its own DB session."""
    db: Session = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        site = db.query(Site).filter(Site.id == site_id).first()
        if not scan or not site:
            logger.error("Scan %s or Site %s not found", scan_id, site_id)
            return

        scan.status = "running"
        db.commit()

        logger.info("Starting scan for %s (scan_id=%s, max_pages=%s)", site_url, scan_id, max_pages)
        result = run_scan(site_url, max_pages=max_pages)

        scan.status = "completed"
        scan.score = result.score
        scan.pages_scanned = len(result.pages)
        scan.total_violations = result.total_violations
        scan.critical_count = result.critical_count
        scan.serious_count = result.serious_count
        scan.moderate_count = result.moderate_count
        scan.minor_count = result.minor_count
        scan.completed_at = datetime.now(timezone.utc)

        for page in result.pages:
            for v in page.violations:
                fix_text = ""
                if ai_fixes:
                    try:
                        fix_text = generate_fix(v.rule_id, v.description, v.element_html)
                    except Exception as e:
                        logger.warning("AI fix generation failed for %s: %s", v.rule_id, e)
                        fix_text = ""

                violation = Violation(
                    scan_id=scan.id,
                    rule_id=v.rule_id,
                    rule_name=v.rule_name,
                    severity=v.severity,
                    wcag_criteria=v.wcag_criteria,
                    description=v.description,
                    element_html=v.element_html,
                    page_url=page.url,
                    fix_suggestion=fix_text,
                    selector=v.selector,
                )
                db.add(violation)

        site.compliance_score = result.score
        site.last_scan_at = datetime.now(timezone.utc)
        db.commit()

        try:
            user = db.query(User).filter(User.id == site.user_id).first()
            if user:
                send_scan_complete_email(user.email, site_url, result.score, result.total_violations, site.uid)
        except Exception as e:
            logger.warning("Failed to send scan email: %s", e)

        logger.info("Scan %s completed: score=%s, violations=%s", scan_id, result.score, result.total_violations)

    except Exception as e:
        logger.error("Scan %s failed: %s", scan_id, e, exc_info=True)
        try:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
