from fastapi import FastAPI
from app.api.v1.endpoints.resume import router as resume_router
from app.api.v1.endpoints.auth import router as auth_router

app = FastAPI(title="Advanced ATS Analyzer")

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
@app.get("/")
def home():
    return {"message": "Advance ATS Analyzer"}