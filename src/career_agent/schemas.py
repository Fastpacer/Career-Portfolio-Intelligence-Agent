from pydantic import BaseModel


class CareerRequest(BaseModel):
    cv_text: str
    github_username: str
    target_role: str


class RepoSummary(BaseModel):
    name: str | None = None
    description: str | None = None
    stars: int = 0
    language: str | None = None
    updated_at: str | None = None


class GitHubProfile(BaseModel):
    repos: list[RepoSummary] = []
    repo_count: int | None = None
    total_stars: int | None = None
    top_languages: dict[str, int] = {}


class CareerReport(BaseModel):
    """Analysis result. Phase 2 replaces free-form markdown with typed sections and scores."""

    markdown: str
