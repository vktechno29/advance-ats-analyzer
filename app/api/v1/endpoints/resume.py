from fastapi import APIRouter, UploadFile, File, Form
import pdfplumber
import re
from pydantic import BaseModel
from openai import OpenAI
import os
from app.schemas.resume import ResumeCreate
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database.db import get_db
from app.models.resume import Resume
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

    file: UploadFile = File(...),

    job_description: str = Form(...)

):

    # Extract resume text

    resume_raw = extract_text(file.file)

    resume_text = clean_text(resume_raw)

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

    # FINAL RESPONSE

    return {

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


@router.post("/ai-rewrite")
def ai_rewrite(data: ResumeRequest):

    prompt = f"""
    Rewrite this resume professionally.

    Make it:
    - ATS optimized
    - Professional
    - Clean
    - Strong action words
    - Better formatting

    Resume:

    {data.resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "rewritten_resume": response.choices[0].message.content
    }
@router.post("/save")
def save_resume(
    data: ResumeCreate,
    db: Session = Depends(get_db)
):

    resume = Resume(
        original_resume=data.original_resume,
        ats_score=data.ats_score,
        missing_skills=data.missing_skills,
        job_description=data.job_description
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume Saved",
        "resume_id": resume.id
    }

 👇
@router.post("/rewrite/{resume_id}")
def rewrite_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

    if not resume:
        return {"error": "Resume not found"}

    prompt = f"""
    Rewrite this resume professionally.

    ATS Score: {resume.ats_score}

    Missing Skills:
    {resume.missing_skills}

    Resume:
    {resume.original_resume}

    Improve ATS score.
    Add strong action verbs.
    Improve formatting.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    rewritten = response.choices[0].message.content

    resume.rewritten_resume = rewritten

    db.commit()

    return {
        "resume_id": resume.id,
        "rewritten_resume": rewritten
    }