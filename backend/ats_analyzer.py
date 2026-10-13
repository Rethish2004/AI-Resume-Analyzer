import re


# ==========================================
# IMPORTANT ATS / JOB KEYWORDS
# ==========================================

COMMON_KEYWORDS = [
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
    "node.js",

    "flask",
    "django",
    "fastapi",

    "rest api",
    "api",

    "git",
    "github",

    "aws",
    "azure",

    "machine learning",
    "deep learning",

    "pandas",
    "numpy",
    "scikit-learn",

    "data analysis",
    "data analytics",
    "business analytics",

    "excel",
    "power bi",
    "tableau",

    "testing",
    "manual testing",
    "automation testing",
    "selenium",

    "communication",
    "problem solving",
    "team collaboration",
]


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):
    """
    Convert text into lowercase searchable text.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# EXTRACT KEYWORDS
# ==========================================

def extract_keywords(job_description):
    """
    Find important technical and professional
    keywords in the job description.
    """

    text = clean_text(
        job_description
    )

    found_keywords = []

    for keyword in COMMON_KEYWORDS:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text
        ):
            found_keywords.append(
                keyword
            )

    return found_keywords


# ==========================================
# NORMALIZE KEYWORD DISPLAY
# ==========================================

def normalize_keyword(keyword):

    keyword_map = {

        "python": "Python",

        "java": "Java",

        "c++": "C++",

        "sql": "SQL",

        "mysql": "MySQL",

        "postgresql": "PostgreSQL",

        "mongodb": "MongoDB",

        "html": "HTML",

        "css": "CSS",

        "javascript": "JavaScript",

        "react": "React",

        "node.js": "Node.js",

        "flask": "Flask",

        "django": "Django",

        "fastapi": "FastAPI",

        "rest api": "REST API",

        "api": "API",

        "git": "Git",

        "github": "GitHub",

        "aws": "AWS",

        "azure": "Azure",

        "machine learning":
            "Machine Learning",

        "deep learning":
            "Deep Learning",

        "pandas": "Pandas",

        "numpy": "NumPy",

        "scikit-learn":
            "Scikit-learn",

        "data analysis":
            "Data Analysis",

        "data analytics":
            "Data Analytics",

        "business analytics":
            "Business Analytics",

        "excel": "Excel",

        "power bi": "Power BI",

        "tableau": "Tableau",

        "testing": "Testing",

        "manual testing":
            "Manual Testing",

        "automation testing":
            "Automation Testing",

        "selenium": "Selenium",

        "communication":
            "Communication",

        "problem solving":
            "Problem Solving",

        "team collaboration":
            "Team Collaboration",

    }

    return keyword_map.get(
        keyword.lower(),
        keyword.title()
    )


# ==========================================
# COMPARE RESUME WITH JOB
# ==========================================

def compare_keywords(
    resume_text,
    job_keywords
):
    """
    Find which job keywords are present
    or absent in the resume.
    """

    resume = clean_text(
        resume_text
    )

    matched = []

    missing = []

    for keyword in job_keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            resume
        ):

            matched.append(
                normalize_keyword(
                    keyword
                )
            )

        else:

            missing.append(
                normalize_keyword(
                    keyword
                )
            )

    return matched, missing


# ==========================================
# ATS SCORE
# ==========================================

def calculate_ats_score(
    matched_keywords,
    total_keywords
):
    """
    Calculate keyword match percentage.

    This is a project-defined ATS metric.
    """

    if total_keywords == 0:

        return 0

    score = (
        len(matched_keywords)
        /
        total_keywords
    ) * 100

    return round(
        score,
        2
    )


# ==========================================
# COMPLETE ATS ANALYSIS
# ==========================================

def analyze_ats(
    resume_text,
    job_description
):
    """
    Perform complete ATS keyword analysis.
    """

    job_keywords_raw = (
        extract_keywords(
            job_description
        )
    )

    (
        matched_keywords,
        missing_keywords
    ) = compare_keywords(
        resume_text,
        job_keywords_raw
    )

    job_keywords = [
        normalize_keyword(keyword)
        for keyword in job_keywords_raw
    ]

    ats_score = calculate_ats_score(
        matched_keywords,
        len(job_keywords)
    )

    return {

        "ats_score":
            ats_score,

        "total_keywords":
            len(job_keywords),

        "matched_keyword_count":
            len(matched_keywords),

        "missing_keyword_count":
            len(missing_keywords),

        "job_keywords":
            job_keywords,

        "matched_keywords":
            matched_keywords,

        "missing_keywords":
            missing_keywords

    }