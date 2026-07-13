from fastapi import FastAPI
from app.api.v1.endpoints.resume import router as resume_router
from app.api.v1.endpoints.auth import router as auth_router
from app.models.user import User
from app.models.resume import Resume
from app.database.db import Base,engine
from app.api.v1.endpoints import user
from app.api.v1.endpoints.template import router as template_router
from app.api.v1.endpoints.subscription import router as subscription_router
from app.models.subscription import Subscription
from app.api.v1.endpoints import dashboard
from app.api.v1.endpoints import usage
from app.api.v1.endpoints import admin
from fastapi.staticfiles import StaticFiles
from app.models.contact import Contact
from app.api.v1.endpoints.contact import router as contact_router
from app.models.activity import Activity
from app.api.v1.endpoints.payment import router as payment_router
app = FastAPI(title="Advanced ATS Analyzer")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
Base.metadata.create_all(bind=engine)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume Analyzer"]
)
app.include_router(user.router, prefix="/user", tags=["User"])
@app.get("/")
def home():
    return {"message": "Advance ATS Analyzer"}
app.include_router(template_router, prefix="/template", tags=["Template"])
app.include_router(subscription_router)
app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)
app.include_router(usage.router, prefix="/usage", tags=["Usage"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(contact_router, prefix="/contact", tags=["Contact"])
app.include_router(payment_router, prefix="/payment", tags=["Payment"])