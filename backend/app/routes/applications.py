from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Application
from schemas import ApplicationCreate, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    application: ApplicationCreate, db: Session = Depends(get_db)
):
    db_application = Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("", response_model=list[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).all()
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
