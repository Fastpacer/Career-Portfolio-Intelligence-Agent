from career_agent.core.pipeline import analyze_profile, build_prompt
from career_agent.schemas import GitHubProfile


def test_analyze_profile_returns_llm_markdown(fake_llm, fake_github):
    report = analyze_profile("cv", "octocat", "Data Engineer", llm=fake_llm, github=fake_github)

    assert report.markdown == fake_llm.reply
    assert fake_github.usernames == ["octocat"]
    prompt = fake_llm.prompts[0]
    assert "Data Engineer" in prompt
    assert "proj | Python | ⭐ 3 | A project" in prompt
    assert "Python (1 repos)" in prompt


def test_cv_is_truncated_to_configured_limit(fake_llm, fake_github, monkeypatch):
    monkeypatch.setenv("CV_MAX_CHARS", "10")
    analyze_profile("A" * 10 + "B" * 50, "u", "r", llm=fake_llm, github=fake_github)

    assert "A" * 10 in fake_llm.prompts[0]
    assert "B" not in fake_llm.prompts[0].split("Candidate CV:")[1].split("GitHub Summary")[0]


def test_build_prompt_handles_empty_github_profile():
    prompt = build_prompt("cv", GitHubProfile(), "SWE")

    assert "No significant repositories found." in prompt
    assert "Not enough data" in prompt
