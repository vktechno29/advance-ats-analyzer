from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# -----------------------------
# User Card
# -----------------------------
class DashboardUser(BaseModel):
    id: int
    name: str
    email: str
    plan: str
    active_subscription: bool
    resume_limit: int
    resumes_uploaded: int
    remaining: int


# -----------------------------
# Statistics
# -----------------------------
class DashboardStatistics(BaseModel):
    totalResumes: int
    atsScans: int
    averageAtsScore: float
    downloads: int


# -----------------------------
# Recent Activity
# -----------------------------
class ActivityItem(BaseModel):
    id: int
    type: str
    title: str
    time: str
    createdAt: datetime


# -----------------------------
# Resume Actions
# -----------------------------
class ResumeActions(BaseModel):
    edit: str
    preview: str
    downloadPdf: str


# -----------------------------
# Resume Card
# -----------------------------
class ResumeCard(BaseModel):
    id: int
    title: str
    template: str
    thumbnail: Optional[str] = None
    pdf_url: Optional[str] = None
    atsScore: Optional[int] = None
    status: str
    lastUpdated: str
    createdAt: datetime
    updatedAt: datetime
    actions: ResumeActions


# -----------------------------
# Dashboard Data
# -----------------------------
class DashboardData(BaseModel):
    user: DashboardUser
    statistics: DashboardStatistics
    recentActivity: List[ActivityItem]
    resumes: List[ResumeCard]


# -----------------------------
# Final Response
# -----------------------------
class DashboardResponse(BaseModel):
    success: bool
    message: str
    data: DashboardData