from sqlalchemy import Column, Integer, String, Text
from app.database.db import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String)
    phone = Column(String)
    linkedin = Column(String)

    original_resume = Column(Text)

    ats_score = Column(Integer)
    job_description = Column(Text)

    missing_skills = Column(Text)

    rewritten_resume = Column(Text)

    pdf_url = Column(String)
    template_id = Column(Integer,default=1)