from fastapi import APIRouter, UploadFile, File, Form
import pdfplumber
import re
from pydantic import BaseModel
from openai import OpenAI
import os
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.extractor import extract_name,extract_email,extract_phone,extract_linkedin
from app.database.db import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate
from app.core.pdf_generator import generate_resume_pdf
from fastapi.responses import FileResponse
from fastapi import APIRouter,Depends,HTTPException
from app.models.subscription import Subscription
from app.models.activity import Activity

import json

router = APIRouter()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


# =========================
# STOPWORDS
# =========================

STOPWORDS = {
    "and", "or", "the", "is", "in", "at", "of", "a", "an", "to",
    "for", "on", "with", "as", "by", "this", "that", "from",
    "it", "be", "are", "was", "were"
}

# =========================
# SKILLS DATABASE (60+)
# =========================

SKILLS = {

    "data_analyst": [

        "python", "sql", "excel", "power bi", "tableau",
        "pandas", "numpy", "matplotlib", "seaborn",
        "statistics", "data analysis", "data visualization",
        "data cleaning", "eda", "dashboard", "reporting",
        "forecasting", "data mining", "machine learning",
        "scikit-learn", "r", "hypothesis testing",
        "regression", "classification", "time series",
        "big data", "spark", "hadoop", "etl",
        "data warehousing", "data modeling",
        "business intelligence", "dax", "power query",
        "pivot tables", "vlookup", "data wrangling",
        "kpi", "analytics", "predictive modeling",
        "data storytelling", "data pipelines"

    ],

    "data_science": [

        "python", "r", "machine learning", "deep learning",
        "tensorflow", "pytorch", "nlp",
        "computer vision", "statistics", "probability",
        "data mining", "feature engineering",
        "model evaluation", "model deployment",
        "scikit-learn", "xgboost", "lightgbm",
        "clustering", "regression", "classification",
        "time series", "neural networks",
        "data preprocessing", "eda", "big data",
        "spark", "hadoop", "data pipelines"

    ],

    "full_stack": [

        "html", "css", "javascript", "react",
        "node", "express", "mongodb", "mysql",
        "postgresql", "rest api", "graphql",
        "next.js", "typescript", "redux",
        "bootstrap", "tailwind", "firebase",
        "jwt", "authentication", "api integration",
        "frontend", "backend", "web development",
        "git", "github", "docker"

    ]
}

# =========================
# TEXT CLEANING
# =========================

def clean_text(text):

    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)

    words = text.split()

    cleaned_words = [
        word for word in words
        if word not in STOPWORDS
    ]

    return " ".join(cleaned_words)

# =========================
# EXTRACT TEXT FROM PDF
# =========================

def extract_text(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + " "

    return text.lower()

# =========================
# DETECT DOMAIN
# =========================

def detect_domain(text):

    scores = {}

    for domain, skills in SKILLS.items():

        scores[domain] = sum(
            1 for skill in skills
            if skill in text
        )

    return max(scores, key=scores.get)

# =========================
# MATCH SKILLS
# =========================

def match_skills(resume_text, jd_text, domain):

    domain_skills = SKILLS[domain]

    resume_skills = [
        skill for skill in domain_skills
        if skill in resume_text
    ]

    jd_skills = [
        skill for skill in domain_skills
        if skill in jd_text
    ]

    matched = list(
        set(resume_skills) & set(jd_skills)
    )

    missing = list(
        set(jd_skills) - set(resume_skills)
    )

    keyword_score = (
        len(matched) / len(jd_skills) * 100
        if jd_skills else 0
    )

    return matched, missing, keyword_score

# =========================
# ACHIEVEMENT DETECTION
# =========================

def detect_achievements(text):

    patterns = [

        r"\d+%",
        r"\d+\+",
        r"\d{2,}",

        "improved",
        "increased",
        "reduced",
        "optimized",
        "enhanced",
        "boosted",
        "generated",
        "delivered",
        "achieved"

    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )

# =========================
# SEMANTIC SCORE
# =========================

def calculate_semantic(text):

    impact_words = [

        "improved",
        "increased",
        "reduced",
        "optimized",
        "enhanced",
        "achieved",
        "boosted",
        "generated",
        "delivered"

    ]

    action_verbs = [

        "developed",
        "built",
        "created",
        "designed",
        "analyzed",
        "implemented",
        "managed",
        "automated",
        "engineered"

    ]

    score = 0

    for word in impact_words:

        if word in text:
            score += 12

    for word in action_verbs:

        if word in text:
            score += 8

    if re.search(r"\d+%", text):
        score += 20

    if re.search(r"\d+\+", text):
        score += 15

    return min(score, 100)

# =========================
# TEMPLATE CHECK
# =========================

def check_template(text):

    issues = []

    # STRICT separator detection

    if text.count("|") > 8:

        issues.append("Too many separators (|)")

    # STRICT table-like detection

    lines = text.split("\n")

    table_like_lines = 0

    for line in lines:

        if line.count("  ") >= 4:
            table_like_lines += 1

    if table_like_lines > 8:

        issues.append("Possible table formatting (ATS risk)")

    # Fancy symbols only

    fancy_symbols = ["►", "✓", "➤", "●", "★"]

    if any(symbol in text for symbol in fancy_symbols):

        issues.append(
            "Use simple bullet points instead of symbols"
        )

    return issues

# =========================
# MAIN ATS ANALYZER API
# =========================

@router.post("/analyze")

async def analyze_resume(
    user_id: int = Form(...),

    file: UploadFile = File(...),

    job_description: str = Form(...),
    db: Session = Depends(get_db)

):
    # FREE PLAN LIMIT CHECK

    subscription = db.query(
        Subscription
    ).filter(
        Subscription.user_id == user_id,
        Subscription.is_active == True,
        Subscription.payment_status == "Paid"
    ).first()

    total_analyses = db.query(
        Resume
    ).filter(
        Resume.user_id == user_id
    ).count()

    if not subscription:

        if total_analyses >= 2:
            raise HTTPException(
                status_code=403,
                detail="Free plan limit reached. Please upgrade your plan."
            )

    elif subscription.plan_name.lower() == "pro":

        if total_analyses >= 5:
            raise HTTPException(
                status_code=403,
                detail="Pro plan limit reached."
            )

    elif subscription.plan_name.lower() == "premium":

        if total_analyses >= 10:
            raise HTTPException(
                status_code=403,
                detail="Premium plan limit reached."
            )


    # Extract resume text

    resume_raw = extract_text(file.file)

    resume_text = clean_text(resume_raw)
    name = extract_name(resume_raw)
    email = extract_email(resume_raw)
    phone = extract_phone(resume_raw)
    linkedin = extract_linkedin(resume_raw)

    jd_text = clean_text(job_description)

    # Detect domains

    jd_domain = detect_domain(jd_text)

    resume_domain = detect_domain(resume_text)

    domain_match = jd_domain == resume_domain

    # Match skills

    matched, missing, keyword_score = match_skills(

        resume_text,
        jd_text,
        jd_domain

    )

    # Semantic score

    semantic_score = calculate_semantic(resume_text)

    # FINAL SCORE

    score = (

        (0.75 * keyword_score) +

        (0.25 * semantic_score)

    )

    # Quality checks

    quality_issues = []

    if not detect_achievements(resume_text):

        quality_issues.append(
            "No measurable achievements"
        )

    # Template issues

    template_issues = check_template(resume_raw)

    # Suggestions

    suggestions = []

    if "No measurable achievements" in quality_issues:

        suggestions.append(
            "Add impact with numbers (e.g., improved efficiency by 30%)"
        )

    if semantic_score < 60:

        suggestions.append(
            "Use strong action verbs and show results"
        )

    if missing:

        suggestions.append(
            f"Add missing skills: {', '.join(missing[:10])}"
        )

    if not template_issues:

        suggestions.append(
            "Resume format is ATS-friendly"
        )

    # Bonus for good ATS resume

    if (
        keyword_score >= 85 and
        semantic_score >= 60 and
        not template_issues
    ):

        score += 5

    # Limit max score

    score = min(score, 95)
    resume = Resume(
        user_id=user_id,
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        original_resume=resume_text,
        job_description=job_description,
        ats_score=int(score),
        missing_skills=", ".join(missing)
    )

    db.add(resume)

    db.commit()

    db.refresh(resume)
    activity = Activity(
        user_id=user_id,
        type="ats_scan",
        title=f"ATS Scan Completed ({int(score)}%)",
        description=f"Resume analyzed with ATS score {int(score)}%"
    )

    db.add(activity)
    db.commit()

    # FINAL RESPONSE

    return {
        "resume_id": resume.id,

        "jd_domain": jd_domain,

        "resume_domain": resume_domain,

        "domain_match": domain_match,

        "score": round(score, 2),

        "keyword_score": round(keyword_score, 2),

        "semantic_score": round(semantic_score, 2),

        "matched_skills": sorted(matched),

        "missing_skills": sorted(missing),

        "quality_issues": quality_issues,

        "template_issues": template_issues,

        "suggestions": suggestions

    }
class ResumeRequest(BaseModel):
    resume_text: str


import json

import json
from fastapi import Depends
from sqlalchemy.orm import Session

@router.post("/ai-rewrite")
def ai_rewrite(
    resume_id: int,
    data: ResumeCreate,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    prompt = f"""
You are an ATS Resume Expert.

Rewrite the resume according to the job description.

JOB DESCRIPTION:
{data.job_description}

ORIGINAL RESUME:
{data.original_resume}

MISSING SKILLS:
{data.missing_skills}

Return ONLY valid JSON.

Format:

{{
  "professional_summary": "",
  "technical_skills": [],
  "experience": [],
  "projects": [],
  "education": [],
  "certifications": [],
  "languages": [],
  "activities": []
}}

Rules:

1. JSON only
2. No markdown
3. No explanation
4. No extra text
5. Add missing skills naturally
6. ATS friendly
7. Professional content
8. Every section must contain data
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content

        rewritten_resume = json.loads(content)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI Rewrite Failed: {str(e)}"
        )

    resume.rewritten_resume = json.dumps(
        rewritten_resume,
        indent=2
    )

    db.commit()
    db.refresh(resume)
    activity = Activity(
        user_id=resume.user_id,
        type="resume_updated",
        title="AI Resume Rewritten",
        description="Resume rewritten using AI"
    )

    db.add(activity)
    db.commit()

    return {
        "resume_id": resume.id,
        "rewritten_resume": rewritten_resume
    }


@router.post("/save")
def save_resume(
    data: ResumeCreate,
    db: Session = Depends(get_db)
):

    resume = Resume(
        original_resume=data.original_resume,
        job_description=data.job_description,
        ats_score=data.ats_score,
        missing_skills=data.missing_skills,
        user_id=data.user_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        linkedin=data.linkedin,
        template_id=data.template_id

    )

    db.add(resume)

    db.commit()

    db.refresh(resume)
    activity = Activity(
        user_id=resume.user_id,
        type="resume_created",
        title="Resume Created",
        description="New resume saved successfully"
    )

    db.add(activity)
    db.commit()

    return {
        "message": "Resume saved",
        "resume_id": resume.id
    }



@router.get("/download/{resume_id}")
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.is_deleted==False
    ).first()

    if not resume:
        return {"error": "Resume not found"}

    filename = f"resume_{resume.id}.pdf"


    try:
        data = json.loads(resume.rewritten_resume)

        pdf_text = f"""
    PROFESSIONAL SUMMARY

    {data.get('professional_summary', '')}

    TECHNICAL SKILLS

    {data.get('technical_skills', '')}

    EXPERIENCE

    {data.get('experience', '')}

    PROJECTS

    {data.get('projects', '')}

    EDUCATION

    {data.get('education', '')}

    CERTIFICATIONS

    {data.get('certifications', '')}

    LANGUAGES

    {data.get('languages', '')}

    ACTIVITIES

    {data.get('activities', '')}
    """

    except:
        pdf_text = resume.rewritten_resume

    generate_resume_pdf(
        filename=filename,
        name=resume.name,
        email=resume.email,
        phone=resume.phone,
        linkedin=resume.linkedin,
        content=pdf_text
    )
    resume.pdf_url = f"/resume/download/{resume.id}"
    resume.is_generated = True
    resume.download_count += 1

    activity = Activity(
        user_id=resume.user_id,
        type="resume_download",
        title="Resume PDF Downloaded",
        description="Downloaded generated resume PDF"
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)
    db.refresh(resume)

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/pdf"
    )

@router.get("/")
def get_all_resumes(
    db: Session = Depends(get_db)
):

    resumes = db.query(Resume).filter(Resume.is_deleted== False).all()

    return [
        {
            "id": resume.id,
            "name": resume.name,
            "email": resume.email,
            "ats_score": resume.ats_score,
            "template_id": resume.template_id
        }
        for resume in resumes
    ]
@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.is_deleted==False
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Soft Delete
    resume.is_deleted = True

    # Activity Log
    activity = Activity(
        user_id=resume.user_id,
        type="resume_deleted",
        title="Resume Deleted",
        description="User deleted a resume"
    )

    db.add(activity)

    db.commit()

    db.refresh(resume)

    return {
        "message": "Resume deleted successfully"
    }
@router.get("/report/{resume_id}")
def get_resume_report(
    resume_id: int,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.is_deleted==False
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return {
        "resume_id": resume.id,
        "ats_score": resume.ats_score,
        "missing_skills": resume.missing_skills,
        "template_id": resume.template_id,
        "name": resume.name
    }
@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.is_deleted==False
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return {
        "id": resume.id,
        "name": resume.name,
        "email": resume.email,
        "phone": resume.phone,
        "linkedin": resume.linkedin,
        "ats_score": resume.ats_score,
        "job_description": resume.job_description,
        "missing_skills": resume.missing_skills,
        "rewritten_resume": resume.rewritten_resume,
        "pdf_url": resume.pdf_url,
        "template_id": resume.template_id
    }
@router.get("/user/{user_id}")
def get_resumes_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    resumes = (
        db.query(Resume)
        .filter(
            Resume.user_id == user_id,
            Resume.is_deleted == False
        )
        .order_by(Resume.updated_at.desc())
        .all()
    )

    return {
        "success": True,
        "message": "Resumes fetched successfully",
        "count": len(resumes),
        "data": [
            {
                "id": resume.id,
                "name": resume.name,
                "email": resume.email,
                "phone": resume.phone,
                "linkedin": resume.linkedin,

                "ats_score": resume.ats_score,

                "job_description": resume.job_description,

                "missing_skills": resume.missing_skills,

                "template_id": resume.template_id,

                "pdf_url": resume.pdf_url,

                "is_generated": resume.is_generated,

                "created_at": resume.created_at,

                "updated_at": resume.updated_at
            }
            for resume in resumes
        ]
    }