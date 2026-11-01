from career_agent.clients.github import GitHubClient, get_github_client
from career_agent.clients.llm import LLMClient, get_llm_client
from career_agent.config import get_settings
from career_agent.core.prompts import CAREER_STRATEGY_V1
from career_agent.logging import logger
from career_agent.schemas import CareerReport, GitHubProfile


def build_prompt(cv_text: str, profile: GitHubProfile, target_role: str) -> str:
    languages_text = (
        ", ".join(f"{lang} ({count} repos)" for lang, count in profile.top_languages.items())
        or "Not enough data"
    )
    repo_text = (
        "\n".join(
            f"{r.name} | {r.language} | ⭐ {r.stars} | {r.description}" for r in profile.repos
        )
        or "No significant repositories found."
    )
    return CAREER_STRATEGY_V1.format(
        cv_text=cv_text,
        repo_count=profile.repo_count,
        total_stars=profile.total_stars,
        languages_text=languages_text,
        repo_text=repo_text,
        target_role=target_role,
    )


def analyze_profile(
    cv_text: str,
    github_username: str,
    target_role: str,
    *,
    llm: LLMClient | None = None,
    github: GitHubClient | None = None,
) -> CareerReport:
    """Run the full analysis. Clients are injectable for tests and alternate providers."""
    llm = llm or get_llm_client()
    github = github or get_github_client()

    logger.info("Starting career analysis for role={!r}", target_role)
    cv_text = cv_text[: get_settings().cv_max_chars]
    profile = github.fetch_profile(github_username)
    prompt = build_prompt(cv_text, profile, target_role)
    return CareerReport(markdown=llm.complete(prompt))
