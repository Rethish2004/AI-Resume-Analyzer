
"""PDF report generator for the AI Resume Analyzer."""

from datetime import datetime
from html import escape
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)

NAVY = colors.HexColor("#152238")
BLUE = colors.HexColor("#3457D5")
PALE_BLUE = colors.HexColor("#EEF3FF")
PALE_GREY = colors.HexColor("#F3F5F8")
MID_GREY = colors.HexColor("#5B6575")
BORDER = colors.HexColor("#D8DFEA")


def normalize_key(value: Any) -> str:
    return "".join(c for c in str(value).lower() if c.isalnum())


def find_value(data: Any, aliases: list[str], depth: int = 0) -> Any:
    """Find a field in the API response, including nested dictionaries."""
    if data is None or depth > 12:
        return None

    alias_set = {normalize_key(alias) for alias in aliases}

    if isinstance(data, dict):
        # Prefer matches at the current level.
        for key, value in data.items():
            if normalize_key(key) in alias_set and value is not None:
                return value

        # Search nested dictionaries.
        for value in data.values():
            found = find_value(value, aliases, depth + 1)
            if found is not None:
                return found

    elif isinstance(data, (list, tuple)):
        for value in data:
            found = find_value(value, aliases, depth + 1)
            if found is not None:
                return found

    return None


def format_score(value: Any) -> str:
    """Format an existing score as a percentage; never invent one."""
    if value is None or value == "":
        return "Not returned by backend"

    if isinstance(value, dict):
        for key in ("percentage", "score", "value", "match_score"):
            if value.get(key) is not None:
                value = value[key]
                break
        else:
            return "Not returned by backend"

    original = str(value).strip()
    has_percent = original.endswith("%")
    numeric_text = original[:-1].strip() if has_percent else original

    try:
        number = float(numeric_text)
    except (TypeError, ValueError):
        return escape(original) if original else "Not returned by backend"

    # Convert fractions such as 0.85 to 85%.
    if not has_percent and 0 < number < 1:
        number *= 100

    number = max(0.0, min(100.0, number))
    number = round(number, 1)

    if number.is_integer():
        number = int(number)

    return f"{number}%"


def display_value(value: Any) -> str:
    if value is None or value == "":
        return "Not returned by backend"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (list, tuple, set)):
        if not value:
            return "None detected"
        return ", ".join(display_value(item) for item in value)

    if isinstance(value, dict):
        for key in (
            "name", "text", "label", "status",
            "value", "email", "phone", "role"
        ):
            if value.get(key) not in (None, ""):
                return display_value(value[key])

        return "; ".join(
            f"{key}: {display_value(item)}"
            for key, item in value.items()
        )

    return escape(str(value))


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []

    if isinstance(value, (list, tuple, set)):
        output = []

        for item in value:
            if isinstance(item, dict):
                chosen = None

                for key in (
                    "name", "skill", "keyword",
                    "text", "suggestion", "label"
                ):
                    if item.get(key) not in (None, ""):
                        chosen = item[key]
                        break

                output.append(
                    str(chosen if chosen is not None else item)
                )
            else:
                output.append(str(item))

        return [item for item in output if item.strip()]

    if isinstance(value, dict):
        return [f"{key}: {item}" for key, item in value.items()]

    if isinstance(value, str):
        parts = value.replace(";", "\n").splitlines()
        output = []

        for part in parts:
            output.extend(
                item.strip()
                for item in part.split(",")
                if item.strip()
            )

        return output

    return [str(value)]


def paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(str(text), style)


def add_list_section(
    story: list,
    title: str,
    value: Any,
    styles: dict,
) -> None:
    story.append(Spacer(1, 4 * mm))
    story.append(paragraph(escape(title), styles["section"]))

    items = as_list(value)

    if not items:
        story.append(
            paragraph(
                "No data returned by the analysis API.",
                styles["muted"],
            )
        )
        return

    bullets = [
        paragraph(f"&#8226;&nbsp; {escape(item)}", styles["body"])
        for item in items
    ]

    story.append(KeepTogether(bullets))


def generate_analysis_pdf(analysis: dict) -> bytes:
    """Generate a PDF from the exact analysis response sent by React."""
    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary")

    # Handle an optional extra wrapper around the API result.
    # Do not discard the outer dictionary because some metadata may be there.
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="AI Resume Analyzer Report",
        author="AI Resume Analyzer",
    )

    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=4 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontSize=9,
            leading=13,
            textColor=MID_GREY,
            alignment=TA_CENTER,
            spaceAfter=7 * mm,
        ),
        "section": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=NAVY,
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyTextCustom",
            parent=base["BodyText"],
            fontSize=9,
            leading=13,
            spaceAfter=1.5 * mm,
            textColor=colors.HexColor("#202938"),
        ),
        "muted": ParagraphStyle(
            "BodyMuted",
            parent=base["BodyText"],
            fontSize=9,
            leading=13,
            textColor=MID_GREY,
            italic=True,
            spaceAfter=1.5 * mm,
        ),
        "header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        ),
        "cell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#202938"),
        ),
        "score": ParagraphStyle(
            "ScoreCell",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=BLUE,
        ),
    }

    # These aliases match the fields returned by your /analyze route.
    filename = find_value(
        analysis,
        ["filename", "resume_name", "resume_filename", "original_filename"],
    )

    role = find_value(
        analysis,
        [
            "detected_job_role",
            "predicted_job_role",
            "job_role",
            "predicted_role",
            "role_name",
            "role",
        ],
    )

    word_count = find_value(
        analysis,
        ["word_count", "resume_word_count", "total_words"],
    )

    score_definitions = [
        (
            "Resume Match Score",
            [
                "resume_score",
                "overall_match_score",
                "overall_match_percentage",
                "resume_match_score",
                "match_score",
                "match_percentage",
                "overall_score",
            ],
        ),
        (
            "Job Similarity",
            [
                "similarity_score",
                "job_similarity",
                "job_similarity_score",
                "job_similarity_percentage",
                "similarity_percentage",
            ],
        ),
        (
            "Skill Match",
            [
                "skill_match",
                "skill_match_score",
                "skill_match_percentage",
                "skills_match_percentage",
            ],
        ),
        (
            "Role Keyword Match",
            [
                "role_keyword_match",
                "role_keyword_match_score",
                "role_keyword_match_percentage",
                "role_match_score",
            ],
        ),
        (
            "ATS Score",
            [
                "ats_score",
                "ats_percentage",
                "ats_match_score",
                "ats_score_percentage",
            ],
        ),
    ]

    story = [
        paragraph("AI Resume Analyzer", styles["title"]),
        paragraph("Resume Analysis Report", styles["subtitle"]),
        paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["muted"],
        ),
        Spacer(1, 3 * mm),
        paragraph("Resume Details", styles["section"]),
    ]

    details = [
        [
            paragraph("Field", styles["header"]),
            paragraph("Result", styles["header"]),
        ],
        [
            paragraph("Resume file", styles["cell"]),
            paragraph(display_value(filename), styles["cell"]),
        ],
        [
            paragraph("Detected Job Role", styles["cell"]),
            paragraph(display_value(role), styles["cell"]),
        ],
        [
            paragraph("Word Count", styles["cell"]),
            paragraph(display_value(word_count), styles["cell"]),
        ],
    ]

    details_table = Table(
        details,
        colWidths=[52 * mm, 115 * mm],
        repeatRows=1,
    )

    details_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_GREY]),
        ])
    )

    story.append(details_table)
    story.append(Spacer(1, 5 * mm))
    story.append(paragraph("Score Summary", styles["section"]))

    score_rows = [[
        paragraph("Score", styles["header"]),
        paragraph("Value", styles["header"]),
    ]]

    for label, aliases in score_definitions:
        actual_value = find_value(analysis, aliases)

        score_rows.append([
            paragraph(escape(label), styles["cell"]),
            paragraph(format_score(actual_value), styles["score"]),
        ])

    score_table = Table(
        score_rows,
        colWidths=[100 * mm, 67 * mm],
        repeatRows=1,
    )

    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PALE_BLUE, colors.white]),
        ])
    )

    story.append(score_table)

    # Skills, keywords and recommendations.
    list_sections = [
        (
            "Resume Skills",
            [
                "resume_skills", "detected_skills", "extracted_skills",
                "skills_found", "skills_detected", "skills",
            ],
        ),
        (
            "Required Job Skills",
            ["required_skills", "job_skills", "required_job_skills"],
        ),
        (
            "Matched Skills",
            ["matched_skills", "skills_matched", "common_skills"],
        ),
        (
            "Missing Skills",
            [
                "missing_skills", "skills_missing",
                "unmatched_skills", "required_missing_skills",
            ],
        ),
        (
            "Matched ATS Keywords",
            [
                "matched_ats_keywords", "matched_keywords_list",
                "matched_keywords", "keywords_matched_list",
            ],
        ),
        (
            "Missing ATS Keywords",
            [
                "missing_ats_keywords", "missing_keywords_list",
                "missing_keywords", "keywords_missing_list",
            ],
        ),
        (
            "Detected Role Keywords",
            [
                "detected_role_keywords",
                "role_keywords",
                "matched_role_keywords",
            ],
        ),
        (
            "Resume Improvement Suggestions",
            [
                "resume_improvement_suggestions",
                "improvement_suggestions",
                "suggestions",
                "recommendations",
            ],
        ),
        (
            "Found Resume Sections",
            ["found_sections", "sections_found", "present_sections"],
        ),
        (
            "Missing Resume Sections",
            ["missing_sections", "sections_missing", "absent_sections"],
        ),
    ]

    for title, aliases in list_sections:
        add_list_section(
            story,
            title,
            find_value(analysis, aliases),
            styles,
        )

    # Contact information.
    story.append(Spacer(1, 4 * mm))
    story.append(paragraph("Contact Information", styles["section"]))

    contact_rows = [[
        paragraph("Field", styles["header"]),
        paragraph("Detected Value", styles["header"]),
    ]]

    for label, aliases in [
        (
            "Email",
            ["resume_email", "email_address", "detected_email", "email"],
        ),
        (
            "Phone",
            ["phone_number", "detected_phone", "resume_phone", "phone"],
        ),
    ]:
        contact_rows.append([
            paragraph(escape(label), styles["cell"]),
            paragraph(
                display_value(find_value(analysis, aliases)),
                styles["cell"],
            ),
        ])

    contact_table = Table(
        contact_rows,
        colWidths=[52 * mm, 115 * mm],
        repeatRows=1,
    )

    contact_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_GREY]),
        ])
    )

    story.append(contact_table)

    # Project quality checks.
    story.append(Spacer(1, 4 * mm))
    story.append(paragraph("Project Quality Check", styles["section"]))

    quality_rows = [[
        paragraph("Check", styles["header"]),
        paragraph("Result", styles["header"]),
    ]]

    for label, aliases in [
        (
            "Technology Words",
            [
                "technology_words", "technology_words_status",
                "technologies_detected", "technology_check",
            ],
        ),
        (
            "Action Words",
            [
                "action_words", "action_words_status",
                "action_verbs", "action_word_check",
            ],
        ),
        (
            "Numbers / Results",
            [
                "numbers_results", "numbers_or_results",
                "measurable_results", "results_detected", "numbers_check",
            ],
        ),
    ]:
        quality_rows.append([
            paragraph(escape(label), styles["cell"]),
            paragraph(
                display_value(find_value(analysis, aliases)),
                styles["cell"],
            ),
        ])

    quality_table = Table(
        quality_rows,
        colWidths=[52 * mm, 115 * mm],
        repeatRows=1,
    )

    quality_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_GREY]),
        ])
    )

    story.append(quality_table)
    story.append(Spacer(1, 7 * mm))

    story.append(
        paragraph(
            "Generated by AI Resume Analyzer. Scores and extracted details "
            "come from the analysis API. Missing fields are shown as not "
            "returned by the backend.",
            styles["muted"],
        )
    )

    def draw_page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MID_GREY)
        canvas.drawString(18 * mm, 8 * mm, "AI Resume Analyzer")
        canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    return buffer.getvalue()
