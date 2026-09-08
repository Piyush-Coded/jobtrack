from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Application

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
            counts[value] = count
    return counts


@router.get("")
def get_statistics(db: Session = Depends(get_db)):
    total = db.query(func.count(Application.id)).scalar()

    by_status = _count_by_column(db, Application.status)
    by_employment_type = _count_by_column(db, Application.employment_type)

    avg = db.query(func.avg(Application.salary)).scalar()
    average_salary = round(avg, 2) if avg is not None else None

    return {
        "total_applications": total,
        "by_status": by_status,
        "by_employment_type": by_employment_type,
        "average_salary": average_salary,
    }
