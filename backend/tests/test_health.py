def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data


def test_quiz_endpoint(client):
    response = client.get("/api/v1/quiz/questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) >= 1
