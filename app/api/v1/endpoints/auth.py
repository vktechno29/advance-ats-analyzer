from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone

import random

from app.database.db import SessionLocal
from app.models.user import User
from app.models.email_otp import EmailOTP

from app.schemas.user import SignupSchema, LoginSchema
from app.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.api.v1.endpoints.email_service import send_otp_email

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
@router.post("/send-otp")
def send_signup_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    otp = str(random.randint(100000, 999999))

    db.query(EmailOTP).filter(
        EmailOTP.email == data.email
    ).delete()

    otp_record = EmailOTP(
        email=data.email,
        otp=otp,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )

    db.add(otp_record)
    db.commit()

    send_otp_email(
        data.email,
        otp
    )

    return {
        "success": True,
        "message": "OTP sent successfully."
    }
@router.post("/verify-otp")
def verify_signup_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    otp_record = (
        db.query(EmailOTP)
        .filter(
            EmailOTP.email == data.email,
            EmailOTP.otp == data.otp
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP."
        )

    if otp_record.expires_at < datetime.now(timezone.utc):
        db.delete(otp_record)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="OTP has expired."
        )

    otp_record.is_verified = True
    db.commit()

    return {
        "success": True,
        "message": "OTP verified successfully."
    }

@router.post("/signup")
def signup(
    user: SignupSchema,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == user.email,
        EmailOTP.is_verified == True
    ).first()

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Please verify your email first."
        )

    if otp_record.expires_at < datetime.now(timezone.utc):
        db.delete(otp_record)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="OTP has expired."
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.delete(otp_record)
    db.commit()

    return {
        "success": True,
        "message": "Signup successful",
        "user_id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }
@router.post("/login")
def login(
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    otp = str(random.randint(100000, 999999))

    db.query(EmailOTP).filter(
        EmailOTP.email == data.email
    ).delete()

    otp_record = EmailOTP(
        user_id=user.id,
        email=user.email,
        otp=otp,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )

    db.add(otp_record)
    db.commit()

    send_otp_email(
        user.email,
        otp
    )

    return {
        "success": True,
        "message": "OTP sent to your email."
    }
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    otp_record = (
        db.query(EmailOTP)
        .filter(
            EmailOTP.email == data.email,
            EmailOTP.otp == data.otp
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP."
        )

    if otp_record.expires_at < datetime.now(timezone.utc):
        db.delete(otp_record)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="OTP has expired."
        )

    user.password = hash_password(
        data.new_password
    )

    db.delete(otp_record)

    db.commit()

    return {
        "success": True,
        "message": "Password reset successfully."
    }