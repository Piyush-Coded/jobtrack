from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: int
    company_name: str
    job_title: str
    location: str
    job_url: str
    employment_type: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[str] = "Applied"
    interview_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[float] = None
    applied_date: Optional[datetime] = None
    status: Optional[str] = None
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


# Auth schemas
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # "job_seeker" or "recruiter"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime


# Job Seeker Profile schemas
class JobSeekerProfileCreate(BaseModel):
    headline: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class JobSeekerProfileUpdate(BaseModel):
    headline: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class JobSeekerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    headline: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Company Profile schemas
class CompanyProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recruiter_user_id: int
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Job schemas
class JobCreate(BaseModel):
    title: str
    description: str
    location: str
    employment_type: Optional[str] = "full_time"
    work_mode: Optional[str] = "hybrid"
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[str] = None
    education: Optional[str] = None
    status: Optional[str] = "draft"
    closing_date: Optional[datetime] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[str] = None
    education: Optional[str] = None
    status: Optional[str] = None
    closing_date: Optional[datetime] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    title: str
    description: str
    location: str
    employment_type: str
    work_mode: str
    experience_min: int
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[str] = None
    education: Optional[str] = None
    status: str
    posted_at: datetime
    closing_date: Optional[datetime] = None


class JobListResponse(BaseModel):
    id: int
    title: str
    company_name: str
    location: str
    employment_type: str
    work_mode: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: str
    posted_at: datetime


# Application schemas for responses
class ApplicationStatusUpdate(BaseModel):
    status: str


# Statistics schemas
class StatisticsResponse(BaseModel):
    total_applications: int
    by_status: dict
    by_employment_type: dict
    average_salary: Optional[float] = None