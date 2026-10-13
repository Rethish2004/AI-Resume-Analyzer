import re


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):
    """
    Convert text into normalized lowercase text.
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
# CHECK RESUME SECTIONS
# ==========================================

def check_sections(resume_text):
    """
    Check whether common resume sections
    are present.
    """

    text = clean_text(resume_text)

    sections = {
        "objective": [
            "career objective",
            "objective",
            "summary",
            "profile"
        ],

        "education": [
            "education",
            "academic"
        ],

        "skills": [
            "skills",
            "technical skills",
            "key skills"
        ],

        "projects": [
            "projects",
            "academic projects"
        ],

        "certifications": [
            "certifications",
            "certification"
        ],

        "experience": [
            "experience",
            "work experience",
            "employment"
        ]
    }

    found_sections = []
    missing_sections = []

    for section, keywords in sections.items():

        found = any(
            keyword in text
            for keyword in keywords
        )

        if found:
            found_sections.append(
                section
            )
        else:
            missing_sections.append(
                section
            )

    return {
        "found": found_sections,
        "missing": missing_sections
    }


# ==========================================
# CHECK CONTACT INFORMATION
# ==========================================

def check_contact_information(resume_text):
    """
    Check for common contact information.
    """

    text = resume_text or ""

    result = {
        "email": False,
        "phone": False
    }

    # Email
    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    if re.search(
        email_pattern,
        text
    ):
        result["email"] = True

    # Phone
    phone_pattern = (
        r"(?:\+91[\s-]?)?"
        r"[6-9]\d{9}"
    )

    if re.search(
        phone_pattern,
        text
    ):
        result["phone"] = True

    return result


# ==========================================
# CHECK PROJECT BULLETS
# ==========================================

def check_project_quality(resume_text):
    """
    Check whether project descriptions contain
    useful technical and result-oriented language.
    """

    text = clean_text(
        resume_text
    )

    result = {
        "has_technology_words": False,
        "has_action_words": False,
        "has_numbers": False
    }

    technology_words = [
        "python",
        "java",
        "sql",
        "mysql",
        "javascript",
        "react",
        "flask",
        "django",
        "html",
        "css",
        "git",
        "machine learning"
    ]

    action_words = [
        "developed",
        "built",
        "created",
        "implemented",
        "designed",
        "developed",
        "improved",
        "automated",
        "tested",
        "managed"
    ]

    if any(
        word in text
        for word in technology_words
    ):
        result["has_technology_words"] = True

    if any(
        word in text
        for word in action_words
    ):
        result["has_action_words"] = True

    if re.search(
        r"\b\d+%?\b",
        text
    ):
        result["has_numbers"] = True

    return result


# ==========================================
# GENERATE SUGGESTIONS
# ==========================================

def generate_suggestions(
    resume_text,
    missing_keywords=None
):
    """
    Generate suggestions based on
    resume structure and detected gaps.
    """

    suggestions = []

    missing_keywords = (
        missing_keywords or []
    )

    # ======================================
    # SECTIONS
    # ======================================

    section_result = check_sections(
        resume_text
    )

    found_sections = section_result[
        "found"
    ]

    missing_sections = section_result[
        "missing"
    ]


    # ======================================
    # CONTACT
    # ======================================

    contact = check_contact_information(
        resume_text
    )

    if not contact["email"]:

        suggestions.append(
            "Add a professional email address "
            "to the resume header."
        )

    if not contact["phone"]:

        suggestions.append(
            "Add a reachable phone number "
            "to the resume header."
        )


    # ======================================
    # SKILLS
    # ======================================

    if "skills" not in found_sections:

        suggestions.append(
            "Add a clearly labelled Skills "
            "section containing relevant technical "
            "skills."
        )


    # ======================================
    # PROJECTS
    # ======================================

    if "projects" not in found_sections:

        suggestions.append(
            "Add relevant academic or personal "
            "projects and mention the technologies "
            "you used."
        )


    # ======================================
    # EXPERIENCE
    # ======================================

    if "experience" not in found_sections:

        suggestions.append(
            "If applicable, add internships, "
            "training, freelance work, or practical "
            "experience."
        )


    # ======================================
    # PROJECT QUALITY
    # ======================================

    project_quality = (
        check_project_quality(
            resume_text
        )
    )

    if not project_quality[
        "has_technology_words"
    ]:

        suggestions.append(
            "Mention the specific technologies "
            "used in each project."
        )


    if not project_quality[
        "has_action_words"
    ]:

        suggestions.append(
            "Start project bullets with action "
            "words such as Developed, Built, "
            "Implemented, Designed, or Automated."
        )


    if not project_quality[
        "has_numbers"
    ]:

        suggestions.append(
            "Add measurable results where "
            "possible, such as time saved, records "
            "processed, features implemented, or "
            "percentage improvements."
        )


    # ======================================
    # MISSING JOB KEYWORDS
    # ======================================

    if missing_keywords:

        keyword_text = ", ".join(
            missing_keywords[:8]
        )

        suggestions.append(
            "Review these missing job keywords "
            "and include only the ones that "
            "truthfully match your skills or "
            f"experience: {keyword_text}."
        )


    # ======================================
    # GENERAL SUGGESTION
    # ======================================

    suggestions.append(
        "Keep the resume concise and place the "
        "most relevant skills and project "
        "information where recruiters can find "
        "them easily."
    )


    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_suggestions = []

    for suggestion in suggestions:

        if suggestion not in unique_suggestions:

            unique_suggestions.append(
                suggestion
            )


    # Return maximum 8 suggestions
    return unique_suggestions[:8]


# ==========================================
# COMPLETE SUGGESTION ANALYSIS
# ==========================================

def analyze_resume_suggestions(
    resume_text,
    missing_keywords=None
):
    """
    Perform complete resume suggestion analysis.
    """

    sections = check_sections(
        resume_text
    )

    contact = check_contact_information(
        resume_text
    )

    project_quality = (
        check_project_quality(
            resume_text
        )
    )

    suggestions = generate_suggestions(
        resume_text,
        missing_keywords
    )

    return {

        "suggestions":
            suggestions,

        "sections": {

            "found":
                sections["found"],

            "missing":
                sections["missing"]

        },

        "contact": contact,

        "project_quality":
            project_quality
    }