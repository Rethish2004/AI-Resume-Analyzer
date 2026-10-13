import re


# ==========================================
# ROLE KEYWORDS
# ==========================================

ROLE_KEYWORDS = {

    "Python Developer": [

        "python developer",
        "python software developer",
        "python engineer",
        "python",

        "flask",
        "django",
        "fastapi"

    ],


    "Data Analyst": [

        "data analyst",
        "data analysis",
        "data analytics",
        "business analyst",

        "excel",
        "power bi",
        "tableau",
        "sql"

    ],


    "Data Scientist": [

        "data scientist",
        "data science",

        "machine learning",
        "deep learning",

        "pandas",
        "numpy",
        "scikit-learn"

    ],


    "Backend Developer": [

        "backend developer",
        "backend engineer",
        "back-end developer",

        "rest api",
        "api development",

        "flask",
        "django",
        "fastapi",

        "node.js"

    ],


    "Frontend Developer": [

        "frontend developer",
        "frontend engineer",

        "front end developer",
        "front-end developer",

        "react",
        "javascript",
        "html",
        "css"

    ],


    "Full Stack Developer": [

        "full stack developer",
        "full-stack developer",
        "full stack engineer",

        "frontend",
        "backend",

        "react",
        "node.js",
        "api"

    ],


    "Software Tester": [

        "software tester",
        "software testing",

        "qa tester",
        "quality assurance",

        "manual testing",
        "automation testing",

        "selenium",
        "api testing"

    ],


    "Machine Learning Engineer": [

        "machine learning engineer",
        "ml engineer",

        "machine learning",
        "deep learning",

        "tensorflow",
        "pytorch",
        "scikit-learn"

    ]

}


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):

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
# DETECT ROLE
# ==========================================

def detect_job_role(
    job_description
):

    text = clean_text(
        job_description
    )


    if not text:

        return {

            "role": "Unknown",

            "score": 0,

            "matched_keywords": []

        }


    role_results = {}


    for role, keywords in ROLE_KEYWORDS.items():

        matched_keywords = []


        for keyword in keywords:

            keyword = keyword.lower()


            if keyword in text:

                matched_keywords.append(
                    keyword
                )


        role_results[role] = {

            "score":
                len(matched_keywords),

            "matched_keywords":
                matched_keywords

        }


    best_role = max(

        role_results,

        key=lambda role:
            role_results[role]["score"]

    )


    best_score = role_results[
        best_role
    ]["score"]


    best_keywords = role_results[
        best_role
    ]["matched_keywords"]


    if best_score == 0:

        return {

            "role": "Unknown",

            "score": 0,

            "matched_keywords": []

        }


    return {

        "role":
            best_role,

        "score":
            best_score,

        "matched_keywords":
            best_keywords

    }