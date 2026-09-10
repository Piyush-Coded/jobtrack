from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from database import get_db
from dependencies.auth import get_current_user, require_job_seeker, require_recruiter
from models import User, Job, JobSeekerProfile, CompanyProfile
from schemas import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
)


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobListResponse])
def list_jobs(
    search: Optional[str] = None,
    location: Optional[str] = None,
    employment_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    skills: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    db: Session = Depends(get_db),
):
    """List jobs with filtering and search."""
    query = db.query(Job).filter(Job.status == "published")

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.description.ilike(pattern),
                Job.skills.ilike(pattern),
                CompanyProfile.name.ilike(pattern),
            )
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if employment_type:
        query = query.filter(Job.employment_type == employment_type)

    if work_mode:
        query = query.filter(Job.work_mode == work_mode)

    if experience_min is not None:
        query = query.filter(Job.experience_min >= experience_min)

    if experience_max is not None:
        query = query.filter(Job.experience_max <= experience_max)

    if salary_min is not None:
        query = query.filter(Job.salary_min >= salary_min)

    if salary_max is not None:
        query = query.filter(Job.salary_max <= salary_max)

    if skills:
        query = query.filter(Job.skills.ilike(f"%{skills}%"))

    # Sort
    if sort_by:
        field = getattr(Job, sort_by, None)
        if field is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sort field",
            )
        column = field
        query = query.order_by(column.desc() if order == "desc" else column.asc())
    else:
        query = query.order_by(Job.posted_at.desc())

    return query.all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job details."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Get company info
    company = db.query(CompanyProfile).filter(CompanyProfile.id == job.company_id).first()
    
    # Build response manually
    return {
        "id": job.id,
        "company_id": job.company_id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "employment_type": job.employment_type,
        "work_mode": job.work_mode,
        "experience_min": job.experience_min,
        "experience_max": job.experience_max,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "skills": job.skills,
        "education": job.education,
        "status": job.status,
        "posted_at": job.posted_at,
        "closing_date": job.closing_date,
        "company": {
            "id": company.id if company else None,
            "name": company.name if company else None,
            "description": company.description if company else None,
            "website": company.website if company else None,
            "industry": company.industry if company else None,
            "company_size": company.company_size if company else None,
            "location": company.location if company else None,
            "logo_url": company.logo_url if company else None,
        } if company else None,
    }


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Create a new job posting (recruiter only)."""
    # Check if user has a company profile
    company = db.query(CompanyProfile).filter(CompanyProfile.recruiter_user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must create a company profile first before posting jobs",
        )

    new_job = Job(
        company_id=company.id,
        **job_data.model_dump(),
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Update job (recruiter can only edit their own jobs)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Check ownership
    company = db.query(CompanyProfile).filter(CompanyProfile.id == job.company_id).first()
    if company.recruiter_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own jobs",
        )

    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Delete/close job (recruiter can only delete their own jobs)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # Check ownership
    company = db.query(CompanyProfile).filter(CompanyProfile.id == job.company_id).first()
    if company.recruiter_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only close your own jobs",
        )

    # Soft delete - set status to closed instead of deleting
    job.status = "closed"
    db.commit()
    return None