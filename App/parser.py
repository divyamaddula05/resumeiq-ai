import pdfplumber
import re
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_resume_data(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted

    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    email = email[0] if email else ""

    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    phone = phone[0] if phone else ""

    doc = nlp(text)

    name = ""

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    skills_db = [
        "python",
        "java",
        "sql",
        "mysql",
        "html",
        "css",
        "javascript",
        "react",
        "django",
        "streamlit",
        "machine learning",
        "tensorflow",
        "flask",
        "pandas",
        "numpy"
    ]

    found_skills = []

    lower_text = text.lower()

    for skill in skills_db:
        if skill.lower() in lower_text:
            found_skills.append(skill)

    return {
        "name": name,
        "email": email,
        "mobile_number": phone,
        "skills": found_skills,
        "no_of_pages": len(pdf.pages)
    }