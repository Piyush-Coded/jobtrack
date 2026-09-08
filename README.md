# JobTrack

JobTrack — Job Application Tracker

![Python](https://img.shields.io/badge/Python-3.14-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-0d597f)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57)
![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063)
![pytest](https://img.shields.io/badge/pytest-9.1-0A9EDC)
![tests](https://img.shields.io/badge/tests-22%20passed-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

## Description

JobTrack is a REST API backend that helps users track their job applications. It provides a simple, practical way to create, view, update, and delete job applications, plus search, filtering, sorting, and statistics — all backed by a local SQLite database. It is intended as a clean, well-tested backend that a future frontend can plug into.

## Features

- Create applications
- View applications
- Update applications
- Delete applications
- Search (case-insensitive across company, title, location)
- Filtering (by status and employment type)
- Sorting (whitelisted fields, ascending/descending)
- Statistics (totals, breakdowns, average salary)
- REST API
- SQLite database
- API validation (Pydantic schemas)
- Automated tests (pytest)

## Tech Stack

- **Python**
- **FastAPI** – web framework
- **SQLAlchemy** – ORM
- **SQLite** – database
- **Pydantic** – request/response validation
- **Pytest** – automated testing
- **Git/GitHub** – version control

## Architecture

```
Client
  ↓
FastAPI
  ↓
SQLAlchemy
  ↓
SQLite
```

The FastAPI app exposes HTTP endpoints. Each request is validated by Pydantic schemas, then handled by SQLAlchemy against the SQLite database.

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/applications` | Create an application |
| GET | `/api/applications` | List applications (search, filter, sort) |
| GET | `/api/applications/{id}` | Get an application by ID |
| PUT | `/api/applications/{id}` | Update an application |
| DELETE | `/api/applications/{id}` | Delete an application |
| GET | `/api/statistics` | Get application statistics |

### List query parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `search` | Case-insensitive match on company, title, location | `?search=python` |
| `status` | Filter by exact status | `?status=Interview` |
| `employment_type` | Filter by exact employment type | `?employment_type=Full-time` |
| `sort_by` | Sort field: `company_name`, `job_title`, `applied_date`, `salary`, `status` | `?sort_by=salary` |
| `order` | Sort direction: `asc` or `desc` | `?order=desc` |

## Example Request

```json
{
  "company_name": "Google",
  "job_title": "Python Backend Developer",
  "location": "Bangalore",
  "job_url": "https://example.com/job",
  "employment_type": "Full-time",
  "salary": 800000,
  "status": "Applied",
  "interview_date": null,
  "notes": "Applied through company website"
}
```

## Running Locally

Open a terminal and run these commands (Windows/PowerShell):

1. Enter the app directory:

   ```powershell
   cd D:\jobtrack\backend\app
   ```

2. Activate the virtual environment:

   ```powershell
   ..\.venv\Scripts\Activate.ps1
   ```

3. Install requirements:

   ```powershell
   pip install -r ..\requirements.txt
   ```

4. Start the FastAPI/Uvicorn server:

   ```powershell
   uvicorn main:app --reload
   ```

   The API runs at `http://127.0.0.1:8000`.

5. Access the API documentation at:

   - `http://127.0.0.1:8000/docs` (Swagger UI)
   - `http://127.0.0.1:8000/redoc` (ReDoc)

## Testing

From the `backend` directory, run:

```powershell
cd D:\jobtrack\backend
pytest
```

The test suite uses an isolated in-memory SQLite database, so the real `backend/app/jobtrack.db` is never touched.

## Project Structure

```
jobtrack/
├── README.md
├── .gitignore
└── backend/
    ├── requirements.txt
    ├── .venv/                    # virtual environment (not committed)
    ├── app/
    │   ├── main.py               # FastAPI app entry point
    │   ├── database.py           # SQLAlchemy engine, session, get_db dependency
    │   ├── models.py             # SQLAlchemy Application model
    │   ├── schemas.py            # Pydantic request/response schemas
    │   ├── routes/
    │   │   ├── applications.py   # application CRUD + search/filter/sort
    │   │   └── statistics.py     # statistics endpoint
    │   └── jobtrack.db           # SQLite database (committed as sample)
    └── tests/
        ├── conftest.py           # isolated test DB fixture
        └── test_api.py           # API test suite
```