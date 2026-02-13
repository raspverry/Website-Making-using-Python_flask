import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from backend.database import Base


def _uid():
    return uuid.uuid4().hex[:12]


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    plan = Column(String(20), nullable=False, default="free")
    stripe_customer_id = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    sites = relationship("Site", back_populates="owner", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(12), unique=True, nullable=False, default=_uid, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(500), nullable=False)
    name = Column(String(100), nullable=False)
    compliance_score = Column(Integer)
    last_scan_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="sites")
    scans = relationship("Scan", back_populates="site", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(12), unique=True, nullable=False, default=_uid)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    score = Column(Integer)
    pages_scanned = Column(Integer, default=0)
    total_violations = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    serious_count = Column(Integer, default=0)
    moderate_count = Column(Integer, default=0)
    minor_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    
    site = relationship("Site", back_populates="scans")
    violations = relationship("Violation", back_populates="scan", cascade="all, delete-orphan")


class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    rule_id = Column(String(50), nullable=False)
    rule_name = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    wcag_criteria = Column(String(50))
    description = Column(Text, nullable=False)
    element_html = Column(Text)
    page_url = Column(String(500))
    fix_suggestion = Column(Text)
    selector = Column(String(500))
    
    scan = relationship("Scan", back_populates="violations")
