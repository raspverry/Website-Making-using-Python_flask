import stripe
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import Subscription

billing_bp = Blueprint("billing", __name__, template_folder="templates/dashboard")


def get_stripe():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    return stripe


@billing_bp.route("/")
@login_required
def billing_portal():
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
        flash("Invalid plan selected.", "error")
        return redirect(url_for("billing.billing_portal"))

    # Create or retrieve Stripe customer
    if not current_user.stripe_customer_id:
        customer = s.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id},
        )
        current_user.stripe_customer_id = customer.id
        db.session.commit()

    checkout_session = s.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{current_app.config['APP_URL']}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{current_app.config['APP_URL']}/billing/",
        metadata={"user_id": current_user.id, "plan": plan},
    )

    return redirect(checkout_session.url)


@billing_bp.route("/success")
@login_required
def checkout_success():
    flash("Payment successful! Your plan has been upgraded.", "success")
    return redirect(url_for("dashboard.index"))


@billing_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    s = get_stripe()
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    if not webhook_secret:
        return jsonify({"error": "Webhook secret not configured"}), 500

    try:
        event = s.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except s.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_completed(session)
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        handle_subscription_updated(subscription)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        handle_subscription_deleted(subscription)

    return jsonify({"status": "ok"}), 200


def handle_checkout_completed(session):
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


def handle_subscription_updated(subscription_data):
    sub = Subscription.query.filter_by(
        stripe_subscription_id=subscription_data["id"]
    ).first()
    if sub:
        sub.status = subscription_data["status"]
        db.session.commit()


def handle_subscription_deleted(subscription_data):
    sub = Subscription.query.filter_by(
        stripe_subscription_id=subscription_data["id"]
    ).first()
    if sub:
        sub.status = "canceled"
        sub.user.plan = "free"
        db.session.commit()
