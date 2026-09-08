from fastapi import FastAPI

from database import Base, engine
from models import Application

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobTrack API",
    description="A Job Application Tracker backend",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}