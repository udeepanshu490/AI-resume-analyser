# AI Resume Analyzer & Job Recommendation System

A runnable full-stack MVP built with FastAPI, SQLite, HTML/CSS/JavaScript, and local NLP-style matching.

## Features
- Upload PDF or DOCX resume
- Extract resume text
- Detect skills, education, experience, projects, and certifications
- Generate a resume score
- Analyze ATS keywords and missing sections
- Match resume against built-in job listings
- Recommend jobs with match percentages
- Show skill gaps for each recommended job
- Add custom job descriptions
- Store uploaded resumes and analyses in SQLite

## Requirements
- Python 3.10+
- pip

## Run on Windows
```powershell
cd AI-Resume-Analyzer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run on macOS/Linux
```bash
cd AI-Resume-Analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000

API documentation:
http://127.0.0.1:8000/docs

No paid AI API key is required for this version. Matching is performed locally with skill extraction and TF-IDF similarity.

## Project structure
```text
AI-Resume-Analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── analyzer.py
│   ├── recommender.py
│   ├── parsers.py
│   └── jobs.py
├── static/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── uploads/
├── requirements.txt
└── README.md
```
