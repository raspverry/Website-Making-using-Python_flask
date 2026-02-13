from flask import Blueprint, jsonify, request
from app.models import Space, Testimonial

api_bp = Blueprint("api", __name__)


@api_bp.route("/spaces/<space_uid>/testimonials")
def get_testimonials(space_uid):
    space = Space.query.filter_by(uid=space_uid).first()
    if not space:
        return jsonify({"error": "Space not found"}), 404

    testimonials = (
        space.approved_testimonials()
        .order_by(Testimonial.is_starred.desc(), Testimonial.created_at.desc())
        .all()
    )

    return jsonify({
        "space": {"name": space.name, "logo_url": space.logo_url},
        "testimonials": [
            {
                "id": t.uid,
                "author_name": t.author_name,
                "author_title": t.author_title,
                "company": t.company,
                "rating": t.rating,
                "text": t.text,
                "avatar_url": t.author_avatar_url,
                "is_starred": t.is_starred,
                "created_at": t.created_at.isoformat(),
            }
            for t in testimonials
        ],
        "count": len(testimonials),
    })
