from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Site, Scan, Violation
from backend.schemas import AgentQuestion, AgentAnswer
from backend.services.ai_service import answer_question, generate_executive_summary

router = APIRouter(prefix="/api/v1", tags=["agent"])


@router.post("/sites/{site_uid}/agent/ask", response_model=AgentAnswer)
def ask_agent(site_uid: str, body: AgentQuestion, db: Session = Depends(get_db)):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    if len(body.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long (max 500 chars)")
    
    site = db.query(Site).filter(Site.uid == site_uid).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    scan = db.query(Scan).filter(Scan.site_id == site.id).order_by(Scan.created_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No scan data available")
    
    violations = db.query(Violation).filter(Violation.scan_id == scan.id).limit(20).all()
    violations_text = "\n".join(
        f"- [{v.severity}] {v.rule_name}: {v.description}" for v in violations
    )
    
    answer = answer_question(body.question, site.url, scan.score or 0, violations_text)
    return AgentAnswer(answer=answer)


@router.get("/sites/{site_uid}/agent/summary")
def get_summary(site_uid: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.uid == site_uid).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    scan = db.query(Scan).filter(Scan.site_id == site.id).order_by(Scan.created_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No scan data")
    
    violations = db.query(Violation).filter(Violation.scan_id == scan.id).limit(20).all()
    violations_text = "\n".join(
        f"- [{v.severity}] {v.rule_name}: {v.description}" for v in violations
    )
    
    summary = generate_executive_summary(
        site.url, scan.score or 0, scan.total_violations or 0,
        scan.critical_count or 0, scan.serious_count or 0, scan.moderate_count or 0,
        violations_text,
    )
    
    return {"summary": summary, "score": scan.score, "total_violations": scan.total_violations}
