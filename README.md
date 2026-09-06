# JobTrack

JobTrack is a Job Application Tracker backend that lets users create, view, update, delete, search, filter, and analyze job applications.

## Project Structure

```
jobtrack/
    backend/
        app/          # FastAPI application code
        tests/        # Tests (pytest will be added later)
    README.md
    .gitignore
```

## Tech Stack (planned)

- **Python**
- **FastAPI** – web framework
- **Uvicorn** – ASGI server
- **pytest** – test framework (added later)
- **SQLite** – database (added later)
- **SQLAlchemy** – ORM (added later)

## Getting Started

### 1. Create and activate a virtual environment

From the `backend/` directory:

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Or activate it (macOS / Linux)
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
uvicorn app.main:app --reload
```

The application will be available at http://127.0.0.1:8000.

Interactive API docs: http://127.0.0.1:8000/docs

### 4. Check the health endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```
