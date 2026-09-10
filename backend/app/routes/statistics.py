from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Application, Job


router = APIRouter(prefix="/api/statistics", tags=["statistics"])


def _count_by_column(db: Session, column) -> dict:
    rows = (
        db.query(column, func.count(Application.id))
        .group_by(column)
        .all()
    )
    counts = {}
    for value, count in rows:
        if value is not None:
            counts[str(value)] = count
    return counts


@router.get("", response_model=dict)
def get_statistics(db: Session = Depends(get_db)):
    total = db.query(func.count(Application.id)).scalar()

    by_status = _count_by_column(db, Application.status)
    by_employment_type = _count_by_column(db, Job.employment_type)

    avg = db.query(func.avg(Job.salary_min)).scalar()
    average_salary = round(float(avg), 2) if avg is not None else None

    # Count by job status
    jobs_total = db.query(func.count(Job.id)).scalar()
    jobs_published = db.query(func.count(Job.id)).filter(Job.status == "published").scalar()
    jobs_draft = db.query(func.count(Job.id)).filter(Job.status == "draft").scalar()
    jobs_closed = db.query(func.count(Job.id)).filter(Job.status == "closed").scalar()

    return {
        "total_applications": total,
        "by_status": by_status,
        "by_employment_type": by_employment_type,
        "average_salary": average_salary,
        "jobs": {
            "total": jobs_total,
            "published": jobs_published,
            "draft": jobs_draft,
            "closed": jobs_closed,
        },
    }