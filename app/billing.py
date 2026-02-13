import stripe
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user

from app import db, csrf
from app.models import Subscription

billing_bp = Blueprint("billing", __name__)


def get_stripe():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    return stripe


@billing_bp.route("/")
@login_required
def portal():
    return render_template("dashboard/billing.html")


@billing_bp.route("/checkout/<plan>", methods=["POST"])
@login_required
def create_checkout(plan):
    s = get_stripe()

    price_map = {
        "starter": current_app.config["STRIPE_PRICE_STARTER"],
        "pro": current_app.config["STRIPE_PRICE_PRO"],
        "agency": current_app.config["STRIPE_PRICE_AGENCY"],
    }

    price_id = price_map.get(plan)
    if not price_id:
        flash("Invalid plan.", "error")
        return redirect(url_for("billing.portal"))

    if not current_user.stripe_customer_id:
        customer = s.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id},
        )
        current_user.stripe_customer_id = customer.id
        db.session.commit()

    session = s.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{current_app.config['APP_URL']}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{current_app.config['APP_URL']}/billing/",
        metadata={"user_id": current_user.id, "plan": plan},
    )

    return redirect(session.url)


@billing_bp.route("/success")
@login_required
def success():
    flash("Payment successful! Your plan has been upgraded.", "success")
    return redirect(url_for("dashboard.index"))


@billing_bp.route("/webhook", methods=["POST"])
def webhook():
    s = get_stripe()
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature")
    secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    if not secret:
        return jsonify({"error": "Not configured"}), 500

    try:
        event = s.Webhook.construct_event(payload, sig, secret)
    except (ValueError, s.error.SignatureVerificationError):
        return jsonify({"error": "Invalid"}), 400

    if event["type"] == "checkout.session.completed":
        _handle_checkout(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        _handle_cancel(event["data"]["object"])

    return jsonify({"ok": True}), 200


# Exempt webhook from CSRF
csrf.exempt(billing_bp)


def _handle_checkout(session):
    from app.models import User

    user_id = session.get("metadata", {}).get("user_id")
    plan = session.get("metadata", {}).get("plan", "starter")
    if not user_id:
        return

    user = db.session.get(User, int(user_id))
    if not user:
        return

    user.plan = plan
    sub = Subscription.query.filter_by(user_id=user.id).first()
    if not sub:
        sub = Subscription(user_id=user.id)
        db.session.add(sub)
    sub.stripe_subscription_id = session.get("subscription")
    sub.status = "active"
    db.session.commit()


def _handle_cancel(sub_data):
    sub = Subscription.query.filter_by(stripe_subscription_id=sub_data["id"]).first()
    if sub:
        sub.status = "canceled"
        sub.user.plan = "free"
        db.session.commit()
