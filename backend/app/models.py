from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_url = Column(String, nullable=False)
    employment_type = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    applied_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="Applied")
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)