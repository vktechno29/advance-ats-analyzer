from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db import Base


class Activity(Base):
    __tablename__ = "activities"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # User
    # =====================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user = relationship(
        "User",
        back_populates="activities"
    )

    # =====================================================
    # Activity Details
    # =====================================================

    type = Column(
        String(100),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )

    # =====================================================
    # Timestamp
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )