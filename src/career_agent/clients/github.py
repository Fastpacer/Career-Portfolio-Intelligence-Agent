"""GitHub portfolio fetch.

Behaviour intentionally matches the pre-refactor service (first page only, stats
over the top 5 repos, failures return an empty profile). Phase 2 fixes these (I-7).
"""

from collections import Counter
from functools import lru_cache
from typing import Protocol

import requests

from career_agent.config import Settings, get_settings
from career_agent.logging import logger
from career_agent.schemas import GitHubProfile, RepoSummary

TOP_N_REPOS = 5


class GitHubClient(Protocol):
    def fetch_profile(self, username: str) -> GitHubProfile: ...


class RestGitHubClient:
    def __init__(self, settings: Settings):
        self._base_url = settings.github_api_url.rstrip("/")
        self._timeout = settings.github_timeout_seconds

    def fetch_profile(self, username: str) -> GitHubProfile:
        url = f"{self._base_url}/users/{username}/repos"
        logger.info("Fetching repos for {}", username)
        try:
            response = requests.get(url, timeout=self._timeout)
            if response.status_code != 200:
                logger.error("GitHub API request failed with status {}", response.status_code)
                return GitHubProfile()
            repos = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("GitHub request error: {}", exc)
            return GitHubProfile()

        top = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:TOP_N_REPOS]
        summaries = [
            RepoSummary(
                name=r.get("name"),
                description=r.get("description"),
                stars=r.get("stargazers_count", 0),
                language=r.get("language"),
                updated_at=r.get("updated_at"),
            )
            for r in top
        ]
        languages = Counter(s.language for s in summaries if s.language)
        return GitHubProfile(
            repos=summaries,
            repo_count=len(repos),
            total_stars=sum(s.stars for s in summaries),
            top_languages=dict(languages.most_common(3)),
        )


@lru_cache
def get_github_client() -> GitHubClient:
    return RestGitHubClient(get_settings())
