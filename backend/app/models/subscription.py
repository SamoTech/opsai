import datetime as dt
import enum
import uuid

from sqlalchemy import Column, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class PlanTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String(100), unique=True)
    stripe_subscription_id = Column(String(100), unique=True)
    plan = Column(SAEnum(PlanTier), default=PlanTier.FREE)
    status = Column(SAEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    # Fix 12: was String(10) — must be Integer for arithmetic and atomic DB increments
    runs_used_this_month = Column(Integer, nullable=False, default=0, server_default="0")
    billing_period_start = Column(Date, nullable=True, default=dt.date.today)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
