from pydantic import BaseModel

class ResumeCreate(BaseModel):
    original_resume: str
    ats_score: float
    missing_skills: str
    job_description: str