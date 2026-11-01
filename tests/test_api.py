import pytest
from fastapi.testclient import TestClient

from api.main import app
from career_agent.clients.github import get_github_client
from career_agent.clients.llm import get_llm_client


@pytest.fixture
def client(fake_llm, fake_github):
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    app.dependency_overrides[get_github_client] = lambda: fake_github
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_root(client):
    assert client.get("/").json() == {"message": "Career AI Agent Running"}


def test_analyze_returns_career_strategy(client, fake_llm, fake_github):
    resp = client.post(
        "/analyze",
        json={"cv_text": "cv", "github_username": "octocat", "target_role": "SRE"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"career_strategy": fake_llm.reply}
    assert fake_github.usernames == ["octocat"]


def test_analyze_without_api_key_returns_503(fake_github):
    app.dependency_overrides[get_github_client] = lambda: fake_github
    try:
        resp = TestClient(app).post(
            "/analyze", json={"cv_text": "cv", "github_username": "u", "target_role": "r"}
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 503
    assert "GROQ_API_KEY" not in resp.text


def test_analyze_validates_body(client):
    assert client.post("/analyze", json={"cv_text": "cv"}).status_code == 422
