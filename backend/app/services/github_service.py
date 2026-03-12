import requests
import os
from collections import Counter
from backend.app.utils.logger import get_logger

logger = get_logger()

GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")


def fetch_repositories(username: str):

    url = f"{GITHUB_API_URL}/users/{username}/repos"

    logger.info(f"Fetching repos for {username}")

    try:
        response = requests.get(url)

        if response.status_code != 200:
            logger.error("GitHub API request failed")
            return {"repos": [], "summary": {}}

        repos = response.json()

    except Exception as e:
        logger.error(f"GitHub request error: {e}")
        return {"repos": [], "summary": {}}

    repos_sorted = sorted(
        repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True
    )

    top_repos = repos_sorted[:5]

    processed_repos = []
    languages = []
    total_stars = 0

    for repo in top_repos:

        language = repo.get("language")

        if language:
            languages.append(language)

        stars = repo.get("stargazers_count", 0)
        total_stars += stars

        processed_repos.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": stars,
            "language": language,
            "updated_at": repo.get("updated_at")
        })

    language_counter = Counter(languages)

    summary = {
        "repo_count": len(repos),
        "top_languages": dict(language_counter.most_common(3)),
        "total_stars": total_stars
    }

    return {
        "repos": processed_repos,
        "summary": summary
    }