"""Versioned prompt templates. Fill with `str.format`; never build prompts inline in stages."""

CAREER_STRATEGY_V1 = """
You are a senior technical recruiter and career advisor.

Evaluate the candidate profile and produce structured career insights.

Candidate CV:
{cv_text}

GitHub Summary

Total repositories: {repo_count}
Total stars: {total_stars}
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
