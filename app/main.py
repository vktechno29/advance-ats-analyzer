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

app = FastAPI(title="Advanced ATS Analyzer")
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