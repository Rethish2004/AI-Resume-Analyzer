from resume_parser import extract_resume_text


file_path = "sample_resume.pdf"

try:
    text = extract_resume_text(file_path)

    print("\n===== RESUME TEXT =====\n")
    print(text)

except Exception as error:
    print("Error:", error)
    