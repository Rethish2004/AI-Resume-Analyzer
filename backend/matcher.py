import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


JOB_SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "html",
    "css",
    "javascript",
    "react",
    "django",
    "flask",
    "fastapi",
    "rest api",
    "git",
    "github",
    "aws",
    "azure",
    "machine learning",
    "data analysis",
    "excel",
    "powerpoint",
    "problem solving",
    "communication",
    "team collaboration"
]


def clean_text(text):
    """Convert text into a simple searchable format."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_skills(text):
    """Find skills mentioned in the given text."""
    text = clean_text(text)

    found = []

    for skill in JOB_SKILLS:
        if skill in text:
            found.append(skill)

    return sorted(set(found))


def calculate_similarity(resume_text, job_description):
    """Calculate resume and job description similarity."""
    documents = [
        clean_text(resume_text),
        clean_text(job_description)
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

    return round(similarity * 100, 2)


def analyze_job_match(resume_text, job_description):
    """Compare resume with job description."""

    resume_skills = find_skills(resume_text)
    required_skills = find_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    if required_skills:
        skill_match = (
            len(matched_skills) / len(required_skills)
        ) * 100
    else:
        skill_match = 0

    return {
        "similarity_score": similarity_score,
        "skill_match": round(skill_match, 2),
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }