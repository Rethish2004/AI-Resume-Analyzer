"""AI Resume Analyzer Flask API.

Local development backend for registration/login, resume parsing, transparent
keyword-based scoring, history, and PDF report download.

Set SECRET_KEY to a long random value in the environment before deployment.
"""

from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone
from functools import wraps
from io import BytesIO
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# The project already has this parser module. We use it first, then try common
# PDF/DOCX libraries if it cannot extract text.
try:
    from resume_parser import extract_resume_text as project_extract_resume_text
except Exception:  # The fallback parser below can still work without this module.
    project_extract_resume_text = None

try:
    from report_generator import generate_analysis_pdf
except Exception:
    generate_analysis_pdf = None

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("RESUME_ANALYZER_DB", str(BASE_DIR / "resume_analysis.db")))
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # 12 MB maximum upload
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "local-development-only-change-this-secret-before-deployment"
)

# Allow the deployed frontend URL(s) and local development URLs.
# Set FRONTEND_URL on Render to the public frontend origin, for example:
# https://your-frontend-name.onrender.com
frontend_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_URL", "").split(",")
    if origin.strip()
]

frontend_origins.extend([
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
])

CORS(
    app,
    resources={r"/*": {"origins": frontend_origins}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="resume-analyzer-auth")

# Skills are deliberately explicit and explainable. Scores are keyword-based;
# this code does not claim to be a trained semantic ML model.
SKILL_TERMS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis",
    "Flask", "Django", "FastAPI", "REST API", "REST APIs", "API development",
    "Git", "GitHub", "HTML", "CSS", "React", "Node.js", "Express.js",
    ".NET", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
    "Machine Learning", "Deep Learning", "Artificial Intelligence", "NLP",
    "Natural Language Processing", "Pandas", "NumPy", "scikit-learn",
    "TensorFlow", "PyTorch", "Data Analysis", "Data Visualization",
    "Power BI", "Tableau", "Excel", "Statistics", "Data Science",
    "Object-Oriented Programming", "OOP", "Data Structures", "Algorithms",
    "Unit Testing", "Manual Testing", "Automation Testing", "Debugging",
    "Problem Solving", "Communication", "Agile", "CI/CD", "Jenkins",
    "GitLab", "Selenium", "Postman", "Jupyter", "Matplotlib", "Seaborn",
    "Computer Vision", "SQLAlchemy", "Authentication", "Cybersecurity",
]

ROLE_PROFILES = [
    ("AI/ML Engineer", ["machine learning", "deep learning", "artificial intelligence", "tensorflow", "pytorch", "scikit-learn", "nlp"]),
    ("Data Scientist", ["data science", "machine learning", "statistics", "pandas", "numpy", "data analysis"]),
    ("Data Analyst", ["data analysis", "sql", "excel", "power bi", "tableau", "data visualization", "statistics"]),
    ("Python Developer", ["python", "flask", "django", "fastapi", "rest api", "sql"]),
    ("Frontend Developer", ["javascript", "typescript", "react", "html", "css", "frontend"]),
    ("Backend Developer", ["python", "java", "flask", "django", "fastapi", "node.js", "rest api", "sql"]),
    ("Full Stack Developer", ["react", "javascript", "html", "css", "node.js", "rest api", "sql"]),
    ("Software Engineer", ["data structures", "algorithms", "java", "python", "object-oriented programming", "git"]),
    ("QA / Test Engineer", ["testing", "automation testing", "manual testing", "selenium", "postman", "debugging"]),
    ("Cybersecurity Analyst", ["cybersecurity", "penetration testing", "network security", "linux"]),
]

STOP_WORDS = set("""
a an the and or but if then else for to from by with without in on at as is are was were be been being
it its this that these those we you they he she them our your their of into about across over under
will would can could should may might must have has had do does did not no yes all any each more most
such than also using use used work working role job candidate candidate's required requirements
responsibilities responsibility experience years year good strong excellent ability skills skill
including related preferred plus environment team teams company position developer engineer
""".split())

RESUME_SECTION_ALIASES = {
    "Summary / Objective": ["summary", "professional summary", "career objective", "objective", "profile"],
    "Skills": ["skills", "technical skills", "key skills", "core competencies"],
    "Education": ["education", "academic background", "qualification"],
    "Experience": ["experience", "work experience", "employment history", "professional experience", "internship"],
    "Projects": ["projects", "academic projects", "personal projects", "project experience"],
    "Certifications": ["certifications", "certificates", "licenses"],
}

TECH_WORDS = [term for term in SKILL_TERMS if term.lower() not in {"communication", "problem solving"}]
ACTION_WORDS = [
    "developed", "built", "created", "implemented", "designed", "improved",
    "analyzed", "automated", "managed", "tested", "deployed", "optimized",
    "delivered", "led", "collaborated", "integrated", "maintained", "reduced",
    "increased", "resolved", "documented", "configured", "trained",
]


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()}


def ensure_users_table() -> None:
    with db_connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )

        columns = table_columns(conn, "users")
        # Add a compatible password field if an older local table used another
        # layout. Existing data/tables are not dropped.
        if not ("password_hash" in columns or "hashed_password" in columns or "password" in columns):
            conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        columns = table_columns(conn, "users")
        if not ("name" in columns or "full_name" in columns or "username" in columns):
            conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
        if "email" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT")

        conn.execute(
            """CREATE TABLE IF NOT EXISTS api_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resume_score REAL,
                ats_score REAL,
                analysis_json TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )"""
        )
        conn.commit()


ensure_users_table()


def get_user_columns() -> tuple[str, str, str, str]:
    with db_connect() as conn:
        columns = table_columns(conn, "users")
    id_col = next((c for c in ("id", "user_id") if c in columns), None)
    name_col = next((c for c in ("name", "full_name", "username") if c in columns), None)
    email_col = next((c for c in ("email", "email_address") if c in columns), None)
    password_col = next((c for c in ("password_hash", "hashed_password", "password") if c in columns), None)
    if not all((id_col, name_col, email_col, password_col)):
        raise RuntimeError(
            "The existing users table has an unsupported schema. Back up resume_analysis.db "
            "and inspect its users table before continuing."
        )
    return id_col, name_col, email_col, password_col


USER_ID_COL, USER_NAME_COL, USER_EMAIL_COL, USER_PASSWORD_COL = get_user_columns()


def row_to_public_user(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    data = dict(row)
    return {
        "id": data.get(USER_ID_COL),
        "name": data.get(USER_NAME_COL) or "User",
        "email": data.get(USER_EMAIL_COL) or "",
    }


def find_user_by_email(email: str):
    with db_connect() as conn:
        row = conn.execute(
            f'SELECT * FROM users WHERE LOWER("{USER_EMAIL_COL}") = LOWER(?) LIMIT 1',
            (email.strip(),),
        ).fetchone()
        return dict(row) if row else None


def find_user_by_id(user_id: int):
    with db_connect() as conn:
        row = conn.execute(
            f'SELECT * FROM users WHERE "{USER_ID_COL}" = ? LIMIT 1',
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def create_user(name: str, email: str, password: str) -> dict[str, Any]:
    password_hash = generate_password_hash(password)
    columns = [USER_NAME_COL, USER_EMAIL_COL, USER_PASSWORD_COL]
    values: list[Any] = [name.strip(), email.strip().lower(), password_hash]

    with db_connect() as conn:
        try:
            conn.execute(
                f'INSERT INTO users ("{columns[0]}", "{columns[1]}", "{columns[2]}") VALUES (?, ?, ?)',
                values,
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("An account with this email already exists.") from exc

    user = find_user_by_email(email)
    if not user:
        raise RuntimeError("The user was created but could not be loaded.")
    return user


def read_bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return None


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = read_bearer_token()
        if not token:
            return jsonify({"success": False, "error": "Authentication required."}), 401

        try:
            payload = serializer.loads(token, max_age=24 * 60 * 60)
        except (BadSignature, SignatureExpired):
            return jsonify({"success": False, "error": "Invalid or expired login token. Please log in again."}), 401

        try:
            user = find_user_by_id(int(payload.get("user_id")))
        except (TypeError, ValueError):
            user = None

        if not user:
            return jsonify({"success": False, "error": "User account was not found. Please log in again."}), 401

        request.current_user = row_to_public_user(user)
        return function(*args, **kwargs)

    return wrapper


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_text_from_file(filepath: Path, extension: str) -> str:
    """Extract text via this project's parser, with common parser fallbacks."""
    if extension == ".txt":
        return filepath.read_text(encoding="utf-8", errors="ignore")

    if project_extract_resume_text is not None:
        try:
            extracted = project_extract_resume_text(str(filepath))
            if extracted and str(extracted).strip():
                return str(extracted)
        except Exception:
            app.logger.exception("Project resume_parser extraction failed; trying fallback parser")

    if extension == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(filepath))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(filepath))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError as exc:
                raise RuntimeError("Install pypdf using: python -m pip install pypdf") from exc

    if extension == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Install python-docx using: python -m pip install python-docx") from exc
        document = Document(str(filepath))
        return "\n".join(p.text for p in document.paragraphs)

    return ""


def term_present(text_lower: str, term: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text_lower, flags=re.IGNORECASE) is not None


def detect_terms(text: str, terms: list[str]) -> list[str]:
    lower = (text or "").lower()
    # Prefer longer phrases before abbreviations, then restore list order by
    # iterating over a length-sorted copy so that phrase hits are consistent.
    ordered = sorted(set(terms), key=len, reverse=True)
    found = [term for term in ordered if term_present(lower, term)]
    return found


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", (text or "").lower())
    return [token.strip(".-") for token in tokens if token.strip(".-") and token not in STOP_WORDS and len(token.strip(".-")) > 1]


def cosine_similarity_percent(text_a: str, text_b: str) -> int:
    a = Counter(tokenize(text_a))
    b = Counter(tokenize(text_b))
    if not a or not b:
        return 0
    common = set(a) & set(b)
    dot = sum(a[token] * b[token] for token in common)
    magnitude_a = math.sqrt(sum(value * value for value in a.values()))
    magnitude_b = math.sqrt(sum(value * value for value in b.values()))
    if not magnitude_a or not magnitude_b:
        return 0
    return max(0, min(100, round((dot / (magnitude_a * magnitude_b)) * 100)))


def job_keywords(job_description: str) -> list[str]:
    tokens = tokenize(job_description)
    # Maintain the original order and remove duplicates.
    unique = list(dict.fromkeys(tokens))
    return unique[:80]


def detect_role(job_description: str) -> tuple[str, list[str]]:
    jd = (job_description or "").lower()
    best_role = "Not detected"
    best_terms: list[str] = []
    best_count = 0

    for role, role_terms in ROLE_PROFILES:
        count = sum(1 for term in role_terms if term_present(jd, term))
        if count > best_count:
            best_role = role
            best_terms = role_terms
            best_count = count

    if best_count == 0:
        # Generic role phrases from a job description can still provide a role.
        if "developer" in jd:
            best_role = "Software Developer"
        elif "engineer" in jd:
            best_role = "Software Engineer"

    return best_role, best_terms


def find_resume_sections(resume_text: str) -> tuple[list[str], list[str]]:
    lower = (resume_text or "").lower()
    found: list[str] = []
    missing: list[str] = []

    for canonical, aliases in RESUME_SECTION_ALIASES.items():
        if any(alias in lower for alias in aliases):
            found.append(canonical)
        else:
            missing.append(canonical)
    return found, missing


def make_suggestions(
    missing_skills: list[str],
    missing_sections: list[str],
    resume_text: str,
    email: str | None,
    phone: str | None,
    project_quality: dict[str, list[str]],
) -> list[str]:
    suggestions: list[str] = []

    if missing_skills:
        suggestions.append(
            "If you genuinely have them, add relevant job skills such as: "
            + ", ".join(missing_skills[:10]) + "."
        )
    if missing_sections:
        suggestions.append(
            "Consider adding relevant resume sections where applicable: "
            + ", ".join(missing_sections) + "."
        )
    if not email:
        suggestions.append("Add a professional email address to your contact section.")
    if not phone:
        suggestions.append("Add a current phone number if you want recruiters to contact you by phone.")
    if not project_quality["action_words"]:
        suggestions.append("Start project bullets with clear action verbs such as Developed, Implemented, Tested, or Automated.")
    if not project_quality["numbers_results"]:
        suggestions.append("Where accurate, include measurable project outcomes, test counts, performance changes, or other verifiable results.")
    if len((resume_text or "").split()) < 120:
        suggestions.append("Your extracted resume text is relatively short. Check that the whole resume was uploaded and parsed correctly.")
    if not suggestions:
        suggestions.append("Keep tailoring your resume to each job description and ensure that all stated skills and results are accurate.")
    return suggestions


def build_analysis(resume_text: str, job_description: str, filename: str, user: dict[str, Any]) -> dict[str, Any]:
    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    resume_skills = detect_terms(resume_text, SKILL_TERMS)
    required_skills = detect_terms(job_description, SKILL_TERMS)
    matched_skills = [skill for skill in required_skills if term_present(resume_lower, skill)]
    missing_skills = [skill for skill in required_skills if skill not in matched_skills]

    skill_match = round(100 * len(matched_skills) / len(required_skills)) if required_skills else 0
    similarity_score = cosine_similarity_percent(resume_text, job_description)

    jd_keywords = job_keywords(job_description)
    resume_tokens = set(tokenize(resume_text))
    matched_keywords = [keyword for keyword in jd_keywords if keyword in resume_tokens]
    missing_keywords = [keyword for keyword in jd_keywords if keyword not in resume_tokens]
    total_keywords = len(jd_keywords)
    keyword_coverage = (len(matched_keywords) / total_keywords * 100) if total_keywords else 0

    role, role_terms = detect_role(job_description)
    role_keywords = [term for term in role_terms if term_present(job_lower, term)]
    matched_role_keywords = [term for term in role_keywords if term_present(resume_lower, term)]
    role_keyword_match = round(100 * len(matched_role_keywords) / len(role_keywords)) if role_keywords else 0

    found_sections, missing_sections = find_resume_sections(resume_text)
    section_score = (len(found_sections) / len(RESUME_SECTION_ALIASES)) * 100
    ats_score = round((0.80 * keyword_coverage) + (0.20 * section_score))

    # Transparent weighted mean: 30% text similarity, 30% job skill coverage,
    # 25% ATS keyword/section coverage, 15% role-specific keyword coverage.
    resume_score = round(
        0.30 * similarity_score
        + 0.30 * skill_match
        + 0.25 * ats_score
        + 0.15 * role_keyword_match
    )

    email_match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text, re.IGNORECASE)
    phone_match = re.search(r"(?:\+?\d[\d ().-]{7,}\d)", resume_text)
    resume_email = email_match.group(0) if email_match else None
    phone_number = phone_match.group(0).strip() if phone_match else None

    detected_tech = detect_terms(resume_text, TECH_WORDS)
    lower_resume = resume_text.lower()
    detected_actions = [word.title() for word in ACTION_WORDS if term_present(lower_resume, word)]
    numeric_results = re.findall(
        r"\b\d+(?:\.\d+)?\s*(?:%|percent|users|records|projects|tests|seconds|minutes|hours|days|weeks|months|years|ms|gb|mb)\b|\b(?:improved|increased|reduced|decreased|saved)\s+\w+(?:\s+\w+){0,3}\s+by\s+\d+(?:\.\d+)?%?",
        resume_text,
        flags=re.IGNORECASE,
    )

    project_quality = {
        "technology_words": detected_tech,
        "action_words": detected_actions,
        "numbers_results": numeric_results,
    }

    suggestions = make_suggestions(
        missing_skills,
        missing_sections,
        resume_text,
        resume_email,
        phone_number,
        project_quality,
    )

    word_count = len(re.findall(r"\b\w+(?:[+#.-]\w+)*\b", resume_text))

    analysis: dict[str, Any] = {
        "success": True,
        "filename": filename,
        "resume_name": filename,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]},
        "detected_job_role": role,
        "job_role": role,
        "predicted_role": role,
        "resume_score": resume_score,
        "overall_match_score": resume_score,
        "match_score": resume_score,
        "similarity_score": similarity_score,
        "job_similarity": similarity_score,
        "job_similarity_score": similarity_score,
        "skill_match": skill_match,
        "skill_match_score": skill_match,
        "role_keyword_match": role_keyword_match,
        "role_keyword_match_score": role_keyword_match,
        "ats_score": ats_score,
        "ats_percentage": ats_score,
        "word_count": word_count,
        "resume_word_count": word_count,
        "resume_skills": resume_skills,
        "detected_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_keywords": total_keywords,
        "matched_keywords_count": len(matched_keywords),
        "missing_keywords_count": len(missing_keywords),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_ats_keywords": matched_keywords,
        "missing_ats_keywords": missing_keywords,
        "detected_role_keywords": role_keywords,
        "matched_role_keywords": matched_role_keywords,
        "found_sections": found_sections,
        "missing_sections": missing_sections,
        "resume_email": resume_email,
        "phone_number": phone_number,
        "technology_words": detected_tech,
        "action_words": detected_actions,
        "numbers_results": numeric_results,
        "project_quality": project_quality,
        "suggestions": suggestions,
        "improvement_suggestions": suggestions,
        "ats_analysis": {
            "ats_score": ats_score,
            "total_keywords": total_keywords,
            "matched_keywords_count": len(matched_keywords),
            "missing_keywords_count": len(missing_keywords),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "keyword_coverage_percentage": round(keyword_coverage),
            "section_coverage_percentage": round(section_score),
        },
        "scoring_method": {
            "type": "transparent keyword-based heuristic; not a trained ML prediction",
            "resume_match_weights": {
                "job_similarity_percent": 30,
                "skill_match_percent": 30,
                "ats_score_percent": 25,
                "role_keyword_match_percent": 15,
            },
        },
    }
    return analysis


@app.get("/")
def home():
    return jsonify({
        "success": True,
        "message": "AI Resume Analyzer API is running.",
        "endpoints": ["/health", "/register", "/login", "/me", "/analyze", "/history", "/download-report"],
    })


@app.get("/health")
def health():
    return jsonify({"status": "OK", "success": True})


@app.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not name or not email or not password:
        return jsonify({"success": False, "error": "Name, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must contain at least 6 characters."}), 400
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"success": False, "error": "Enter a valid email address."}), 400

    try:
        user_row = create_user(name, email, password)
        public_user = row_to_public_user(user_row)
        return jsonify({"success": True, "message": "Account created successfully.", "user": public_user}), 201
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 409
    except Exception:
        app.logger.exception("Registration failed")
        return jsonify({"success": False, "error": "Registration failed. Check the backend terminal."}), 500


@app.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user_row = find_user_by_email(email)
    if not user_row:
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    stored_hash = user_row.get(USER_PASSWORD_COL)
    try:
        valid = bool(stored_hash) and check_password_hash(stored_hash, password)
    except (ValueError, TypeError):
        valid = False

    if not valid:
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    user = row_to_public_user(user_row)
    token = serializer.dumps({"user_id": user["id"], "email": user["email"]})
    return jsonify({"success": True, "message": "Login successful.", "token": token, "user": user})


@app.get("/me")
@login_required
def me():
    return jsonify({"success": True, "user": request.current_user})


@app.post("/analyze")
@login_required
def analyze_resume_route():
    user = request.current_user

    if "resume" not in request.files:
        return jsonify({"success": False, "error": "Resume file is required."}), 400

    resume_file = request.files["resume"]
    if not resume_file or not resume_file.filename:
        return jsonify({"success": False, "error": "Please select a resume file."}), 400

    safe_name = secure_filename(resume_file.filename)
    extension = Path(safe_name).suffix.lower()
    if extension not in {".pdf", ".docx", ".txt"}:
        return jsonify({"success": False, "error": "Supported file types are PDF, DOCX, and TXT."}), 400

    job_description = normalize_text(
        request.form.get("job_description")
        or request.form.get("jobDescription")
        or ""
    )
    if not job_description:
        return jsonify({"success": False, "error": "Job description is required."}), 400

    filepath = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    try:
        resume_file.save(filepath)
        text = extract_text_from_file(filepath, extension)
        if not text or not text.strip():
            return jsonify({
                "success": False,
                "error": "No selectable text was extracted from the resume. If this is a scanned PDF, run OCR or upload a text-based PDF/DOCX.",
            }), 400

        analysis = build_analysis(text, job_description, safe_name, user)
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        with db_connect() as conn:
            cursor = conn.execute(
                """INSERT INTO api_analyses
                   (user_id, filename, created_at, resume_score, ats_score, analysis_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    user["id"],
                    safe_name,
                    created_at,
                    analysis["resume_score"],
                    analysis["ats_score"],
                    "{}",
                ),
            )
            analysis_id = cursor.lastrowid
            analysis["analysis_id"] = analysis_id
            analysis["created_at"] = created_at
            conn.execute(
                "UPDATE api_analyses SET analysis_json = ? WHERE id = ?",
                (json.dumps(analysis, ensure_ascii=False), analysis_id),
            )
            conn.commit()

        return jsonify(analysis)
    except RuntimeError as exc:
        app.logger.exception("Resume extraction dependency error")
        return jsonify({"success": False, "error": str(exc)}), 500
    except Exception:
        app.logger.exception("Resume analysis failed")
        return jsonify({"success": False, "error": "Resume analysis failed. Check the backend terminal for the full traceback."}), 500
    finally:
        try:
            filepath.unlink(missing_ok=True)
        except Exception:
            pass


@app.get("/history")
@login_required
def history():
    user = request.current_user
    with db_connect() as conn:
        rows = conn.execute(
            """SELECT id, filename, created_at, resume_score, ats_score, analysis_json
               FROM api_analyses WHERE user_id = ? ORDER BY id DESC LIMIT 100""",
            (user["id"],),
        ).fetchall()

    entries = []
    for row in rows:
        try:
            saved_analysis = json.loads(row["analysis_json"] or "{}")
        except (json.JSONDecodeError, TypeError):
            saved_analysis = {}

        entries.append({
            "id": row["id"],
            "analysis_id": row["id"],
            "filename": row["filename"],
            "created_at": row["created_at"],
            "resume_score": row["resume_score"],
            "match_score": row["resume_score"],
            "ats_score": row["ats_score"],
            "analysis": saved_analysis,
        })

    return jsonify({"success": True, "history": entries})


@app.post("/download-report")
@login_required
def download_report():
    payload = request.get_json(silent=True) or {}
    analysis = payload.get("analysis")

    if not isinstance(analysis, dict) or not analysis:
        return jsonify({"success": False, "error": "Analysis data is required. Analyze a resume before downloading the report."}), 400

    if generate_analysis_pdf is None:
        return jsonify({
            "success": False,
            "error": "PDF module is unavailable. Ensure report_generator.py defines generate_analysis_pdf and install reportlab.",
        }), 500

    try:
        pdf_bytes = generate_analysis_pdf(analysis)
        if not isinstance(pdf_bytes, (bytes, bytearray)):
            raise TypeError("generate_analysis_pdf must return PDF bytes")

        return send_file(
            BytesIO(bytes(pdf_bytes)),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="resume-analysis-report.pdf",
        )
    except Exception:
        app.logger.exception("PDF report generation failed")
        return jsonify({"success": False, "error": "PDF generation failed. Check the backend terminal."}), 500


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"success": False, "error": "The uploaded file is too large. Maximum size is 12 MB."}), 413


if __name__ == "__main__":
    print("AI Resume Analyzer API is starting...")
    print("Health check: http://127.0.0.1:5000/health")
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)