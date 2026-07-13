from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    plan_name = Column(String(100), nullable=False)

    amount = Column(Integer, nullable=False)

    payment_id = Column(String(255), nullable=True)

    order_id = Column(String(255), nullable=True)

    invoice_number = Column(String(100), nullable=True)

    payment_method = Column(String(50), nullable=True)

    currency = Column(String(10), default="INR")

    payment_status = Column(
        String(30),
        default="Pending"
    )

    is_active = Column(
        Boolean,
        default=False
    )

    start_date = Column(DateTime)

    end_date = Column(DateTime)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        backref="subscriptions"
    )