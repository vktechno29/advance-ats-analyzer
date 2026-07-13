from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.subscription import Subscription

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


@router.get("/history/{user_id}")
def payment_history(
    user_id: int,
    db: Session = Depends(get_db)
):

    payments = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id
        )
        .order_by(
            Subscription.created_at.desc()
        )
        .all()
    )

    if not payments:
        raise HTTPException(
            status_code=404,
            detail="No payment history found."
        )

    return {
        "success": True,
        "message": "Payment history fetched successfully.",
        "count": len(payments),
        "data": [
            {
                "id": payment.id,
                "invoice_number": payment.invoice_number,
                "plan_name": payment.plan_name,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "payment_id": payment.payment_id,
                "order_id": payment.order_id,
                "payment_status": payment.payment_status,
                "is_active": payment.is_active,
                "start_date": payment.start_date,
                "end_date": payment.end_date,
                "created_at": payment.created_at,
                "download_bill": f"/payment/download-bill/{payment.id}"
            }
            for payment in payments
        ]
    }
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
import os


@router.get("/download-bill/{subscription_id}")
def download_bill(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id)
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found."
        )

    filename = f"invoice_{subscription.invoice_number}.pdf"

    c = canvas.Canvas(filename)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "ATS Resume Analyzer")

    c.setFont("Helvetica", 12)

    y = 760

    c.drawString(50, y, f"Invoice No: {subscription.invoice_number}")
    y -= 25

    c.drawString(50, y, f"User ID: {subscription.user_id}")
    y -= 25

    c.drawString(50, y, f"Plan: {subscription.plan_name}")
    y -= 25

    c.drawString(50, y, f"Amount: {subscription.amount} {subscription.currency}")
    y -= 25

    c.drawString(50, y, f"Payment Method: {subscription.payment_method}")
    y -= 25

    c.drawString(50, y, f"Payment ID: {subscription.payment_id}")
    y -= 25

    c.drawString(50, y, f"Order ID: {subscription.order_id}")
    y -= 25

    c.drawString(50, y, f"Status: {subscription.payment_status}")
    y -= 25

    c.drawString(50, y, f"Start Date: {subscription.start_date}")
    y -= 25

    c.drawString(50, y, f"End Date: {subscription.end_date}")
    y -= 25

    c.drawString(50, y, "Thank you for choosing ATS Resume Analyzer.")

    c.save()

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )