import streamlit as st
import pdfplumber
import sys
import os

# Allow Streamlit to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.agents.career_agent import generate_career_strategy

st.set_page_config(
    page_title="Career Portfolio Intelligence Agent",
    layout="wide"
)

st.title("Career Portfolio Intelligence Agent")

st.caption("Role-agnostic AI career advisor powered by LLM-based profile analysis.")

st.markdown(
"""
Upload your CV and evaluate how well your profile aligns with your target role.

The system analyzes your **experience, skills, GitHub projects, and resume structure**
to identify improvement opportunities and generate actionable career guidance.
"""
)

# Sidebar inputs
st.sidebar.header("Profile Inputs")

uploaded_file = st.sidebar.file_uploader(
    "Upload CV (PDF)",
    type=["pdf"]
)

github_username = st.sidebar.text_input(
    "GitHub Username"
)

target_role = st.sidebar.text_input(
    "Target Role",
    value="Software Engineer"
)

analyze_button = st.sidebar.button("Analyze Profile")


def extract_cv_text(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

    return text


if analyze_button:

    if uploaded_file is None:
        st.error("Please upload a CV PDF")

    elif github_username.strip() == "":
        st.error("Please enter your GitHub username")

    else:

        with st.spinner("Analyzing your career profile..."):

            try:

                cv_text = extract_cv_text(uploaded_file)

                result = generate_career_strategy(
                    cv_text=cv_text,
                    github_username=github_username,
                    target_role=target_role
                )

                st.success("Analysis complete")

                st.markdown("## Career Strategy Report")

                st.markdown(result)

            except Exception as e:

                st.error("An error occurred during analysis.")
                st.exception(e)