from pathlib import Path
import json
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import init_db, get_connection
from .parsers import extract_text
from .analyzer import analyze
from .recommender import recommend
from .jobs import JOBS

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Resume Analyzer & Job Recommendation System")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

class JobRequest(BaseModel):
    title: str
    company: str = "Custom Company"
    location: str = "Not specified"
    description: str
    skills: list[str] = []

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/api/jobs")
def get_jobs():
    return JOBS

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Please upload a PDF or DOCX resume.")

    safe_name = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
    path = UPLOAD_DIR / safe_name
    path.write_bytes(await file.read())

    try:
        text = extract_text(str(path))
    except Exception as e:
        raise HTTPException(400, f"Could not read resume: {e}")

    if len(text.strip()) < 30:
        raise HTTPException(400, "The resume contains too little readable text.")

    analysis = analyze(text)
    recommendations = recommend(text, analysis["skills"], JOBS)

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO analyses(filename,resume_text,score,skills,recommendations) VALUES(?,?,?,?,?)",
        (file.filename, text, analysis["score"], json.dumps(analysis["skills"]), json.dumps(recommendations))
    )
    analysis_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": analysis_id,
        "filename": file.filename,
        "analysis": analysis,
        "recommendations": recommendations
    }

@app.post("/api/match-job")
def match_custom_job(payload: JobRequest):
    if not payload.description.strip():
        raise HTTPException(400, "Job description is required.")

    resume_jobs = [payload.model_dump()]
    conn = get_connection()
    row = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    if not row:
        raise HTTPException(400, "Upload a resume first.")

    resume_skills = json.loads(row["skills"])
    results = recommend(row["resume_text"], resume_skills, resume_jobs, 1)
    return results[0]

@app.get("/api/history")
def history():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, filename, score, skills, created_at FROM analyses ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
