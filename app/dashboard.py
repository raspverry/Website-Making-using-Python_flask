import re

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Space, Testimonial, Widget

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates/dashboard")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80]


@dashboard_bp.route("/")
@login_required
def index():
    spaces = current_user.spaces.order_by(Space.created_at.desc()).all()
    return render_template("dashboard/index.html", spaces=spaces)


@dashboard_bp.route("/spaces/new", methods=["GET", "POST"])
@login_required
def create_space():
    if not current_user.can_create_space():
        flash("You've reached the maximum number of spaces for your plan. Upgrade to create more.", "error")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        website_url = request.form.get("website_url", "").strip()
        header_text = request.form.get("header_text", "").strip()

        if not name or len(name) < 2:
            flash("Space name must be at least 2 characters.", "error")
            return render_template("dashboard/create_space.html", name=name, website_url=website_url)

        slug = slugify(name)
        # Ensure unique slug
        existing = Space.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{Space.query.count() + 1}"

        space = Space(
            name=name,
            slug=slug,
            user_id=current_user.id,
            website_url=website_url or None,
            header_text=header_text or "Share your experience with us!",
        )
        db.session.add(space)

        # Create default Wall of Love widget
        widget = Widget(space=space, widget_type="wall", theme="light")
        db.session.add(widget)

        db.session.commit()

        flash(f'Space "{name}" created! Share the collection link to start gathering testimonials.', "success")
        return redirect(url_for("dashboard.space_detail", space_uid=space.uid))

    return render_template("dashboard/create_space.html")


@dashboard_bp.route("/spaces/<space_uid>")
@login_required
def space_detail(space_uid):
    space = Space.query.filter_by(uid=space_uid, user_id=current_user.id).first_or_404()
    status_filter = request.args.get("status", "all")

    if status_filter == "pending":
        testimonials = space.pending_testimonials().order_by(Testimonial.created_at.desc()).all()
    elif status_filter == "approved":
        testimonials = space.approved_testimonials().order_by(Testimonial.created_at.desc()).all()
    else:
        testimonials = space.testimonials.order_by(Testimonial.created_at.desc()).all()

    widgets = space.widgets.all()
    collect_url = f"{current_app.config['APP_URL']}/t/{space.slug}"

    return render_template(
        "dashboard/space_detail.html",
        space=space,
        testimonials=testimonials,
        widgets=widgets,
        collect_url=collect_url,
        status_filter=status_filter,
    )


@dashboard_bp.route("/spaces/<space_uid>/edit", methods=["GET", "POST"])
@login_required
def edit_space(space_uid):
    space = Space.query.filter_by(uid=space_uid, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        website_url = request.form.get("website_url", "").strip()
        header_text = request.form.get("header_text", "").strip()
        thank_you_text = request.form.get("thank_you_text", "").strip()

        if not name or len(name) < 2:
            flash("Space name must be at least 2 characters.", "error")
            return render_template("dashboard/edit_space.html", space=space)

        space.name = name
        space.website_url = website_url or None
        space.header_text = header_text or space.header_text
        space.thank_you_text = thank_you_text or space.thank_you_text
        db.session.commit()

        flash("Space updated.", "success")
        return redirect(url_for("dashboard.space_detail", space_uid=space.uid))

    return render_template("dashboard/edit_space.html", space=space)


@dashboard_bp.route("/spaces/<space_uid>/delete", methods=["POST"])
@login_required
def delete_space(space_uid):
    space = Space.query.filter_by(uid=space_uid, user_id=current_user.id).first_or_404()
    db.session.delete(space)
    db.session.commit()
    flash(f'Space "{space.name}" deleted.', "info")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/testimonials/<testimonial_uid>/approve", methods=["POST"])
@login_required
def approve_testimonial(testimonial_uid):
    testimonial = Testimonial.query.filter_by(uid=testimonial_uid).first_or_404()
    space = Space.query.filter_by(id=testimonial.space_id, user_id=current_user.id).first_or_404()
    testimonial.status = "approved"
    db.session.commit()
    flash("Testimonial approved.", "success")
    return redirect(url_for("dashboard.space_detail", space_uid=space.uid))


@dashboard_bp.route("/testimonials/<testimonial_uid>/reject", methods=["POST"])
@login_required
def reject_testimonial(testimonial_uid):
    testimonial = Testimonial.query.filter_by(uid=testimonial_uid).first_or_404()
    space = Space.query.filter_by(id=testimonial.space_id, user_id=current_user.id).first_or_404()
    testimonial.status = "rejected"
    db.session.commit()
    flash("Testimonial rejected.", "info")
    return redirect(url_for("dashboard.space_detail", space_uid=space.uid))


@dashboard_bp.route("/testimonials/<testimonial_uid>/star", methods=["POST"])
@login_required
def toggle_star(testimonial_uid):
    testimonial = Testimonial.query.filter_by(uid=testimonial_uid).first_or_404()
    Space.query.filter_by(id=testimonial.space_id, user_id=current_user.id).first_or_404()
    testimonial.is_starred = not testimonial.is_starred
    db.session.commit()
    return redirect(request.referrer or url_for("dashboard.index"))


@dashboard_bp.route("/testimonials/<testimonial_uid>/delete", methods=["POST"])
@login_required
def delete_testimonial(testimonial_uid):
    testimonial = Testimonial.query.filter_by(uid=testimonial_uid).first_or_404()
    space = Space.query.filter_by(id=testimonial.space_id, user_id=current_user.id).first_or_404()
    db.session.delete(testimonial)
    db.session.commit()
    flash("Testimonial deleted.", "info")
    return redirect(url_for("dashboard.space_detail", space_uid=space.uid))


@dashboard_bp.route("/settings")
@login_required
def settings():
    return render_template("dashboard/settings.html")
