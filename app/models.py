import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


def generate_uuid():
    return uuid.uuid4().hex[:12]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    plan = db.Column(db.String(20), nullable=False, default="free")
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    spaces = db.relationship("Space", backref="owner", lazy="dynamic", cascade="all, delete-orphan")
    subscription = db.relationship("Subscription", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_plan_limits(self):
        from flask import current_app
        return current_app.config["PLAN_LIMITS"].get(self.plan, current_app.config["PLAN_LIMITS"]["free"])

    def can_create_space(self):
        limits = self.get_plan_limits()
        max_spaces = limits["spaces"]
        if max_spaces == -1:
            return True
        return self.spaces.count() < max_spaces

    def has_branding(self):
        return self.get_plan_limits()["branding"]


class Space(db.Model):
    __tablename__ = "spaces"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False, default=generate_uuid, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, index=True)
    logo_url = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    header_text = db.Column(db.String(200), default="Share your experience with us!")
    thank_you_text = db.Column(db.String(200), default="Thank you for your testimonial!")
    questions = db.Column(db.Text, nullable=True)  # JSON list of custom questions
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    testimonials = db.relationship("Testimonial", backref="space", lazy="dynamic", cascade="all, delete-orphan")
    widgets = db.relationship("Widget", backref="space", lazy="dynamic", cascade="all, delete-orphan")

    def approved_testimonials(self):
        return self.testimonials.filter_by(status="approved")

    def pending_testimonials(self):
        return self.testimonials.filter_by(status="pending")

    def testimonial_count(self):
        return self.testimonials.count()

    def can_accept_testimonial(self):
        limits = self.owner.get_plan_limits()
        max_per_space = limits["testimonials_per_space"]
        if max_per_space == -1:
            return True
        return self.testimonial_count() < max_per_space


class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False, default=generate_uuid)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(255), nullable=True)
    author_title = db.Column(db.String(100), nullable=True)  # e.g. "CEO at Acme"
    author_avatar_url = db.Column(db.String(500), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)  # pending, approved, rejected
    is_starred = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500), nullable=True)  # comma-separated tags
    source = db.Column(db.String(50), default="form")  # form, import, manual
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def get_tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Widget(db.Model):
    __tablename__ = "widgets"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), unique=True, nullable=False, default=generate_uuid)
    space_id = db.Column(db.Integer, db.ForeignKey("spaces.id"), nullable=False)
    widget_type = db.Column(db.String(30), nullable=False, default="wall")  # wall, carousel, badge
    theme = db.Column(db.String(20), default="light")  # light, dark
    max_display = db.Column(db.Integer, default=10)
    show_rating = db.Column(db.Boolean, default=True)
    show_date = db.Column(db.Boolean, default=False)
    show_avatar = db.Column(db.Boolean, default=True)
    custom_css = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    stripe_price_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="active")  # active, canceled, past_due
    current_period_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
