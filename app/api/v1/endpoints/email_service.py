import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.api.v1.endpoints.config import settings


def send_otp_email(receiver_email: str, otp: str):

    subject = "Your OTP Verification Code"

    body = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 10 minutes.

If you did not request this OTP, please ignore this email.

Thanks,
SmartPrep AI Team
"""

    message = MIMEMultipart()
    message["From"] = settings.EMAIL_USERNAME
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(
        settings.EMAIL_HOST,
        587,
        timeout=30
    )

    server.starttls()

    server.login(
        settings.EMAIL_USERNAME,
        settings.EMAIL_PASSWORD
    )

    server.send_message(message)

    server.quit()