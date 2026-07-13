from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.database.db import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    preview_image = Column(String(500), nullable=False)

    thumbnail = Column(String(500), nullable=True)

    description = Column(String(500), nullable=True)

    category = Column(String(100), default="Professional")

    is_premium = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )