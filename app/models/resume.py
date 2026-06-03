from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime
from datetime import datetime
from app.database.db import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    original_resume = Column(Text, nullable=False)

    rewritten_resume = Column(Text)

    ats_score = Column(Float)

    missing_skills = Column(Text)

    job_description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)