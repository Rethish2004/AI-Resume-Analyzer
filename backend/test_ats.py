from resume_parser import extract_resume_text

from ats_analyzer import analyze_ats


# ==========================================
# RESUME FILE
# ==========================================

resume_file = "sample_resume.pdf"


# ==========================================
# TEST JOB DESCRIPTION
# ==========================================

job_description = """
We are looking for a Python Software Developer.

Requirements:

Python
Django
Flask
FastAPI
REST API
MySQL
Git
GitHub
React
AWS
Machine Learning
SQL
Problem Solving
Communication
"""


# ==========================================
# READ RESUME
# ==========================================

try:

    resume_text = extract_resume_text(
        resume_file
    )


    # ======================================
    # ATS ANALYSIS
    # ======================================

    result = analyze_ats(
        resume_text,
        job_description
    )


    print()
    print("=" * 55)
    print("ATS ANALYSIS")
    print("=" * 55)


    print()
    print(
        "ATS Score:"
    )

    print(
        result["ats_score"],
        "%"
    )


    print()
    print(
        "Total Job Keywords:"
    )

    print(
        result["total_keywords"]
    )


    print()
    print(
        "Matched Keywords:"
    )


    for keyword in result[
        "matched_keywords"
    ]:

        print(
            "-",
            keyword
        )


    print()
    print(
        "Missing Keywords:"
    )


    for keyword in result[
        "missing_keywords"
    ]:

        print(
            "-",
            keyword
        )


    print()
    print("=" * 55)


except Exception as error:

    print()
    print(
        "ERROR:",
        error
    )