from resume_parser import extract_resume_text

from suggestion_engine import (
    analyze_resume_suggestions
)


# ==========================================
# RESUME
# ==========================================

resume_file = "sample_resume.pdf"


# ==========================================
# TEST MISSING KEYWORDS
# ==========================================

missing_keywords = [
    "Django",
    "Flask",
    "REST API",
    "React",
    "AWS"
]


# ==========================================
# EXTRACT RESUME
# ==========================================

try:

    resume_text = extract_resume_text(
        resume_file
    )


    # ======================================
    # ANALYZE
    # ======================================

    result = analyze_resume_suggestions(

        resume_text,

        missing_keywords

    )


    print()
    print("=" * 60)
    print("RESUME IMPROVEMENT ANALYSIS")
    print("=" * 60)


    print()
    print("Found Sections:")

    for section in result[
        "sections"
    ]["found"]:

        print(
            "-",
            section
        )


    print()
    print("Missing Sections:")

    for section in result[
        "sections"
    ]["missing"]:

        print(
            "-",
            section
        )


    print()
    print("Contact Information:")

    print(
        "Email:",
        result["contact"]["email"]
    )

    print(
        "Phone:",
        result["contact"]["phone"]
    )


    print()
    print("Project Quality:")

    print(
        "Technology words:",
        result["project_quality"][
            "has_technology_words"
        ]
    )

    print(
        "Action words:",
        result["project_quality"][
            "has_action_words"
        ]
    )

    print(
        "Numbers:",
        result["project_quality"][
            "has_numbers"
        ]
    )


    print()
    print("Suggestions:")


    for index, suggestion in enumerate(
        result["suggestions"],
        start=1
    ):

        print(
            f"{index}. {suggestion}"
        )


    print()
    print("=" * 60)


except Exception as error:

    print()

    print(
        "ERROR:",
        error
    )