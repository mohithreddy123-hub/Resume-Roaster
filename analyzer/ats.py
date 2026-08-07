# pyrefly: ignore
"""
analyzer/ats.py
---------------
Estimates an ATS (Applicant Tracking System) compatibility score (0–100).

Design principles:
  - Completely independent from Resume Score — no shared signals.
  - Multi-factor model reflecting how modern ATS systems actually evaluate resumes.
  - Evaluates keyword relevance, placement, context, stuffing, section structure,
    contact completeness, formatting/parseability, JD alignment, and readability.
  - Rigid percentage-cutoff thresholds are replaced with a weighted evidence model.
"""

import re
from utils.helper import detect_sections, extract_email, extract_phone, extract_links


# ─── ATS Factor Weights (must sum to 1.0) ─────────────────────────────────────
_ATS_WEIGHTS = {
    "keywords":    0.28,   # Keyword relevance, coverage, placement, stuffing
    "sections":    0.22,   # Standard section headings in expected order
    "contact":     0.18,   # Email, phone, LinkedIn, GitHub
    "formatting":  0.17,   # Formatting & parseability (no tables, symbols, columns)
    "jd_alignment":0.10,   # Job-description keyword alignment
    "readability": 0.05,   # Word count in valid range
}

# Standard tech-resume ATS keywords — covers languages, frameworks, tools, and methods
ATS_KEYWORDS: list[str] = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "dart", "r",
    # Frameworks & Libraries
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "fastapi",
    "express", "next.js", "laravel", "rails", ".net", "flutter",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "elasticsearch",
    "cassandra", "dynamodb", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd",
    "linux", "terraform", "ansible", "jenkins", "github actions",
    # ML / AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "nlp", "computer vision",
    # Professional methodology keywords
    "rest api", "microservices", "agile", "scrum", "devops",
    "object-oriented", "data structures", "algorithms",
]

# ATS expects sections in roughly this order for optimal parsing
EXPECTED_SECTION_ORDER = [
    "summary", "education", "experience", "projects", "skills",
    "certifications", "achievements",
]


def calculate_ats_score(resume_text: str, job_description: str = "") -> int:
    """
    Estimate the ATS compatibility score of a resume (0–100).

    Multi-factor model — each factor has its own weight:
        keywords     28% — relevance, coverage, placement, stuffing penalty
        sections     22% — standard headings in expected parseable order
        contact      18% — email, phone, LinkedIn, GitHub
        formatting   17% — no tables, columns, or symbols breaking ATS parsing
        jd_alignment 10% — keyword overlap with provided job description
        readability   5% — word count in valid resume range

    Args:
        resume_text:     The cleaned resume text.
        job_description: Optional target job description text for alignment scoring.

    Returns:
        Integer ATS score from 0 to 100.
    """
    text_lower = resume_text.lower()
    jd_lower   = job_description.lower() if job_description else ""

    keyword_score    = _score_keywords(text_lower)
    section_score    = _score_sections(resume_text)
    contact_score    = _score_contact(resume_text)
    formatting_score = _score_ats_formatting(resume_text)
    jd_score         = _score_jd_alignment(text_lower, jd_lower)
    readability_score = _score_readability(resume_text)

    total = (
        keyword_score     * _ATS_WEIGHTS["keywords"] +
        section_score     * _ATS_WEIGHTS["sections"] +
        contact_score     * _ATS_WEIGHTS["contact"] +
        formatting_score  * _ATS_WEIGHTS["formatting"] +
        jd_score          * _ATS_WEIGHTS["jd_alignment"] +
        readability_score * _ATS_WEIGHTS["readability"]
    )

    return max(0, min(100, round(total)))


def _ats_keyword_details(text_lower: str) -> dict:
    """
    Internal helper: compute detailed keyword stats for explanation generation.
    Returns matched_count, total, stuffed_count.
    """
    matched: list[str] = []
    stuffed: list[str] = []

    for kw in ATS_KEYWORDS:
        count = len(re.findall(r"\b" + re.escape(kw) + r"\b", text_lower))
        if count >= 1:
            matched.append(kw)
        if count > 3:
            stuffed.append(kw)

    return {
        "matched": matched,
        "matched_count": len(matched),
        "total": len(ATS_KEYWORDS),
        "stuffed": stuffed,
        "stuffed_count": len(stuffed),
    }


def _score_keywords(text_lower: str) -> float:
    """
    Score keyword relevance, coverage, placement, and stuffing (0–100).

    Multi-factor evaluation:
      - Base coverage: how many ATS keywords are present.
      - Placement bonus: keywords near section headers score higher.
      - Stuffing penalty: same keyword appearing >3x without new context.
      - Keyword-only spam penalty: sections with only keyword lists, no prose.
    """
    details = _ats_keyword_details(text_lower)
    matched_count = details["matched_count"]
    total         = details["total"]
    stuffed_count = details["stuffed_count"]

    # ── Base Coverage Score ────────────────────────────────────────────────
    ratio = matched_count / total
    if ratio >= 0.55:
        base = 90.0
    elif ratio >= 0.40:
        base = 75.0
    elif ratio >= 0.28:
        base = 60.0
    elif ratio >= 0.18:
        base = 44.0
    elif ratio >= 0.10:
        base = 28.0
    elif ratio >= 0.05:
        base = 14.0
    else:
        base = 4.0

    # ── Placement Bonus ───────────────────────────────────────────────────
    # Keywords appearing within 100 chars of a section header score higher in real ATS
    placement_bonus = 0.0
    section_headers = re.finditer(
        r"(skills|technologies|tech stack|experience|projects|education)"
        r"\s*[:\n]",
        text_lower
    )
    for header_match in section_headers:
        nearby_text = text_lower[header_match.start(): header_match.start() + 200]
        nearby_matches = sum(
            1 for kw in ATS_KEYWORDS
            if re.search(r"\b" + re.escape(kw) + r"\b", nearby_text)
        )
        if nearby_matches >= 5:
            placement_bonus = min(placement_bonus + 8.0, 12.0)

    # ── Stuffing Penalty ──────────────────────────────────────────────────
    # Each over-repeated keyword deducts points
    stuffing_penalty = min(stuffed_count * 4.0, 20.0)

    # ── Prose Quality Check ───────────────────────────────────────────────
    # If keywords appear with no surrounding verbs or descriptive context,
    # it resembles a keyword-spam section that ATS and humans both penalize
    has_action_context = bool(re.search(
        r"\b(developed|built|implemented|designed|deployed|managed|"
        r"created|led|improved|automated|launched|delivered)\b",
        text_lower
    ))
    prose_bonus = 5.0 if has_action_context else -8.0

    final = base + placement_bonus + prose_bonus - stuffing_penalty
    return max(0.0, min(100.0, final))


def _score_sections(resume_text: str) -> float:
    """
    Score standard section structure and order (0–100).

    ATS systems expect consistent, recognizable section names.
    Sections appearing in the expected order score higher.
    """
    text_lower = resume_text.lower()
    lines      = resume_text.split("\n")

    # Map each expected section to the line it first appears on
    section_positions: dict[str, int] = {}
    for section in EXPECTED_SECTION_ORDER:
        for i, line in enumerate(lines):
            if re.search(r"\b" + re.escape(section) + r"\b", line, re.IGNORECASE):
                section_positions[section] = i
                break

    present_count = len(section_positions)
    total_count   = len(EXPECTED_SECTION_ORDER)

    # Base score for section presence
    presence_ratio = present_count / total_count
    if presence_ratio >= 0.85:
        base = 85.0
    elif presence_ratio >= 0.70:
        base = 70.0
    elif presence_ratio >= 0.55:
        base = 55.0
    elif presence_ratio >= 0.40:
        base = 38.0
    else:
        base = 20.0

    # Order bonus: check that sections appear in expected sequence
    present_ordered = sorted(section_positions.items(), key=lambda x: x[1])
    expected_order  = [s for s in EXPECTED_SECTION_ORDER if s in section_positions]
    actual_order    = [s for s, _ in present_ordered]

    order_matches = sum(
        1 for a, e in zip(actual_order, expected_order) if a == e
    )
    order_bonus = (order_matches / max(len(expected_order), 1)) * 15.0

    return min(base + order_bonus, 100.0)


def _score_contact(resume_text: str) -> float:
    """
    Score contact information completeness (0–100).
    Each contact element is individually scored — zero-based.
    """
    score = 0.0

    if extract_email(resume_text):
        score += 35.0
    if extract_phone(resume_text):
        score += 28.0
    links = extract_links(resume_text)
    if links.get("linkedin"):
        score += 22.0
    if links.get("github"):
        score += 15.0

    return min(score, 100.0)


def _score_ats_formatting(resume_text: str) -> float:
    """
    Score ATS-friendly formatting and parseability (0–100). Zero-based.

    Evaluates:
      - No complex symbols that break ATS parsers
      - Consistent date formatting
      - Clear, parseable line structure
      - No very short (< 3 char) orphan lines suggesting column/table layouts
    """
    score = 0.0
    lines = resume_text.split("\n")
    non_empty_lines = [l for l in lines if l.strip()]

    if not non_empty_lines:
        return 0.0

    # ── Start with base for any parseable text ─────────────────────────────
    score += 30.0

    # ── Symbol penalty (ATS misreads decorative characters) ───────────────
    heavy_symbols = len(re.findall(r"[★✦✓◆■▪✔➤❖◉●]", resume_text))
    if heavy_symbols > 20:
        score -= 20.0
    elif heavy_symbols > 10:
        score -= 10.0

    # ── Consistent date formatting ─────────────────────────────────────────
    standard_dates = len(re.findall(
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\.?\s+20\d\d\b",
        resume_text, re.IGNORECASE
    ))
    if standard_dates >= 2:
        score += 15.0
    elif standard_dates >= 1:
        score += 8.0

    # ── Clear section headers (title-case or all-caps short lines) ─────────
    header_lines = sum(
        1 for l in non_empty_lines
        if re.match(r"^[A-Z][a-zA-Z\s]{2,28}$", l.strip())
        and len(l.strip().split()) <= 5
    )
    if header_lines >= 5:
        score += 25.0
    elif header_lines >= 3:
        score += 15.0
    elif header_lines >= 1:
        score += 8.0

    # ── Column/table detection penalty ────────────────────────────────────
    # Very short non-empty lines suggest a multi-column layout that breaks ATS
    orphan_lines = sum(1 for l in non_empty_lines if len(l.strip()) < 4)
    orphan_ratio = orphan_lines / len(non_empty_lines)
    if orphan_ratio > 0.30:
        score -= 15.0

    # ── Reasonable line length (not wall-of-text) ──────────────────────────
    reasonable = sum(1 for l in non_empty_lines if 20 <= len(l.strip()) <= 130)
    if reasonable >= 15:
        score += 20.0
    elif reasonable >= 8:
        score += 12.0

    # ── Hyperlink / URL presence (usually parseable) ──────────────────────
    url_count = len(re.findall(r"https?://\S+", resume_text))
    if 1 <= url_count <= 6:
        score += 10.0
    elif url_count > 10:
        score -= 5.0  # Too many links may be flagged

    return max(0.0, min(100.0, score))


def _score_jd_alignment(text_lower: str, jd_lower: str) -> float:
    """
    Score keyword alignment with provided job description (0–100).

    If no JD is provided, award partial credit for generic role signals
    that most tech job postings include.
    """
    if not jd_lower:
        # No JD — award partial credit for general tech role signals
        generic_signals = [
            "python", "java", "javascript", "sql", "docker", "git",
            "api", "rest", "agile", "linux",
        ]
        matched = sum(1 for kw in generic_signals if kw in text_lower)
        return min((matched / len(generic_signals)) * 70.0, 60.0)

    # Extract multi-word and single-word terms from JD
    jd_terms = set(re.findall(r"\b[a-z][a-z0-9.+#\-]{2,}\b", jd_lower))
    resume_terms = set(re.findall(r"\b[a-z][a-z0-9.+#\-]{2,}\b", text_lower))

    # Filter out stopwords
    stopwords = {
        "and", "the", "for", "with", "from", "this", "that", "are", "you",
        "our", "will", "have", "your", "all", "has", "can", "its", "use",
        "not", "but", "any", "who", "how", "she", "his", "her",
    }
    jd_terms    = jd_terms - stopwords
    resume_terms = resume_terms - stopwords

    if not jd_terms:
        return 50.0

    overlap = jd_terms & resume_terms
    coverage = len(overlap) / len(jd_terms)

    if coverage >= 0.60:
        return 92.0
    elif coverage >= 0.45:
        return 78.0
    elif coverage >= 0.30:
        return 62.0
    elif coverage >= 0.18:
        return 46.0
    elif coverage >= 0.10:
        return 30.0
    else:
        return 12.0


def _score_readability(resume_text: str) -> float:
    """
    Score basic text readability for ATS (0–100).
    Evaluates word count — too sparse or too long both reduce ATS confidence.
    Zero-based.
    """
    word_count = len(resume_text.split())

    if 280 <= word_count <= 650:
        return 100.0   # Sweet spot for a one-page tech resume
    elif 200 <= word_count <= 850:
        return 75.0    # Slightly outside range but still parseable
    elif 120 <= word_count <= 1000:
        return 50.0    # Noticeably short or long
    elif word_count < 80:
        return 10.0    # Too sparse — likely incomplete
    else:
        return 30.0    # Very long — may trigger page-limit warnings
