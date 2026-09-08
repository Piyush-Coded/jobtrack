from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    location: str
    job_url: str
    employment_type: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[str] = "Applied"
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    job_title: str
    location: str
    job_url: str
    employment_type: Optional[str] = None
    salary: Optional[float] = None
    applied_date: datetime
    status: str
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
