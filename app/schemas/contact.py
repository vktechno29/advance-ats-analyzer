from pydantic import BaseModel, EmailStr

class ContactCreate(BaseModel):
    full_name: str
    email: EmailStr
    subject: str
    message: str