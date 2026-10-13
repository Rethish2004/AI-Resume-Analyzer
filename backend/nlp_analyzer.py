import re

import spacy

from spacy.matcher import PhraseMatcher


# ==========================================
# LOAD SPACY
# ==========================================

nlp = spacy.load(
    "en_core_web_sm"
)


# ==========================================
# SKILL LIST
# ==========================================

SKILLS = [

    "Python",
    "Java",
    "C++",
    "C",

    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",

    "HTML",
    "CSS",
    "JavaScript",
    "React",

    "Flask",
    "Django",
    "FastAPI",

    "REST API",

    "Git",
    "GitHub",

    "AWS",
    "Azure",

    "Machine Learning",
    "Deep Learning",

    "Data Analysis",
    "Data Analytics",
    "Business Analytics",
    "Data Interpretation",

    "Excel",
    "PowerPoint",
    "Word",

    "Power BI",
    "Tableau",

    "Problem Solving",
    "Team Collaboration",
    "Communication",
    "Time Management",
    "Customer Service",
    "Process Improvement"

]


# ==========================================
# PHRASE MATCHER
# ==========================================

skill_matcher = PhraseMatcher(
    nlp.vocab,
    attr="LOWER"
)


skill_patterns = [

    nlp.make_doc(skill)

    for skill in SKILLS

]


skill_matcher.add(
    "SKILL",
    skill_patterns
)


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):
    """
    Normalize resume text.
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
# NORMALIZE SKILL NAME
# ==========================================

def normalize_skill(skill):

    skill_map = {

        "python": "Python",
        "java": "Java",
        "c++": "C++",
        "c": "C",

        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "mongodb": "MongoDB",

        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",

        "react": "React",

        "flask": "Flask",
        "django": "Django",
        "fastapi": "FastAPI",

        "rest api": "REST API",

        "git": "Git",
        "github": "GitHub",

        "aws": "AWS",
        "azure": "Azure",

        "machine learning":
            "Machine Learning",

        "deep learning":
            "Deep Learning",

        "data analysis":
            "Data Analysis",

        "data analytics":
            "Data Analytics",

        "business analytics":
            "Business Analytics",

        "data interpretation":
            "Data Interpretation",

        "excel":
            "Excel",

        "powerpoint":
            "PowerPoint",

        "word":
            "Word",

        "power bi":
            "Power BI",

        "tableau":
            "Tableau",

        "problem solving":
            "Problem Solving",

        "team collaboration":
            "Team Collaboration",

        "communication":
            "Communication",

        "time management":
            "Time Management",

        "customer service":
            "Customer Service",

        "process improvement":
            "Process Improvement"

    }

    return skill_map.get(
        skill.lower(),
        skill.title()
    )


# ==========================================
# EXTRACT SKILLS
# ==========================================

def extract_skills(text):
    """
    Extract known technical and soft skills.
    """

    if not text:

        return []


    doc = nlp(text)

    matches = skill_matcher(doc)

    found_skills = []


    for _, start, end in matches:

        skill = doc[
            start:end
        ].text

        found_skills.append(
            normalize_skill(skill)
        )


    # C++ additional support
    if re.search(
        r"c\+\+",
        text,
        re.IGNORECASE
    ):

        found_skills.append(
            "C++"
        )


    return sorted(
        set(found_skills),
        key=str.lower
    )


# ==========================================
# COMPLETE NLP ANALYSIS
# ==========================================

def analyze_resume(text):
    """
    Analyze the resume text using spaCy.
    """

    if not text:

        return {

            "word_count": 0,

            "skills": []

        }


    cleaned = clean_text(
        text
    )


    doc = nlp(
        cleaned
    )


    skills = extract_skills(
        cleaned
    )


    return {

        "word_count":
            len(doc),

        "skills":
            skills

    }