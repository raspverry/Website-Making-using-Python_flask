import json
import logging
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.dependencies import get_authenticated_user
from backend.models import User, Subscription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout")
def create_checkout_session(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Create a Stripe Checkout session for a plan upgrade."""
    if plan not in settings.STRIPE_PRICE_IDS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")

    price_id = settings.STRIPE_PRICE_IDS[plan]

    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/dashboard?checkout=success",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?checkout=canceled",
        metadata={"user_id": str(current_user.id), "plan": plan},
    )

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/portal")
def create_portal_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Create a Stripe Customer Portal session for subscription management."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/dashboard",
    )

    return {"portal_url": session.url}


@router.get("/subscription")
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Get current user's subscription details."""
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not sub:
        return {"plan": "free", "status": "active", "current_period_end": None}
    return {
        "plan": sub.plan,
        "status": sub.status,
        "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET not set — rejecting webhook. Set it in production!")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError) as e:
        logger.warning("Webhook signature verification failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(data, db)
    elif event_type == "invoice.payment_failed":
        _handle_payment_failed(data, db)

    return {"status": "ok"}


def _handle_checkout_completed(session_data: dict, db: Session):
    user_id = session_data.get("metadata", {}).get("user_id")
    plan = session_data.get("metadata", {}).get("plan")
    subscription_id = session_data.get("subscription")

    if not user_id or not plan:
        logger.warning("Checkout session missing metadata")
        return

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        logger.warning("User %s not found for checkout", user_id)
        return

    # Update user plan
    user.plan = plan

    # Create or update subscription record
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub:
        sub.stripe_subscription_id = subscription_id
        sub.plan = plan
        sub.status = "active"
    else:
        sub = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription_id,
            plan=plan,
            status="active",
        )
        db.add(sub)

    db.commit()
    logger.info("User %s upgraded to %s plan", user_id, plan)


def _handle_subscription_updated(sub_data: dict, db: Session):
    stripe_sub_id = sub_data.get("id")
    status = sub_data.get("status")

    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if not sub:
        return

    sub.status = status
    if sub_data.get("current_period_end"):
        sub.current_period_end = datetime.fromtimestamp(sub_data["current_period_end"], tz=timezone.utc)

    # Map Stripe plan back if changed
    items = sub_data.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")
        for plan_name, pid in settings.STRIPE_PRICE_IDS.items():
            if pid == price_id:
                sub.plan = plan_name
                sub.owner.plan = plan_name  # using backref
                break

    db.commit()


def _handle_subscription_deleted(sub_data: dict, db: Session):
    stripe_sub_id = sub_data.get("id")
    sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
    if not sub:
        return

    sub.status = "canceled"
    sub.owner.plan = "free"
    db.commit()
    logger.info("Subscription %s canceled, user reverted to free", stripe_sub_id)


def _handle_payment_failed(invoice_data: dict, db: Session):
    customer_id = invoice_data.get("customer")
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        return

    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub:
        sub.status = "past_due"
        db.commit()

    # Notify customer about payment failure
    from backend.services.email_service import send_payment_failed_email
    send_payment_failed_email(user.email, user.name)
    logger.warning("Payment failed for user %s, notification sent", user.id)
