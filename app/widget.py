from flask import Blueprint, render_template, jsonify, request, make_response

from app.models import Space, Widget, Testimonial

widget_bp = Blueprint("widget", __name__, template_folder="templates/widgets")


@widget_bp.route("/<widget_uid>")
def render_widget(widget_uid):
    widget = Widget.query.filter_by(uid=widget_uid).first_or_404()
    space = widget.space

    testimonials = (
        space.approved_testimonials()
        .order_by(Testimonial.is_starred.desc(), Testimonial.created_at.desc())
        .limit(widget.max_display)
        .all()
    )

    show_branding = space.owner.has_branding()

    template_map = {
        "wall": "widgets/wall.html",
        "carousel": "widgets/carousel.html",
        "badge": "widgets/badge.html",
    }

    template = template_map.get(widget.widget_type, "widgets/wall.html")

    return render_template(
        template,
        widget=widget,
        space=space,
        testimonials=testimonials,
        show_branding=show_branding,
    )


@widget_bp.route("/<widget_uid>/data")
def widget_data(widget_uid):
    widget = Widget.query.filter_by(uid=widget_uid).first_or_404()
    space = widget.space

    testimonials = (
        space.approved_testimonials()
        .order_by(Testimonial.is_starred.desc(), Testimonial.created_at.desc())
        .limit(widget.max_display)
        .all()
    )

    data = {
        "space": {"name": space.name, "logo_url": space.logo_url},
        "widget": {
            "type": widget.widget_type,
            "theme": widget.theme,
            "show_rating": widget.show_rating,
            "show_date": widget.show_date,
            "show_avatar": widget.show_avatar,
        },
        "testimonials": [
            {
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
        "branding": space.owner.has_branding(),
    }

    response = make_response(jsonify(data))
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@widget_bp.route("/embed.js")
def embed_js():
    response = make_response(render_template("widgets/embed.js"))
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
