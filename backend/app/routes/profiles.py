from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user, require_job_seeker
from models import User, JobSeekerProfile
from schemas import (
    JobSeekerProfileCreate,
    JobSeekerProfileUpdate,
    JobSeekerProfileResponse,
)


router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("/me", response_model=JobSeekerProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's job seeker profile."""
    profile = db.query(JobSeekerProfile).filter(JobSeekerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.put("/me", response_model=JobSeekerProfileResponse)
def update_my_profile(
    profile_data: JobSeekerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's job seeker profile."""
    profile = db.query(JobSeekerProfile).filter(JobSeekerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile