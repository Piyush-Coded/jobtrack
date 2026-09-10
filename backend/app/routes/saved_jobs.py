from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user, require_job_seeker
from models import Job, SavedJob, Application


router = APIRouter(prefix="/api/saved-jobs", tags=["saved-jobs"])


@router.post("/{job_id}/save", status_code=status.HTTP_201_CREATED)
def save_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """Save a job (job seeker only)."""
    # Check if job exists and is published
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if job.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot save a draft or closed job",
        )

    # Check if already saved
    existing = (
        db.query(SavedJob)
        .filter(
            SavedJob.job_id == job_id,
            SavedJob.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already saved",
        )

    new_saved = SavedJob(job_id=job_id, user_id=current_user.id)
    db.add(new_saved)
    db.commit()
    return {"message": "Job saved successfully"}


@router.delete("/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """Unsave a job (job seeker only)."""
    saved = (
        db.query(SavedJob)
        .filter(
            SavedJob.job_id == job_id,
            SavedJob.user_id == current_user.id,
        )
        .first()
    )
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not saved",
        )

    db.delete(saved)
    db.commit()
    return None


@router.get("/me", response_model=dict)
def list_saved_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """List saved jobs for current user."""
    saved = (
        db.query(SavedJob, Job)
        .join(Job, SavedJob.job_id == Job.id)
        .filter(SavedJob.user_id == current_user.id, Job.status == "published")
        .all()
    )

    result = []
    for saved_job, job in saved:
        result.append({
            "saved_job_id": saved_job.id,
            "job_id": job.id,
            "title": job.title,
            "company_name": "Company not loaded",  # Would need join with CompanyProfile
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "work_mode": job.work_mode,
            "employment_type": job.employment_type,
            "posted_at": job.posted_at,
        })
    return {"saved_jobs": result, "count": len(result)}