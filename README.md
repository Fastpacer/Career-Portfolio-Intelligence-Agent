# Career Portfolio Intelligence Agent

An AI-powered career analysis tool that evaluates a candidate’s **CV, GitHub portfolio, and target role** to generate actionable career improvement insights.

The system uses a **FastAPI backend + LLM reasoning + Streamlit UI** to produce a structured career strategy report including skill gaps, portfolio feedback, resume improvements, and a 30-day learning roadmap.

---

## Features

- CV analysis from uploaded **PDF resumes**
- GitHub portfolio evaluation
- Role-agnostic career recommendations
- Structured career strategy output
- Automated learning roadmap
- Clean Streamlit dashboard interface

---

## Architecture
# Career Portfolio Intelligence Agent

An AI-powered career analysis tool that evaluates a candidate’s **CV, GitHub portfolio, and target role** to generate actionable career improvement insights.

The system uses a **FastAPI backend + LLM reasoning + Streamlit UI** to produce a structured career strategy report including skill gaps, portfolio feedback, resume improvements, and a 30-day learning roadmap.

---

## Features

- CV analysis from uploaded **PDF resumes**
- GitHub portfolio evaluation
- Role-agnostic career recommendations
- Structured career strategy output
- Automated learning roadmap
- Clean Streamlit dashboard interface

---

## Architecture
Streamlit UI
│
│ POST /analyze
▼
FastAPI Backend
│
├── CV Analysis
├── GitHub Portfolio Analysis
└── Career Strategy Agent
│
▼
LLM (Groq / Moonshot)


---

## Project Structure


career_intelligence_agent
│
├── backend
│ └── app
│ ├── agents
│ │ └── career_agent.py
│ ├── services
│ │ ├── groq_service.py
│ │ └── github_service.py
│ ├── models
│ ├── utils
│ └── main.py
│
├── streamlit_app
│ └── app.py
│
├── .gitignore
├── README.md
└── requirements.txt


---

## Setup

### 1️⃣ Clone the repository


git clone https://github.com/your-username/career-intelligence-agent.git

cd career-intelligence-agent


---

### 2️⃣ Create a virtual environment


python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate


---

### 3️⃣ Install dependencies


pip install -r requirements.txt


---

### 4️⃣ Configure environment variables

Create a `.env` file in the **backend folder**.

Example:


GROQ_API_KEY=your_api_key_here
MODEL_NAME=moonshot
GITHUB_API_URL=https://api.github.com


---

## Running the Application

### Start the backend


cd backend
uvicorn app.main:app --reload


Backend will run at:


http://127.0.0.1:8000


---

### Start the Streamlit UI

Open another terminal:


cd streamlit_app
streamlit run app.py


Streamlit UI will run at:


http://localhost:8501


---

## Example Workflow

1. Upload a CV PDF
2. Enter GitHub username
3. Enter target role
4. Click **Analyze Profile**

The AI agent generates:

- Skill gap analysis
- Portfolio improvement suggestions
- Resume feedback
- 30-day learning roadmap

---

## Tech Stack

- **FastAPI** – backend API
- **Streamlit** – UI dashboard
- **Groq / Moonshot LLM** – reasoning engine
- **GitHub API** – portfolio analysis
- **pdfplumber** – CV parsing

---

## Future Improvements

- deeper GitHub repository analysis (README + code signals)
- skill extraction from CV
- project difficulty scoring
- interactive learning roadmap tracking

---

## License

MIT License
