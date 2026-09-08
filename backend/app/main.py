from fastapi import FastAPI

from database import Base, engine
from models import Application
from routes.applications import router as applications_router
from routes.statistics import router as statistics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobTrack API",
    description="A Job Application Tracker backend",
    version="0.1.0",
)

app.include_router(applications_router)
app.include_router(statistics_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}