import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


def _uid():
    return uuid.uuid4().hex[:12]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    plan = db.Column(db.String(20), nullable=False, default="free")
    stripe_customer_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    sites = db.relationship("Site", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    subscription = db.relationship("Subscription", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_plan_limits(self):
        from flask import current_app
        return current_app.config["PLAN_LIMITS"].get(self.plan, current_app.config["PLAN_LIMITS"]["free"])

    def can_add_site(self):
        limits = self.get_plan_limits()
        max_sites = limits["sites"]
        if max_sites == -1:
            return True
        return self.sites.count() < max_sites

    def has_ai_fixes(self):
        return self.get_plan_limits()["ai_fixes"]


class Site(db.Model):
    __tablename__ = "sites"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False, default=_uid, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    compliance_score = db.Column(db.Integer)  # 0-100
    last_scan_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    scans = db.relationship("Scan", backref="site", lazy="dynamic", cascade="all, delete-orphan")

    def latest_scan(self):
        return self.scans.order_by(Scan.created_at.desc()).first()


class Scan(db.Model):
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False, default=_uid)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending, running, completed, failed
    score = db.Column(db.Integer)  # 0-100
    pages_scanned = db.Column(db.Integer, default=0)
    total_violations = db.Column(db.Integer, default=0)
    critical_count = db.Column(db.Integer, default=0)
    serious_count = db.Column(db.Integer, default=0)
    moderate_count = db.Column(db.Integer, default=0)
    minor_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)

    violations = db.relationship("Violation", backref="scan", lazy="dynamic", cascade="all, delete-orphan")


class Violation(db.Model):
    __tablename__ = "violations"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)
    rule_id = db.Column(db.String(50), nullable=False)  # e.g. "img-alt", "label", "color-contrast"
    rule_name = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # critical, serious, moderate, minor
    wcag_criteria = db.Column(db.String(50))  # e.g. "1.1.1", "1.4.3"
    description = db.Column(db.Text, nullable=False)
    element_html = db.Column(db.Text)  # the offending HTML snippet
    page_url = db.Column(db.String(500))
    fix_suggestion = db.Column(db.Text)  # AI-generated fix
    selector = db.Column(db.String(500))  # CSS selector to the element


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    stripe_subscription_id = db.Column(db.String(255))
    stripe_price_id = db.Column(db.String(255))
    status = db.Column(db.String(30), nullable=False, default="active")
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
