from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import Application
from schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate

router = APIRouter(prefix="/api/applications", tags=["applications"])

SORT_FIELDS = {
    "company_name": Application.company_name,
    "job_title": Application.job_title,
    "applied_date": Application.applied_date,
    "salary": Application.salary,
    "status": Application.status,
}

VALID_ORDERS = {"asc", "desc"}


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
def list_applications(
    search: Optional[str] = None,
    status: Optional[str] = None,
    employment_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    db: Session = Depends(get_db),
):
    query = db.query(Application)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Application.company_name.ilike(pattern),
                Application.job_title.ilike(pattern),
                Application.location.ilike(pattern),
            )
        )

    if status:
        query = query.filter(Application.status == status)

    if employment_type:
        query = query.filter(Application.employment_type == employment_type)

    if sort_by:
        if sort_by not in SORT_FIELDS:
            raise HTTPException(status_code=400, detail="Invalid sort field")
        if order not in VALID_ORDERS:
            raise HTTPException(status_code=400, detail="Invalid sort order")
        column = SORT_FIELDS[sort_by]
        query = query.order_by(column.desc() if order == "desc" else column.asc())
    else:
        query = query.order_by(Application.applied_date.desc())

    return query.all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in application_update.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()
    return None
