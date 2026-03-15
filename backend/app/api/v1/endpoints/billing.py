from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from app.services.stripe_service import stripe_service, PLANS
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: str
    user_id: str


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {"id": "free", "name": "Free", "price": 0, "runs_limit": 50, "projects_limit": 3},
            {"id": "pro", "name": "Pro", "price": 29, "runs_limit": 1000, "projects_limit": -1},
            {"id": "team", "name": "Team", "price": 99, "runs_limit": 10000, "projects_limit": -1},
        ]
    }


@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest, request: Request):
    origin = request.headers.get("origin", settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:3000")
    url = await stripe_service.create_checkout_session(
        user_id=payload.user_id,
        plan=payload.plan,
        success_url=f"{origin}/billing/success?plan={payload.plan}",
        cancel_url=f"{origin}/billing",
    )
    if not url:
        raise HTTPException(status_code=400, detail="Could not create checkout session.")
    return {"checkout_url": url}


@router.post("/portal")
async def billing_portal(customer_id: str, request: Request):
    origin = request.headers.get("origin", settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:3000")
    url = await stripe_service.create_billing_portal(customer_id, return_url=f"{origin}/billing")
    if not url:
        raise HTTPException(status_code=400, detail="Could not open billing portal.")
    return {"portal_url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe_service.construct_webhook_event(payload, stripe_signature or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        plan = data.get("metadata", {}).get("plan")
        logger.info(f"Checkout completed: user={user_id} plan={plan}")
        # TODO: update user subscription in DB

    elif event_type == "customer.subscription.deleted":
        logger.info(f"Subscription cancelled: {data.get('id')}")
        # TODO: downgrade to free

    return {"received": True}
