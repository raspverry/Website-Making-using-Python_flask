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


@router.get("/sites/{site_uid}/badge.svg")
def get_badge(site_uid: str, db: Session = Depends(get_db)):
    """Public endpoint: returns a compliance badge SVG for embedding.
    Only available for Pro+ plans with score >= 70."""
    site = db.query(Site).filter(Site.uid == site_uid).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    user = db.query(User).filter(User.id == site.user_id).first()
    if not user or user.plan not in ("pro", "agency"):
        raise HTTPException(status_code=403, detail="Badge requires Pro plan or above")

    score = site.compliance_score
    if score is None or score < 70:
        # Badge only for sites that pass basic threshold
        color = "#6B7280"
        label = "Not Verified"
    elif score >= 90:
        color = "#16A34A"
        label = f"Score: {score}/100"
    elif score >= 70:
        color = "#2563EB"
        label = f"Score: {score}/100"
    else:
        color = "#6B7280"
        label = "Not Verified"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="36" role="img" aria-label="PageGuard: {label}">
  <title>PageGuard: {label}</title>
  <rect rx="4" width="200" height="36" fill="#1F2937"/>
  <rect x="80" rx="4" width="120" height="36" fill="{color}"/>
  <rect rx="4" width="200" height="36" fill="url(#g)"/>
  <defs><linearGradient id="g" x2="0" y2="100%"><stop offset="0" stop-opacity=".1" stop-color="#fff"/><stop offset="1" stop-opacity=".1"/></linearGradient></defs>
  <g fill="#fff" font-family="Verdana,sans-serif" font-size="11">
    <text x="8" y="23" font-weight="bold">PageGuard</text>
    <text x="88" y="23">{label}</text>
  </g>
</svg>"""

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/sites/{site_uid}/badge-embed")
def get_badge_embed(
    site_uid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Get the embed code for the compliance badge. Pro+ only."""
    site = db.query(Site).filter(Site.uid == site_uid, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if current_user.plan not in ("pro", "agency"):
        raise HTTPException(status_code=403, detail="Badge requires Pro plan or above")

    badge_url = f"{settings.FRONTEND_URL}/api/v1/sites/{site_uid}/badge.svg"
    site_url = f"{settings.FRONTEND_URL}/dashboard/sites/{site_uid}"
    embed_html = f'<a href="{site_url}" target="_blank" rel="noopener"><img src="{badge_url}" alt="PageGuard Accessibility Verified" width="200" height="36"></a>'

    return {"badge_url": badge_url, "embed_html": embed_html}
