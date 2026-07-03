from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.subscription import Subscription
from app.models.activity import Activity
from sqlalchemy import func
from datetime import datetime, timezone


router = APIRouter()

@router.get("/dashboard")
def get_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return {
            "error": "User not found"
        }

    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.is_active == True,
        Subscription.payment_status == "Paid"
    ).first()

    resume_count = db.query(Resume).filter(
        Resume.user_id == user_id
    ).count()
    average_ats = (
                      db.query(func.avg(Resume.ats_score))
                      .filter(
                          Resume.user_id == user_id,
                          Resume.ats_score != None
                      )
                      .scalar()
                  ) or 0

    ats_scans = (
        db.query(Resume)
        .filter(
            Resume.user_id == user_id,
            Resume.ats_score != None
        )
        .count()
    )

    recent_activity = (
        db.query(Activity)
        .filter(Activity.user_id == user_id)
        .order_by(Activity.created_at.desc())
        .limit(5)
        .all()
    )

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.id.desc())
        .all()
    )

    plan_name = "Free"
    resume_limit = 1

    if subscription:

        plan_name = subscription.plan_name

        if subscription.plan_name == "Pro":
            resume_limit = 5

        elif subscription.plan_name == "Premium":
            resume_limit = 10

    return {
        "success": True,
        "message": "Dashboard fetched successfully",
        "data": {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "plan": plan_name,
                "active_subscription": subscription is not None,
                "resume_limit": resume_limit,
                "resumes_uploaded": resume_count,
                "remaining": max(0, resume_limit - resume_count)
            },

            "statistics": {
                "totalResumes": resume_count,
                "atsScans": ats_scans,
                "averageAtsScore": round(average_ats, 2),
                "downloads": 0
            },

            "recentActivity": [
                {
                    "id": activity.id,
                    "type": activity.type,
                    "title": activity.title,
                    "time": "Recently",
                    "createdAt": activity.created_at
                }
                for activity in recent_activity
            ],

            "resumes": [
                {
                    "id": resume.id,
                    "title": resume.name,
                    "template": resume.template_id,
                    "thumbnail": None,
                    "pdf_url": resume.pdf_url,
                    "atsScore": resume.ats_score,
                    "status": "saved",
                    "lastUpdated": "Recently",
                    "createdAt": resume.created_at,
                    "updatedAt": resume.updated_at,
                    "actions": {
                        "edit": f"/resume/{resume.id}/edit",
                        "preview": f"/resume/{resume.id}/preview",
                        "downloadPdf": f"/resume/{resume.id}/download"
                    }
                }
                for resume in resumes
            ]
        }
    }