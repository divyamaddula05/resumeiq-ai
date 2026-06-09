# ResumeIQ 🚀

AI-Powered ATS Resume Analyzer built using Python and Streamlit.

## 📌 Overview

ResumeIQ is an intelligent resume analysis platform that evaluates resumes against job descriptions using ATS-style matching techniques. The application provides resume scoring, skill gap analysis, role-based recommendations, and AI-powered improvement suggestions.

The project is designed to help students, freshers, and job seekers optimize their resumes for technical roles such as Software Engineer, Data Analyst, Data Scientist, and Frontend Developer.

---

## ✨ Features

* 📄 Resume PDF Upload
* 🤖 ATS Match Score Calculation
* 🎯 Role-Based Job Description Selection
* 🧠 Skill Extraction using NLP
* 📊 Resume Quality Scoring
* ✅ Matched Skills Detection
* ❌ Missing Skills Analysis
* 🚀 AI Resume Improvement Suggestions
* 📚 Course Recommendations
* 📈 Resume Metrics Dashboard
* 🔍 Candidate Level Prediction
* 🎥 Resume & Interview Preparation Resources
* 👨‍💻 Admin Analytics Dashboard

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### Libraries & Tools

* spaCy
* NLTK
* PDFPlumber
* Pandas
* Plotly
* PyMySQL
* Geocoder
* Streamlit Tags

---

## 🧠 ATS Matching Logic

The system:

1. Extracts resume text from uploaded PDF
2. Extracts technical skills from the resume
3. Compares extracted skills with job description requirements
4. Calculates ATS match percentage
5. Displays:

   * Matched Skills
   * Missing Skills
   * Resume Suggestions

---

## 📷 Application Modules

### User Module

* Upload resume
* Analyze ATS compatibility
* View resume score
* Get recommendations

### Feedback Module

* Submit ratings and feedback

### Admin Module

* View analytics
* Monitor users
* Analyze platform usage

---

## 🚀 Supported Roles

* Software Engineer
* Data Analyst
* Data Scientist
* Frontend Developer

---

## 📂 Project Structure

```bash
ResumeIQ/
│
├── App/
│   ├── App.py
│   ├── Courses.py
│   ├── parser.py
│   ├── styles.py
│   ├── ui.py
│   ├── requirements.txt
│
├── Uploaded_Resumes/
├── Logo/
├── README.md
```

---

## ⚙️ Installation

### Navigate to Project

```bash
cd resumeiq/App
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

```bash
streamlit run App.py
```

---

## 📊 Future Improvements

* Resume PDF Report Download
* AI Chat Assistant
* Semantic Skill Matching
* Advanced NLP-based Resume Parsing
* Cloud Database Integration
* Authentication System

---


# Author

## Divya Maddula

B.Tech Student | AI & Software Development Enthusiast

### Connect With Me

* GitHub: https://github.com/divyamaddula05
* LinkedIn: https://www.linkedin.com/in/divya-maddula-/

---

# Disclaimer

This project is developed for educational and learning purposes. Resume analysis results may vary depending on resume structure, formatting, and content.
