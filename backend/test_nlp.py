from resume_parser import extract_resume_text
from nlp_analyzer import analyze_resume


# Resume file
file_path = "sample_resume.pdf"

try:
    # Step 1: Extract resume text
    resume_text = extract_resume_text(file_path)

    # Step 2: Analyze resume using NLP
    result = analyze_resume(resume_text)

    print("\n===== NLP ANALYSIS =====")

    print("\nWord Count:")
    print(result["word_count"])

    print("\nSkills Found:")

    for skill in result["skills"]:
        print("-", skill)

except Exception as error:
    print("Error:", error)