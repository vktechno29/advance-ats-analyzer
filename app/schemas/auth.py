from pydantic import BaseModel, EmailStr

class SendOTPRequest(BaseModel):
    email: EmailStr
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str