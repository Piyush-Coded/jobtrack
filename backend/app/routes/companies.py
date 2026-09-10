from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import get_current_user, require_recruiter, require_admin
from models import User, CompanyProfile, Job
from schemas import CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileResponse


router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.post("", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_company_profile(
    company_data: CompanyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    """Create company profile (recruiter only)."""
    # Check if company profile already exists
    existing = db.query(CompanyProfile).filter(CompanyProfile.recruiter_user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile already exists",
        )

    new_company = CompanyProfile(
        recruiter_user_id=current_user.id,
        **company_data.model_dump(),
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company


@router.get("/me", response_model=CompanyProfileResponse)
def get_my_company(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's company profile."""
    company = db.query(CompanyProfile).filter(CompanyProfile.recruiter_user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )
    return company


@router.put("/me", response_model=CompanyProfileResponse)
def update_company_profile(
    company_data: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's company profile."""
    company = db.query(CompanyProfile).filter(CompanyProfile.recruiter_user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    for field, value in company_data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=list[CompanyProfileResponse])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all companies - admin only."""
    companies = db.query(CompanyProfile).all()
    return companies