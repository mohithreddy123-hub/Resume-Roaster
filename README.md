# 🔥 Resume Roaster

> An AI-powered, conversational resume review and ATS alignment platform that evaluates resumes like an experienced 20-year veteran senior tech recruiter.

---

## 📌 What the Project Is

Resume Roaster is a **Hybrid Dual-Engine System** combining deterministic Python mathematical scoring with Google Gemini Generative AI. It analyzes tech resumes, calculates independent **Resume Scores** and **ATS Compatibility Scores**, provides evidence-backed recruiter roasts, and offers interactive recruiter chat.

---

## 📦 Dependencies Installed

- `streamlit==1.39.0`
- `google-generativeai==0.8.3`
- `pymupdf==1.24.11`
- `python-docx==1.1.2`
- `pydantic==2.9.2`
- `python-dotenv==1.0.1`
- `regex==2024.9.11`

---

## 🛠️ Technical Skills Used

- **Python 3.12+**
- **Streamlit** (Web Framework & Session State Architecture)
- **Google Gemini API** (`gemini-1.5-flash`)
- **Generative AI & Advanced Prompt Engineering**
- **Document Parsing** (PyMuPDF / `fitz` & `python-docx`)
- **Text Processing & Regex Pattern Extraction**
- **Custom CSS3** (Vanilla Dark Theme Systems)

---

## 📂 Project Structure

```
Resume-Roaster/
├── app.py
├── config.py
├── pyrefly.toml
├── requirements.txt
├── README.md
├── PROJECT_DETAILS.txt
├── .env.example
├── analyzer/
│   ├── __init__.py
│   ├── score.py
│   ├── ats.py
│   ├── classifier.py
│   ├── strengths.py
│   └── weaknesses.py
├── llm/
│   ├── __init__.py
│   └── gemini.py
├── parser/
│   ├── __init__.py
│   ├── parser.py
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   └── section_detector.py
├── prompts/
│   ├── __init__.py
│   ├── system_prompt.py
│   ├── roast_prompt.py
│   ├── json_schema.py
│   ├── conversation_prompt.py
│   ├── missing_prompt.py
│   ├── comparison_prompt.py
│   ├── rewrite_prompt.py
│   └── skill_prompt.py
├── ui/
│   ├── __init__.py
│   ├── styles.py
│   ├── upload.py
│   ├── dashboard.py
│   └── sidebar.py
├── utils/
│   ├── __init__.py
│   ├── cleaner.py
│   ├── validator.py
│   └── helper.py
└── static/
    └── style.css
```

---

## 🚀 Future Improvements

- Optical Character Recognition (OCR) for scanned image PDFs
- Exporting audited resume fixes directly to downloadable PDF / DOCX
- Live job board integration for real-time active JD matching
- Multi-role target comparison matrix