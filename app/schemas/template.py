from pydantic import BaseModel

class TemplateSelect(BaseModel):
    resume_id: int
    template_id: int