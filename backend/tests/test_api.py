def _sample_payload(**overrides):
    payload = {
        "company_name": "Acme Corp",
        "job_title": "Python Developer",
        "location": "Bangalore",
        "job_url": "https://example.com/job",
        "employment_type": "Full-time",
        "salary": 800000,
        "status": "Applied",
        "interview_date": None,
        "notes": "Test application",
    }
    payload.update(overrides)
    return payload


def _create_application(client, **overrides):
    response = client.post("/api/applications", json=_sample_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_application(client):
    data = _create_application(client)
    assert data["company_name"] == "Acme Corp"
    assert data["job_title"] == "Python Developer"
    assert data["status"] == "Applied"
    assert data["id"] is not None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_application_invalid_body(client):
    response = client.post("/api/applications", json={"company_name": "Missing fields"})
    assert response.status_code == 422


def test_list_applications(client):
    _create_application(client)
    _create_application(client, company_name="Other Corp")

    response = client.get("/api/applications")
    assert response.status_code == 200
    applications = response.json()
    companies = {a["company_name"] for a in applications}
    assert {"Acme Corp", "Other Corp"} <= companies


def test_get_application_by_id(client):
    created = _create_application(client)
    response = client.get(f"/api/applications/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["job_title"] == "Python Developer"


def test_get_missing_application(client):
    response = client.get("/api/applications/999999")
    assert response.status_code == 404


def test_get_application_invalid_id(client):
    response = client.get("/api/applications/not-an-int")
    assert response.status_code == 422


def test_update_application(client):
    created = _create_application(client)
    response = client.put(
        f"/api/applications/{created['id']}",
        json={
            "job_title": "Senior Python Developer",
            "status": "Interview",
            "notes": "Updated via PUT",
        },
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["job_title"] == "Senior Python Developer"
    assert updated["status"] == "Interview"
    assert updated["notes"] == "Updated via PUT"


def test_update_missing_application(client):
    response = client.put("/api/applications/999999", json={"status": "Interview"})
    assert response.status_code == 404


def test_delete_application(client):
    created = _create_application(client)
    response = client.delete(f"/api/applications/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/applications/{created['id']}")
    assert response.status_code == 404


def test_delete_missing_application(client):
    response = client.delete("/api/applications/999999")
    assert response.status_code == 404


def test_statistics(client):
    _create_application(client, status="Applied", employment_type="Full-time", salary=800000)
    _create_application(client, status="Interview", employment_type="Full-time", salary=1000000)
    _create_application(client, status="Interview", employment_type="Internship", salary=400000)

    response = client.get("/api/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_applications"] == 3
    assert stats["by_status"] == {"Applied": 1, "Interview": 2}
    assert stats["by_employment_type"] == {"Full-time": 2, "Internship": 1}
    assert stats["average_salary"] == 733333.33


def test_statistics_empty(client):
    response = client.get("/api/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_applications"] == 0
    assert stats["by_status"] == {}
    assert stats["by_employment_type"] == {}
    assert stats["average_salary"] is None


def test_search_applications(client):
    _create_application(client, company_name="Google", job_title="Python Backend Developer")
    _create_application(client, company_name="Netflix", job_title="Frontend JS Developer")

    response = client.get("/api/applications", params={"search": "python"})
    assert response.status_code == 200
    titles = [a["job_title"] for a in response.json()]
    assert titles == ["Python Backend Developer"]


def test_search_case_insensitive(client):
    _create_application(client, company_name="OpenAI")
    response = client.get("/api/applications", params={"search": "OPENAI"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_by_status(client):
    _create_application(client, status="Applied")
    _create_application(client, status="Interview")

    response = client.get("/api/applications", params={"status": "Interview"})
    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 1
    assert applications[0]["status"] == "Interview"


def test_filter_by_employment_type(client):
    _create_application(client, employment_type="Full-time")
    _create_application(client, employment_type="Internship")

    response = client.get(
        "/api/applications", params={"employment_type": "Internship"}
    )
    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 1
    assert applications[0]["employment_type"] == "Internship"


def test_sort_applications_desc(client):
    _create_application(client, salary=800000)
    _create_application(client, salary=1200000)
    _create_application(client, salary=300000)

    response = client.get(
        "/api/applications", params={"sort_by": "salary", "order": "desc"}
    )
    assert response.status_code == 200
    salaries = [a["salary"] for a in response.json()]
    assert salaries == [1200000.0, 800000.0, 300000.0]


def test_sort_applications_asc(client):
    _create_application(client, salary=800000)
    _create_application(client, salary=1200000)

    response = client.get(
        "/api/applications", params={"sort_by": "salary", "order": "asc"}
    )
    assert response.status_code == 200
    salaries = [a["salary"] for a in response.json()]
    assert salaries == [800000.0, 1200000.0]


def test_combined_search_filter_sort(client):
    _create_application(
        client,
        company_name="Google",
        job_title="Python Backend Developer",
        status="Interview",
        salary=1000000,
    )
    _create_application(
        client,
        company_name="Google",
        job_title="Python Intern",
        status="Applied",
        salary=400000,
    )

    response = client.get(
        "/api/applications",
        params={
            "search": "python",
            "status": "Interview",
            "sort_by": "salary",
            "order": "desc",
        },
    )
    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 1
    assert applications[0]["job_title"] == "Python Backend Developer"


def test_invalid_sort_field(client):
    response = client.get(
        "/api/applications", params={"sort_by": "invalid", "order": "desc"}
    )
    assert response.status_code == 400


def test_invalid_sort_order(client):
    response = client.get(
        "/api/applications", params={"sort_by": "salary", "order": "sideways"}
    )
    assert response.status_code == 400