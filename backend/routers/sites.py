from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Site, Scan, Violation
from backend.schemas import SiteCreate, SiteResponse, ScanResponse, ScanResultResponse, ViolationResponse
from backend.services.scanner import run_scan
from backend.services.ai_service import generate_fix

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
def list_sites(db: Session = Depends(get_db)):
    # TODO: filter by current user when auth is added
    sites = db.query(Site).order_by(Site.created_at.desc()).all()
    return sites


@router.post("/sites", response_model=SiteResponse)
def create_site(site_data: SiteCreate, db: Session = Depends(get_db)):
    try:
        url = normalize_url(site_data.url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    name = site_data.name or urlparse(url).netloc
    site = Site(url=url, name=name, user_id=1)  # TODO: use actual user
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/sites/{site_uid}", response_model=SiteResponse)
def get_site(site_uid: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.uid == site_uid).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.post("/sites/{site_uid}/scan", response_model=ScanResultResponse)
def start_scan(site_uid: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.uid == site_uid).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    scan = Scan(site_id=site.id, status="running")
    db.add(scan)
    db.commit()
    
    try:
        result = run_scan(site.url, max_pages=5)
        
        scan.status = "completed"
        scan.score = result.score
        scan.pages_scanned = len(result.pages)
        scan.total_violations = result.total_violations
        scan.critical_count = result.critical_count
        scan.serious_count = result.serious_count
        scan.moderate_count = result.moderate_count
        scan.minor_count = result.minor_count
        scan.completed_at = datetime.now(timezone.utc)
        
        violations = []
        for page in result.pages:
            for v in page.violations:
                fix_text = generate_fix(v.rule_id, v.description, v.element_html)
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
                violations.append(violation)
        
        site.compliance_score = result.score
        site.last_scan_at = datetime.now(timezone.utc)
        db.commit()
        
        return ScanResultResponse(
            scan=ScanResponse.model_validate(scan),
            violations=[ViolationResponse.model_validate(v) for v in violations],
        )
    except Exception as e:
        scan.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/sites/{site_uid}/latest-scan", response_model=ScanResultResponse)
def get_latest_scan(site_uid: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.uid == site_uid).first()
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
