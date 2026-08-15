# 🔥 Resume Roaster

**Resume Roaster** is an AI-powered, conversational resume review and ATS alignment application. Unlike traditional resume tools that output generic, overly polite corporate HR advice, Resume Roaster evaluates tech resumes like an experienced 20-year veteran senior recruiter and engineering director who is sitting across the table having a real conversation.

---

## 📌 What the Project Is

Resume Roaster is a **Hybrid Dual-Engine System** that combines deterministic Python mathematical logic with Google Gemini Generative AI:

* **Dual Mathematical Scoring System (0–100)**:
  * **Resume Score**: Evaluates project depth, evidence, metrics, and technical claims based on candidate career stage (*Fresher*, *Early Career*, *Experienced*).
  * **ATS Compatibility Score**: Evaluates document parseability, keyword coverage against 50+ tech terms, standard section ordering, contact info completeness, and job description alignment.
* **Recruiter AI Character Engine**:
  * **Natural Openings**: Human reactions based on actual resume content.
  * **Evidence-Backed Roasts & Weaknesses**: Calls out weak descriptions, tutorial projects, unproven skills, or exaggerated metrics.
  * **What I'd Fix First**: A single, decisive priority recommendation.
  * **2–3 Resume-Specific Questions**: Direct questions about unproven claims or missing details.
* **Interactive Recruiter Chat & History**:
  * Multi-turn conversational chat maintaining persona context.
  * Multi-resume persistent session management and head-to-head resume comparison.

---

## 📦 Dependencies Installed

The application is built on Python 3.12+ and uses the following dependencies:

| Dependency | Version | Role in Project |
| :--- | :--- | :--- |
| `streamlit` | `1.39.0` | Reactive web UI framework, file uploader, and session state manager |
| `google-generativeai` | `0.8.3` | Official Google Gemini API client SDK (`gemini-1.5-flash`) |
| `pymupdf` (`fitz`) | `1.24.11` | C-backed high-performance PDF layout stream text parser |
| `python-docx` | `1.1.2` | Microsoft Word XML document parser for paragraph and table text extraction |
| `pydantic` | `2.9.2` | Data validation and schema enforcement |
| `python-dotenv` | `1.0.1` | Loads local environment variables (`GEMINI_API_KEY`) securely from `.env` |
| `regex` | `2024.9.11` | Advanced regular expression engine for text sectioning and contact extraction |

---

## 🛠️ Technical Skills Used

* **Generative AI & LLM Integration**: API gateway design using Google Gemini API (`gemini-1.5-flash`), exponential backoff retry algorithms with random jitter for HTTP 429 rate limits, and structured JSON MIME output handling.
* **Prompt Engineering & Persona Design**: Advanced system prompt steering, persona constraint enforcement, corporate HR banned phrase filtering, and in-context prompt injections.
* **Document Parsing & Text Extraction**: Parsing unformatted layout streams from PDFs via PyMuPDF (`fitz`) and XML tree structures from Word documents via `python-docx`.
* **Deterministic Mathematical Modeling**: Developing custom, non-LLM dynamic weight scoring tables, career stage detection heuristics, and multi-factor ATS keyword density algorithms.
* **Full-Stack Python & State Architecture**: Building a single-process reactive web app with Streamlit, handling file buffer streams safely (`.getvalue()`), and managing persistent multi-resume session isolation (`st.session_state`).
* **UI/UX Design Systems**: Designing a Premium Dark Theme UI system using vanilla custom CSS (`static/style.css`), layered card components, floating chat containers, and custom badge elements.

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

## 📄 Folder and File Names Breakdown

### Root Directory
* `app.py`: Main Streamlit application entry point, pipeline orchestrator, and session state router.
* `config.py`: Centralized configuration constants, score weights, model settings, and retry rules.
* `requirements.txt`: List of required Python packages.
* `PROJECT_DETAILS.txt`: Detailed technical documentation report.
* `.env.example`: Template file for setting up local environment variables (`GEMINI_API_KEY`).

### `analyzer/` — Mathematical Scoring & Analytics Engine
* `analyzer/score.py`: Computes Overall Resume Score (0–100) using dynamic career-stage weight tables (*Fresher*, *Early Career*, *Experienced*).
* `analyzer/ats.py`: Computes ATS Compatibility Score (0–100) across 6 weighted factors (keywords, sections, contact, formatting, JD alignment, readability).
* `analyzer/classifier.py`: Tiers resumes into *Excellent*, *Good*, *Average*, or *Bad*.
* `analyzer/strengths.py` & `analyzer/weaknesses.py`: Deterministic rule-based fallback analysis generators.

### `llm/` — Gemini API Gateway
* `llm/gemini.py`: Wrapper for Google Gemini API client SDK with exponential backoff retries handling rate limits.

### `parser/` — Document Text Extraction Engine
* `parser/parser.py`: Unified entry point routing `.pdf` and `.docx` files to respective parsers.
* `parser/pdf_parser.py`: PyMuPDF layout text stream parser for PDF files.
* `parser/docx_parser.py`: `python-docx` XML parser for Microsoft Word files.
* `parser/section_detector.py`: Heuristic regex matcher segmenting raw text into structured resume sections.

### `prompts/` — Prompt Engineering & Schemas
* `prompts/system_prompt.py`: Recruiter character persona rules and banned corporate phrase filter.
* `prompts/roast_prompt.py`: Constructs the initial review prompt containing scores and structured resume data.
* `prompts/json_schema.py`: Output JSON schema specifications and bulletproof regex JSON parser validator.
* `prompts/conversation_prompt.py`: Formats context-rich follow-up chat prompts.
* `prompts/missing_prompt.py`: Prompt builder for sparse or incomplete resumes.
* `prompts/comparison_prompt.py`: Prompt builder for head-to-head comparison between multiple uploaded resumes.
* `prompts/rewrite_prompt.py`: Prompt builder for section and bullet point rewrites.
* `prompts/skill_prompt.py`: Prompt builder for target role skill gap suggestions.

### `ui/` — Streamlit Component Layer
* `ui/styles.py`: Injects custom CSS, renders hero header, Apple/Notion dual minimal score cards, and progress steps.
* `ui/upload.py`: Single primary hero upload dropzone component with byte stream safety.
* `ui/dashboard.py`: Renders recruiter results dashboard and chat interface.
* `ui/sidebar.py`: Left sidebar history selector, session overview statistics, and comparison controls.

### `utils/` — Helper Utilities
* `utils/cleaner.py`: Text cleaning and whitespace normalization.
* `utils/validator.py`: File size/format validation, extracted text validation, and missing field scanner.
* `utils/helper.py`: Regex pattern extractors for emails, phone numbers, and web links.

### `static/` — Custom Styling
* `static/style.css`: Premium Dark Theme CSS stylesheet (`#111315` canvas, `#1B1F27` cards, `#FF6A00` signature orange accent).

---

## 🚀 Future Improvements

1. **Optical Character Recognition (OCR)**: Integrate Tesseract / OCR engines to support image-based and scanned PDF resumes.
2. **Exportable Audited Resumes**: Allow users to export their improved bullet points and fixed sections directly into a formatted downloadable PDF or Word document.
3. **Live Job Board Integration**: Enable real-time fetching of live job descriptions from LinkedIn or Indeed to calculate direct match scores against active job postings.
4. **Multi-Role Target Matrix**: Compare a candidate's resume against multiple target roles simultaneously (e.g., *Backend Engineer* vs. *DevOps Engineer* vs. *Data Engineer*).