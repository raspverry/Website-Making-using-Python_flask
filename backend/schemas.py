from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SiteCreate(BaseModel):
    url: str
    name: Optional[str] = None


class SiteResponse(BaseModel):
    uid: str
    url: str
    name: str
    compliance_score: Optional[int]
    last_scan_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    uid: str
    status: str
    score: Optional[int]
    pages_scanned: int
    total_violations: int
    critical_count: int
    serious_count: int
    moderate_count: int
    minor_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ViolationResponse(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    wcag_criteria: Optional[str]
    description: str
    element_html: Optional[str]
    page_url: Optional[str]
    fix_suggestion: Optional[str]
    selector: Optional[str]
    
    class Config:
        from_attributes = True


class ScanResultResponse(BaseModel):
    scan: ScanResponse
    violations: list[ViolationResponse]


class AgentQuestion(BaseModel):
    question: str


class AgentAnswer(BaseModel):
    answer: str


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    plan: str

    class Config:
        from_attributes = True
