from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import Site, Scan, Violation, User
from backend.schemas import SiteCreate, SiteResponse, ScanResponse, ScanResultResponse, ViolationResponse
from backend.services.plan_service import check_site_limit, check_scan_limit, get_max_pages, check_ai_access
from backend.services.report import generate_pdf_report, generate_text_report
from backend.dependencies import get_authenticated_user
from backend.middleware import limiter

router = APIRouter(prefix="/api/v1", tags=["sites"])


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL")
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


@router.get("/sites", response_model=list[SiteResponse])
def list_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    sites = db.query(Site).filter(Site.user_id == current_user.id).order_by(Site.created_at.desc()).all()
    return sites


@router.post("/sites", response_model=SiteResponse)
def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    # Enforce plan site limit
    check_site_limit(current_user, db)

    try:
        url = normalize_url(site_data.url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid URL")

    name = site_data.name or urlparse(url).netloc
    site = Site(url=url, name=name, user_id=current_user.id)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/sites/{site_uid}", response_model=SiteResponse)
def get_site(
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.post("/sites/{site_uid}/scan", response_model=ScanResponse)
@limiter.limit("10/minute")
def start_scan(
    request: Request,
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Enforce plan scan limit
    check_scan_limit(current_user, site, db)

    # Check for running scan
    running = db.query(Scan).filter(
        Scan.site_id == site.id, Scan.status.in_(["pending", "running"])
    ).first()
    if running:
        raise HTTPException(status_code=409, detail="A scan is already in progress for this site")

    # Use plan-based page limit
    max_pages = get_max_pages(current_user)

    # Check if user has AI access for fix suggestions
    has_ai = True
    try:
        check_ai_access(current_user)
    except HTTPException:
        has_ai = False

    scan = Scan(site_id=site.id, status="pending")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Run scan in background
    from backend.services.task_runner import run_in_background
    from backend.services.scan_task import execute_scan

    run_in_background(execute_scan, scan.id, site.id, site.url, max_pages, has_ai)

    return ScanResponse.model_validate(scan)


@router.get("/scans/{scan_uid}", response_model=ScanResultResponse)
def get_scan(
    scan_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    scan = db.query(Scan).filter(Scan.uid == scan_uid).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Verify ownership
    site = db.query(Site).filter(Site.id == scan.site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Scan not found")

    violations = db.query(Violation).filter(Violation.scan_id == scan.id).all()
    return ScanResultResponse(
        scan=ScanResponse.model_validate(scan),
        violations=[ViolationResponse.model_validate(v) for v in violations],
    )


@router.get("/sites/{site_uid}/latest-scan", response_model=ScanResultResponse)
def get_latest_scan(
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    scan = db.query(Scan).filter(Scan.site_id == site.id).order_by(Scan.created_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No scans found")

    violations = db.query(Violation).filter(Violation.scan_id == scan.id).all()

    return ScanResultResponse(
        scan=ScanResponse.model_validate(scan),
        violations=[ViolationResponse.model_validate(v) for v in violations],
    )


@router.get("/sites/{site_uid}/report/pdf")
def download_pdf_report(
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Download a PDF compliance report for the latest scan. Requires Pro plan or above."""
    if current_user.plan not in ("pro", "agency"):
        raise HTTPException(status_code=403, detail="PDF reports are available on Pro plan and above.")

    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    scan = db.query(Scan).filter(Scan.site_id == site.id).order_by(Scan.created_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No scan data available")

    violations = db.query(Violation).filter(Violation.scan_id == scan.id).all()

    scan_data = {
        "score": scan.score,
        "pages_scanned": scan.pages_scanned,
        "total_violations": scan.total_violations,
        "critical_count": scan.critical_count,
        "serious_count": scan.serious_count,
        "moderate_count": scan.moderate_count,
        "minor_count": scan.minor_count,
        "completed_at": scan.completed_at.strftime("%Y-%m-%d %H:%M UTC") if scan.completed_at else None,
    }
    violations_data = [
        {
            "severity": v.severity,
            "rule_name": v.rule_name,
            "wcag_criteria": v.wcag_criteria,
            "page_url": v.page_url,
            "description": v.description,
            "element_html": v.element_html or "",
            "fix_suggestion": v.fix_suggestion or "",
        }
        for v in violations
    ]

    pdf_bytes = generate_pdf_report(site.url, scan_data, violations_data)
    filename = f"pageguard-report-{site_uid}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/sites/{site_uid}")
def delete_site(
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Delete a site and all its scan data."""
    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    db.delete(site)  # cascade deletes scans and violations
    db.commit()
    return {"status": "deleted"}
