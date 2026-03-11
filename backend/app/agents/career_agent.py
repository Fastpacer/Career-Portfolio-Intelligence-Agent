from app.services.github_service import fetch_repositories
from app.services.groq_service import ask_llm


def generate_career_strategy(cv_text, github_username, target_role):

    # Limit CV size to control token usage
    cv_text = cv_text[:3500]

    github_data = fetch_repositories(github_username)

    repos = github_data.get("repos", [])
    summary = github_data.get("summary", {})

    # Convert language stats into readable format
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

Your task is to evaluate a candidate's profile and provide both **scores and career improvement insights**.

The evaluation should consider:

• CV quality and structure  
• skill alignment with the target role  
• GitHub portfolio strength  
• project relevance and complexity  

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

Provide output using the following structure.

## Career Profile Scores

ATS Readiness Score: <0-100>

Portfolio Strength Score: <0-100>

Skill Alignment Score: <0-100>

Overall Career Readiness Score: <0-100>

Briefly explain why these scores were assigned.

--------------------------------

## 1. Skill Gaps

Identify missing or weak skills for the target role.

For each skill explain briefly:
- why the skill matters
- how the candidate could learn or demonstrate it

--------------------------------

## 2. Portfolio Improvements

Evaluate the GitHub projects and suggest improvements such as:

- stronger project types
- missing technologies
- improving documentation
- demonstrating real-world impact
- improving code quality

--------------------------------

## 3. Resume Improvements

Suggest concrete improvements for:

- resume structure
- clarity of experience
- measurable achievements
- missing sections
- highlighting important projects

--------------------------------

## 4. 30-Day Learning Roadmap

Provide a structured **4-week roadmap** using this exact format:

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

Guidelines:

- Avoid tables
- Keep answers concise but insightful
- Ensure all sections are completed
"""

    return ask_llm(prompt)