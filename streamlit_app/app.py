"""Streamlit adapter over `career_agent.core`.

Run from the repo root: `streamlit run streamlit_app/app.py`.
"""

import os

import streamlit as st

from career_agent.clients.llm import LLMConfigError
from career_agent.core.pipeline import analyze_profile
from career_agent.logging import configure_logging, logger
from career_agent.parsing.cv import extract_cv_text


def _export_secrets_to_env() -> None:
    """Expose top-level st.secrets as env vars so `career_agent.config` stays Streamlit-agnostic."""
    try:
        secrets = dict(st.secrets)
    except Exception:  # no secrets.toml locally
        return
    for key, value in secrets.items():
        if isinstance(value, str | int | float | bool):
            os.environ.setdefault(key.upper(), str(value))


_export_secrets_to_env()
configure_logging()

st.set_page_config(page_title="Career Portfolio Intelligence Agent", layout="wide")

st.title("Career Portfolio Intelligence Agent")
st.caption("Role-agnostic AI career advisor powered by LLM-based profile analysis.")
st.markdown(
    """
Upload your CV and evaluate how well your profile aligns with your target role.

The system analyzes your **experience, skills, GitHub projects, and resume structure**
to identify improvement opportunities and generate actionable career guidance.
"""
)

st.sidebar.header("Profile Inputs")
uploaded_file = st.sidebar.file_uploader("Upload CV (PDF)", type=["pdf"])
github_username = st.sidebar.text_input("GitHub Username")
target_role = st.sidebar.text_input("Target Role", value="Software Engineer")
analyze_button = st.sidebar.button("Analyze Profile")

if analyze_button:
    if uploaded_file is None:
        st.error("Please upload a CV PDF")
    elif github_username.strip() == "":
        st.error("Please enter your GitHub username")
    else:
        with st.spinner("Analyzing your career profile..."):
            try:
                cv_text = extract_cv_text(uploaded_file)
                report = analyze_profile(
                    cv_text=cv_text,
                    github_username=github_username.strip(),
                    target_role=target_role,
                )
                st.success("Analysis complete")
                st.markdown("## Career Strategy Report")
                st.markdown(report.markdown)
            except LLMConfigError:
                logger.error("GROQ_API_KEY missing")
                st.error(
                    "The AI backend isn't configured: `GROQ_API_KEY` is missing. "
                    "Set it in `.env` at the project root (see `.env.example`) or in "
                    "Streamlit Secrets, then rerun."
                )
            except Exception as e:
                # TODO(Phase 2, I-11): typed errors with friendly messages; don't show tracebacks.
                logger.exception("Analysis failed")
                st.error("An error occurred during analysis.")
                st.exception(e)
