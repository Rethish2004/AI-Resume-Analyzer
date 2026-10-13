from role_detector import detect_job_role


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
SQL
Problem Solving
Communication
"""


result = detect_job_role(
    job_description
)


print()
print("=" * 50)
print("JOB ROLE DETECTION")
print("=" * 50)

print()

print(
    "Detected Role:"
)

print(
    result["role"]
)

print()

print(
    "Keyword Score:"
)

print(
    result["score"]
)

print()

print(
    "Matched Role Keywords:"
)


for keyword in result[
    "matched_keywords"
]:

    print(
        "-",
        keyword
    )


print()
print("=" * 50)