from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.template import Template
from app.models.resume import Resume
from app.schemas.template import TemplateSelect

router = APIRouter()

# =====================================================
# GET ALL TEMPLATES
# =====================================================

@router.get("/")
def get_templates(
    db: Session = Depends(get_db)
):

    templates = (
        db.query(Template)
        .filter(Template.is_active == True)
        .all()
    )

    return {
        "success": True,
        "message": "Templates fetched successfully",
        "count": len(templates),
        "data": [
            {
                "id": template.id,
                "name": template.name,
                "preview_image": template.preview_image,
                "thumbnail": template.thumbnail,
                "description": template.description,
                "category": template.category,
                "is_premium": template.is_premium,
                "is_active": template.is_active
            }
            for template in templates
        ]
    }


# =====================================================
# GET SINGLE TEMPLATE
# =====================================================

@router.get("/{template_id}")
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):

    template = (
        db.query(Template)
        .filter(
            Template.id == template_id,
            Template.is_active == True
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    return {
        "success": True,
        "data": {
            "id": template.id,
            "name": template.name,
            "preview_image": template.preview_image,
            "thumbnail": template.thumbnail,
            "description": template.description,
            "category": template.category,
            "is_premium": template.is_premium
        }
    }


# =====================================================
# SELECT TEMPLATE
# =====================================================

@router.post("/select")
def select_template(
    data: TemplateSelect,
    db: Session = Depends(get_db)
):

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == data.resume_id,
            Resume.is_deleted == False
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    template = (
        db.query(Template)
        .filter(
            Template.id == data.template_id,
            Template.is_active == True
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    resume.template_id = template.id
    resume.template_name = template.name

    db.commit()
    db.refresh(resume)

    return {
        "success": True,
        "message": "Template selected successfully",
        "data": {
            "resume_id": resume.id,
            "template_id": template.id,
            "template_name": template.name
        }
    }


# =====================================================
# CREATE DEFAULT TEMPLATES
# =====================================================

@router.post("/seed")
def seed_templates(
    db: Session = Depends(get_db)
):

    existing = db.query(Template).first()

    if existing:
        return {
            "success": True,
            "message": "Templates already exist"
        }

    templates = [

        Template(
            name="Classic ATS",
            preview_image="/static/templates/classic.png",
            thumbnail="/static/templates/classic-thumb.png",
            description="ATS Friendly Professional Resume",
            category="Professional",
            is_premium=False,
            is_active=True
        ),

        Template(
            name="Modern Pro",
            preview_image="/static/templates/modern.png",
            thumbnail="/static/templates/modern-thumb.png",
            description="Modern Premium Resume",
            category="Modern",
            is_premium=True,
            is_active=True
        ),

        Template(
            name="Executive",
            preview_image="/static/templates/executive.png",
            thumbnail="/static/templates/executive-thumb.png",
            description="Executive Level Resume",
            category="Executive",
            is_premium=True,
            is_active=True
        )

    ]

    db.add_all(templates)
    db.commit()

    return {
        "success": True,
        "message": "Templates created successfully",
        "count": len(templates)
    }


# =====================================================
# DELETE TEMPLATE (ADMIN)
# =====================================================

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):

    template = (
        db.query(Template)
        .filter(
            Template.id == template_id
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    template.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "Template deleted successfully"
    }