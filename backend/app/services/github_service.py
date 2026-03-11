from backend.app.services.github_service import fetch_repositories
from backend.app.services.groq_service import ask_llm


def generate_career_strategy(cv_text, github_username, target_role):

    cv_text = cv_text[:3500]

    github_data = fetch_repositories(github_username)

    repos = github_data.get("repos", [])
    summary = github_data.get("summary", {})

    languages_dict = summary.get("top_languages", {})

    languages_text = ", ".join(
        [f"{lang} ({count} repos)" for lang, count in languages_dict.items()]
    )

    if not languages_text:
        languages_text = "Not enough data"

    repo_summary = []

    for repo in repos:
        repo_summary.append(
            f"{repo.get('name')} | {repo.get('language')} | ⭐ {repo.get('stars')} | {repo.get('description')}"
        )

    repo_text = "\n".join(repo_summary)

    if not repo_text:
        repo_text = "No significant repositories found."

    prompt = f"""
You are a senior technical recruiter and career advisor.

Evaluate the candidate profile and produce structured career insights.

Candidate CV:
{cv_text}

GitHub Summary

Total repositories: {summary.get("repo_count")}
Total stars: {summary.get("total_stars")}
Top languages: {languages_text}

Projects:
{repo_text}

Target Role:
{target_role}

Provide the following sections.

## Career Profile Scores

ATS Readiness Score: <0-100>
Portfolio Strength Score: <0-100>
Skill Alignment Score: <0-100>
Overall Career Readiness Score: <0-100>

Explain briefly why these scores were assigned.

## 1. Skill Gaps

List missing or weak skills and why they matter.

## 2. Portfolio Improvements

Suggest improvements to GitHub projects.

## 3. Resume Improvements

Provide actionable resume improvements.

## 4. 30-Day Learning Roadmap

Week 1
Focus:
Actions:
- action
- action
- action

Week 2
Focus:
Actions:
- action
- action
- action

Week 3
Focus:
Actions:
- action
- action
- action

Week 4
Focus:
Actions:
- action
- action
- action
"""

    return ask_llm(prompt)