from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.db import Base


class Resume(Base):
    __tablename__ = "resumes"

    # ==========================================================
    # Primary Key
    # ==========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==========================================================
    # User Relationship
    # ==========================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )

    # ==========================================================
    # Resume Information
    # ==========================================================

    title = Column(
        String(255),
        nullable=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False
    )

    phone = Column(
        String(30),
        nullable=True
    )

    linkedin = Column(
        String(500),
        nullable=True
    )

    # ==========================================================
    # Uploaded Resume
    # ==========================================================

    original_resume = Column(
        Text,
        nullable=True
    )

    # ==========================================================
    # ATS Analysis
    # ==========================================================

    ats_score = Column(
        Integer,
        default=0
    )

    job_description = Column(
        Text,
        nullable=True
    )

    missing_skills = Column(
        Text,
        nullable=True
    )

    # ==========================================================
    # AI Generated Resume
    # ==========================================================

    rewritten_resume = Column(
        Text,
        nullable=True
    )

    # ==========================================================
    # Resume Template
    # ==========================================================

    template_id = Column(
        Integer,
        default=1
    )

    template_name = Column(
        String(100),
        default="Modern"
    )

    thumbnail = Column(
        String(1000),
        nullable=True
    )

    # ==========================================================
    # Generated PDF
    # ==========================================================

    pdf_url = Column(
        String(1000),
        nullable=True
    )

    # ==========================================================
    # Resume Status
    # ==========================================================

    status = Column(
        String(30),
        default="saved"
    )

    is_generated = Column(
        Boolean,
        default=False
    )

    is_deleted = Column(
        Boolean,
        default=False
    )

    # ==========================================================
    # Analytics
    # ==========================================================

    download_count = Column(
        Integer,
        default=0
    )

    preview_count = Column(
        Integer,
        default=0
    )

    # ==========================================================
    # Timestamps
    # ==========================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )