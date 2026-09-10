from fastapi import FastAPI

from database import Base, engine
from models import *
from routes.auth import router as auth_router
from routes.applications import router as applications_router
from routes.statistics import router as statistics_router
from routes.jobs import router as jobs_router
from routes.users import router as users_router
from routes.profiles import router as profiles_router
from routes.companies import router as companies_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobTrack API",
    description="A Job Application Tracker backend",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(statistics_router)
app.include_router(jobs_router)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(companies_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}