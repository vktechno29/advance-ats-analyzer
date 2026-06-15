from sqlalchemy import Column, Integer, String, Boolean
from app.database.db import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    preview_image = Column(String)

    description = Column(String)

    is_premium = Column(Boolean, default=False)