import streamlit as st
import pdfplumber
import requests

API_URL = "http://127.0.0.1:8000/analyze"

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

    elif github_username == "":
        st.error("Please enter your GitHub username")

    else:

        with st.spinner("Analyzing your career profile..."):

            cv_text = extract_cv_text(uploaded_file)

            payload = {
                "cv_text": cv_text,
                "github_username": github_username,
                "target_role": target_role
            }

            response = requests.post(API_URL, json=payload)

            if response.status_code != 200:
                st.error("Backend error occurred")
            else:

                data = response.json()

                result = data["career_strategy"]

                st.markdown("## Career Strategy Report")

                st.markdown(result)