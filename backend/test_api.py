from app import app


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


client = app.test_client()


try:
    with open(resume_file, "rb") as file:

        response = client.post(
            "/analyze",
            data={
                "resume": (
                    file,
                    "sample_resume.pdf"
                ),
                "job_description": job_description
            },
            content_type="multipart/form-data"
        )

    print("\n===== API STATUS =====")
    print(response.status_code)

    print("\n===== API RESPONSE =====")
    print(response.get_json())

except Exception as error:
    print("Error:", error)