from resume_parser import extract_resume_text
from matcher import analyze_job_match


resume_file = "sample_resume.pdf"


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


try:
    resume_text = extract_resume_text(resume_file)

    result = analyze_job_match(
        resume_text,
        job_description
    )

    print("\n===== JOB MATCH ANALYSIS =====")

    print("\nSimilarity Score:")
    print(result["similarity_score"], "%")

    print("\nSkill Match:")
    print(result["skill_match"], "%")

    print("\nRequired Skills:")
    for skill in result["required_skills"]:
        print("-", skill.title())

    print("\nMatched Skills:")
    for skill in result["matched_skills"]:
        print("-", skill.title())

    print("\nMissing Skills:")
    for skill in result["missing_skills"]:
        print("-", skill.title())

except Exception as error:
    print("Error:", error)