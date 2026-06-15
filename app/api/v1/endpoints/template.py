from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.template import Template
from app.models.resume import Resume
from app.schemas.template import TemplateSelect

router = APIRouter()


@router.get("/")
def get_templates(db: Session = Depends(get_db)):

    templates = db.query(Template).all()

    return {
        "count": len(templates),
        "templates": [
            {
                "id": template.id,
                "name": template.name,
                "preview_image": template.preview_image,
                "description": template.description,
                "is_premium": template.is_premium
            }
            for template in templates
        ]
    }


@router.post("/select")
def select_template(
    data: TemplateSelect,
    db: Session = Depends(get_db)
):

    resume = (
        db.query(Resume)
        .filter(Resume.id == data.resume_id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    template = (
        db.query(Template)
        .filter(Template.id == data.template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    resume.template_id = data.template_id

    db.commit()

    return {
        "message": "Template selected successfully",
        "resume_id": resume.id,
        "template_id": template.id,
        "template_name": template.name
    }


@router.post("/seed")
def seed_templates(db: Session = Depends(get_db)):

    existing = db.query(Template).first()

    if existing:
        return {
            "message": "Templates already exist"
        }

    templates = [
        Template(
            name="Classic ATS",
            preview_image="classic.png",
            description="ATS friendly professional template",
            is_premium=False
        ),
        Template(
            name="Modern Pro",
            preview_image="modern.png",
            description="Modern premium template",
            is_premium=True
        ),
        Template(
            name="Executive",
            preview_image="executive.png",
            description="Executive level resume",
            is_premium=True
        )
    ]

    db.add_all(templates)
    db.commit()

    return {
        "message": "Templates created successfully"
    }