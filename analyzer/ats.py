"""
analyzer/ats.py
---------------
Estimates an ATS (Applicant Tracking System) Score for a resume (0–100).
This is always presented as an ESTIMATE — never claimed as exact.
Based on: keywords, section order, readability, formatting, skill relevance.
"""

import re
from utils.helper import detect_sections, extract_links


# ATS-friendly section order (standard resume structure ATS systems expect)
EXPECTED_SECTION_ORDER = [
    "summary",
    "education",
    "experience",
    "projects",
    "skills",
    "certifications",
    "achievements",
]

# Common ATS-friendly keywords for tech resumes
ATS_KEYWORDS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    # Frameworks & Libraries
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "fastapi",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd", "linux",
    # ML/AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    # General professional terms
    "developed", "implemented", "designed", "deployed", "built", "collaborated",
    "agile", "scrum", "rest api", "microservices",
]


def calculate_ats_score(resume_text: str) -> int:
    """
    Estimate the ATS compatibility score of a resume (0–100).

    ATS scoring factors:
        1. Keyword density         — 30%
        2. Section presence        — 25%
        3. Contact information     — 20%
        4. Formatting simplicity   — 15%
        5. File/text readability   — 10%

    Args:
        resume_text: The cleaned resume text.

    Returns:
        Integer ATS score from 0 to 100. Always an estimate.
    """
    text_lower = resume_text.lower()

    keyword_score = _score_keywords(text_lower)
    section_score = _score_sections(resume_text)
    contact_score = _score_contact(resume_text)
    formatting_score = _score_ats_formatting(resume_text)
    readability_score = _score_readability(resume_text)

    # Weighted total
    total = (
        keyword_score * 0.30 +
        section_score * 0.25 +
        contact_score * 0.20 +
        formatting_score * 0.15 +
        readability_score * 0.10
    )

    return max(0, min(100, round(total)))


def _score_keywords(text_lower: str) -> float:
    """Score keyword density (0–100)."""
    matched = sum(1 for kw in ATS_KEYWORDS if kw in text_lower)
    total = len(ATS_KEYWORDS)

    ratio = matched / total
    if ratio >= 0.30:
        return 100.0
    elif ratio >= 0.20:
        return 80.0
    elif ratio >= 0.15:
        return 65.0
    elif ratio >= 0.10:
        return 45.0
    elif ratio >= 0.05:
        return 25.0
    else:
        return 10.0


def _score_sections(resume_text: str) -> float:
    """Score presence of standard ATS-expected sections (0–100)."""
    sections = detect_sections(resume_text)
    present = sum(1 for s in EXPECTED_SECTION_ORDER if sections.get(s, False))
    total = len(EXPECTED_SECTION_ORDER)
    return round((present / total) * 100)


def _score_contact(resume_text: str) -> float:
    """Score contact information completeness (0–100)."""
    from utils.helper import extract_email, extract_phone
    score = 0.0

    if extract_email(resume_text):
        score += 35.0
    if extract_phone(resume_text):
        score += 30.0
    links = extract_links(resume_text)
    if links["linkedin"]:
        score += 20.0
    if links["github"]:
        score += 15.0

    return min(score, 100.0)


def _score_ats_formatting(resume_text: str) -> float:
    """
    Score ATS-friendly formatting (0–100).
    ATS systems prefer plain text with clear section headers.
    """
    score = 50.0
    lines = resume_text.split("\n")

    # Penalty: Too many symbols (ATS can misread decorative symbols)
    symbol_count = len(re.findall(r"[★✦✓•◆■▪]", resume_text))
    if symbol_count > 20:
        score -= 20.0
    elif symbol_count > 10:
        score -= 10.0

    # Bonus: Clear section headers detected
    header_lines = sum(
        1 for l in lines
        if re.match(r"^[A-Z][a-zA-Z\s]{2,25}$", l.strip()) and len(l.strip()) < 30
    )
    if header_lines >= 4:
        score += 30.0
    elif header_lines >= 2:
        score += 15.0

    # Bonus: Reasonable line lengths (not too long, not too short)
    reasonable_lines = sum(
        1 for l in lines
        if 20 <= len(l.strip()) <= 120
    )
    if reasonable_lines >= 10:
        score += 20.0

    return max(0.0, min(score, 100.0))


def _score_readability(resume_text: str) -> float:
    """Score basic readability for ATS (0–100)."""
    score = 50.0
    word_count = len(resume_text.split())

    # Reasonable length range for a 1-page tech resume
    if 250 <= word_count <= 700:
        score += 50.0
    elif 150 <= word_count <= 900:
        score += 30.0
    elif word_count < 100:
        score -= 30.0  # Too short — likely incomplete

    return max(0.0, min(score, 100.0))
