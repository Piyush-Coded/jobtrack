from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    employment_type = Column(String, nullable=False, default="full_time")
    work_mode = Column(String, nullable=False, default="hybrid")
    experience_min = Column(Integer, nullable=True, default=0)
    experience_max = Column(Integer, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    skills = Column(Text, nullable=True)  # JSON or comma-separated
    education = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="draft")  # draft, published, closed
    posted_at = Column(DateTime, nullable=False, server_default=func.now())
    closing_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Useful status values: draft, published, closed
    # Useful employment types: full_time, part_time, contract, internship
    # Useful work modes: remote, hybrid, on_site