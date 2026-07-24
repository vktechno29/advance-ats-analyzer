from pydantic import BaseModel

class TemplateSelect(BaseModel):
    resume_id: int
    template_id: int
class TemplateResponse(BaseModel):
    id: int
    name: str
    preview_image: str
    thumbnail: str | None = None
    description: str | None = None
    category: str
    is_premium: bool
    is_active: bool

    class Config:
        from_attributes = True


class TemplateSeed(BaseModel):
    name: str
    preview_image: str
    thumbnail: str | None = None
    description: str | None = None
    category: str = "Professional"
    is_premium: bool = False