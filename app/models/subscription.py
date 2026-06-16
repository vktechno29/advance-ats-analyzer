from sqlalchemy import Column, Integer, String, Boolean

from app.database.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    plan_name = Column(String)

    amount = Column(Integer)

    payment_id = Column(String, nullable=True)

    order_id = Column(String, nullable=True)

    is_active = Column(Boolean, default=False)