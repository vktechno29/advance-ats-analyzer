from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate

router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"]
)
@router.get("/plans")
def get_plans():

    return [
        {
            "name": "Free",
            "price": 0,
            "resume_limit": 1
        },
        {
            "name": "Pro",
            "price": 199,
            "resume_limit": 5
        },
        {
            "name": "Premium",
            "price": 299,
            "resume_limit": 10
        }
    ]
@router.post("/create-order")
def create_order(
    data: SubscriptionCreate,
    db: Session = Depends(get_db)
):

    subscription = Subscription(
        user_id=data.user_id,
        plan_name=data.plan_name,
        amount=data.amount,
        payment_status="Pending"
    )

    db.add(subscription)

    db.commit()

    db.refresh(subscription)

    return {
        "message": "Order created",
        "subscription_id": subscription.id
    }
@router.post("/verify-payment/{subscription_id}")
def verify_payment(
    subscription_id: int,
    db: Session = Depends(get_db)
):

    subscription = db.query(
        Subscription
    ).filter(
        Subscription.id == subscription_id
    ).first()

    if not subscription:
        return {
            "error": "Subscription not found"
        }

    subscription.payment_status = "Paid"

    db.commit()

    return {
        "message": "Payment verified"
    }
@router.get("/status/{user_id}")
def subscription_status(
    user_id: int,
    db: Session = Depends(get_db)
):

    subscription = db.query(
        Subscription
    ).filter(
        Subscription.user_id == user_id
    ).first()

    if not subscription:
        return {
            "message": "No active subscription"
        }

    return {
        "plan": subscription.plan_name,
        "status": subscription.payment_status
    }