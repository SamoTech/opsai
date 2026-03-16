import stripe
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

PLANS = {
    "free": {"runs_limit": 50, "projects_limit": 3, "price_id": None},
    "pro": {"runs_limit": 1000, "projects_limit": 999, "price_id": settings.STRIPE_PRO_PRICE_ID},
    "team": {"runs_limit": 10000, "projects_limit": 999, "price_id": settings.STRIPE_TEAM_PRICE_ID},
}


class StripeService:
    async def create_checkout_session(
        self, user_id: str, plan: str, success_url: str, cancel_url: str
    ) -> Optional[str]:
        if plan not in PLANS or not PLANS[plan]["price_id"]:
            return None
        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": PLANS[plan]["price_id"], "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"user_id": user_id, "plan": plan},
                allow_promotion_codes=True,
            )
            return session.url
        except stripe.StripeError as e:
            # Fix 17: stripe.error.StripeError was removed in stripe-python v5.
            # The exception is now stripe.StripeError (top-level).
            logger.error(f"Stripe checkout error: {e}")
            return None

    async def create_billing_portal(
        self, customer_id: str, return_url: str
    ) -> Optional[str]:
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.StripeError as e:
            logger.error(f"Stripe portal error: {e}")
            return None

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.StripeError as e:
            logger.error(f"Stripe webhook verification failed: {e}")
            raise


stripe_service = StripeService()
