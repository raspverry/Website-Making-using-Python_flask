from flask import Blueprint, render_template, redirect, url_for, flash, request

from app import db
from app.models import Space, Testimonial

public_bp = Blueprint("public", __name__, template_folder="templates/public")


@public_bp.route("/<slug>", methods=["GET", "POST"])
def collect(slug):
    space = Space.query.filter_by(slug=slug).first_or_404()

    if request.method == "POST":
        if not space.can_accept_testimonial():
            flash("This space has reached its testimonial limit.", "error")
            return render_template("public/collect.html", space=space)

        author_name = request.form.get("author_name", "").strip()
        author_email = request.form.get("author_email", "").strip()
        author_title = request.form.get("author_title", "").strip()
        company = request.form.get("company", "").strip()
        rating = request.form.get("rating", type=int)
        text = request.form.get("text", "").strip()

        errors = []
        if not author_name or len(author_name) < 2:
            errors.append("Please enter your name.")
        if not text or len(text) < 10:
            errors.append("Testimonial must be at least 10 characters.")
        if rating and (rating < 1 or rating > 5):
            errors.append("Rating must be between 1 and 5.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "public/collect.html",
                space=space,
                author_name=author_name,
                author_email=author_email,
                author_title=author_title,
                company=company,
                text=text,
            )

        testimonial = Testimonial(
            space_id=space.id,
            author_name=author_name,
            author_email=author_email or None,
            author_title=author_title or None,
            company=company or None,
            rating=rating,
            text=text,
            status="pending",
            source="form",
        )
        db.session.add(testimonial)
        db.session.commit()

        return render_template("public/thankyou.html", space=space)

    return render_template("public/collect.html", space=space)
