from app.services.github_service import fetch_repositories
from app.services.groq_service import ask_llm


def generate_career_strategy(cv_text, github_username, target_role):

    # Slightly smaller CV slice to free tokens for generation
    cv_text = cv_text[:3000]

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
You are a **senior technical recruiter and career advisor**.

Evaluate the candidate's **skills, projects, and resume quality**
relative to their **target role**.

Think like an experienced recruiter evaluating a candidate for hiring.

--------------------------------

Candidate CV:
{cv_text}

--------------------------------

GitHub Portfolio Summary

Total repositories: {summary.get("repo_count")}
Total stars: {summary.get("total_stars")}
Top languages used: {languages_text}

Highlighted Projects:
{repo_text}

--------------------------------

Target Role:
{target_role}

--------------------------------

Your task is to produce a structured evaluation.

IMPORTANT RULES:

- All 4 sections must be present.
- Keep responses concise but insightful.
- Maximum 5 bullet points per section.
- Avoid tables.
- Use bullet points where possible.

--------------------------------

## 1. Skill Gaps

Identify missing or weak skills for the target role.

For each skill explain briefly:
- why the skill matters
- how the candidate could learn or demonstrate it

--------------------------------

## 2. Portfolio Improvements

Evaluate the GitHub projects.

Focus specifically on:

- project diversity
- real-world usefulness
- code quality signals
- missing project types
- documentation quality

--------------------------------

## 3. Resume Improvements

Suggest improvements related to:

- structure
- clarity
- measurable achievements
- missing sections
- highlighting strongest projects

--------------------------------

## 4. 30-Day Learning Roadmap

Provide a structured **4-week roadmap**.

Use this exact format:

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

--------------------------------

Ensure all four sections are completed before finishing the answer.
"""

    return ask_llm(prompt)