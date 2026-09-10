from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user, require_job_seeker, require_recruiter
from models import Job, Application, User
from schemas import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate


router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """Apply to a job (job seeker only)."""
    job_id = application_data.job_id
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
            detail="Cannot apply to a draft or closed job",
        )

    # Check if user already applied
    existing_application = (
        db.query(Application)
        .filter(
            Application.job_id == job_id,
            Application.candidate_user_id == current_user.id,
        )
        .first()
    )
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        )

    # Create application
    new_application = Application(
        job_id=job_id,
        candidate_user_id=current_user.id,
        resume_url=application_data.get("resume_url"),
        cover_letter=application_data.get("cover_letter"),
        status="applied",
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@router.get("", response_model=list[ApplicationResponse])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """List current user's applications."""
    applications = (
        db.query(Application)
        .filter(Application.candidate_user_id == current_user.id)
        .all()
    )
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_job_seeker),
):
    """Get specific application."""
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.candidate_user_id == current_user.id)
        .first()
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Update application status (recruiter only)."""
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check that the job belongs to the recruiter's company
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    company = db.query(CompanyProfile).filter(CompanyProfile.id == job.company_id).first()
    if company.recruiter_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update applications for your own jobs",
        )

    application.status = status_update.status
    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return application