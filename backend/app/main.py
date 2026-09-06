from fastapi import FastAPI

app = FastAPI(
    title="JobTrack API",
    description="A Job Application Tracker backend",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
