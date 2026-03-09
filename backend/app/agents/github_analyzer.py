from app.services.github_service import fetch_repositories
from app.services.groq_service import ask_llm


def analyze_github(username: str):

    repos = fetch_repositories(username)

    repo_summary = []

    for repo in repos[:5]:
        repo_summary.append(
            f"{repo['name']} - {repo['description']}"
        )

    prompt = f"""
    Analyze these GitHub projects and evaluate portfolio quality.

    Projects:
    {repo_summary}

    Provide:
    - strengths
    - weaknesses
    - improvements
    """

    return ask_llm(prompt)