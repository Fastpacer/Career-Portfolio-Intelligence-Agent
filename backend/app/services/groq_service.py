import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Try loading .env for local development
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

# Try environment variable first
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# If not found, try Streamlit secrets
if not GROQ_API_KEY:
    try:
        import streamlit as st
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "moonshotai/kimi-k2-instruct-0905"
)

client = Groq(api_key=GROQ_API_KEY)


def ask_llm(prompt: str):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1200,
        top_p=0.9
    )

    return response.choices[0].message.content