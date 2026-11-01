import requests
import responses

from career_agent.clients.github import RestGitHubClient
from career_agent.config import Settings

URL = "https://api.github.com/users/octocat/repos"


def _repo(name, stars, language="Python"):
    return {
        "name": name,
        "description": f"{name} desc",
        "stargazers_count": stars,
        "language": language,
        "updated_at": "2026-01-01T00:00:00Z",
    }


@responses.activate
def test_fetch_profile_keeps_top_five_by_stars():
    repos = [_repo(f"r{i}", i) for i in range(7)] + [_repo("js", 100, "JavaScript")]
    responses.get(URL, json=repos)

    profile = RestGitHubClient(Settings()).fetch_profile("octocat")

    assert [r.name for r in profile.repos] == ["js", "r6", "r5", "r4", "r3"]
    assert profile.repo_count == 8
    assert profile.total_stars == 100 + 6 + 5 + 4 + 3
    assert profile.top_languages == {"Python": 4, "JavaScript": 1}


@responses.activate
def test_fetch_profile_returns_empty_on_http_error():
    responses.get(URL, status=404)

    profile = RestGitHubClient(Settings()).fetch_profile("octocat")

    assert profile.repos == [] and profile.repo_count is None


@responses.activate
def test_fetch_profile_returns_empty_on_network_error():
    responses.get(URL, body=requests.ConnectionError("boom"))

    assert RestGitHubClient(Settings()).fetch_profile("octocat").repos == []


@responses.activate
def test_custom_api_url_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_API_URL", "https://ghe.example.com/api/v3/")
    responses.get("https://ghe.example.com/api/v3/users/octocat/repos", json=[])

    assert RestGitHubClient(Settings()).fetch_profile("octocat").repo_count == 0
