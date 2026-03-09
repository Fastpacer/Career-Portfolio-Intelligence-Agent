from app.services.groq_service import ask_llm


def analyze_cv(cv_text: str):

    # Reduce token size
    cv_text = cv_text[:3000]

    prompt = f"""
You are an expert technical recruiter evaluating a candidate for AI/ML roles.

Analyze the CV and extract structured insights.

Focus on:
- technical strengths
- missing or weak skills
- project quality
- resume clarity issues

Return concise bullet points under these headings:

Strengths:
Weaknesses:
Missing Skills:
Resume Issues:

CV:
{cv_text}
"""

    return ask_llm(prompt)