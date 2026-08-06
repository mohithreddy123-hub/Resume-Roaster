"""
analyzer/score.py
-----------------
Calculates the Overall Resume Score (0–100) using evidence-based, dynamically
weighted section scoring adapted per candidate career stage.

Design principles:
  - Every point is earned from evidence — no free base scores.
  - Career stage shifts weights only — never the maximum achievable score.
  - College name / prestige is never evaluated.
  - Score is fully independent of ATS Score.
  - get_score_explanation() produces 3-4 evidence-based reasons per score.
"""

import re
from utils.helper import extract_email, extract_phone, extract_links


# ─── Career-Stage Weight Tables ───────────────────────────────────────────────
# Weights sum to 100 for each stage.
# Career stage shifts emphasis only — no caps on the total score.

_WEIGHTS_FRESHER = {
    "header":         8,
    "education":     12,
    "projects":      35,
    "skills":        22,
    "experience":     5,
    "summary":        8,
    "quantification":10,
}

_WEIGHTS_EARLY_CAREER = {
    "header":         7,
    "education":      8,
    "projects":      25,
    "skills":        18,
    "experience":    22,
    "summary":        8,
    "quantification":12,
}

_WEIGHTS_EXPERIENCED = {
    "header":         5,
    "education":      5,
    "projects":      15,
    "skills":        15,
    "experience":    35,
    "summary":       10,
    "quantification":15,
}


def _detect_career_stage(resume_text: str) -> str:
    """
    Detect candidate career stage from resume signals.

    Returns one of: 'fresher', 'early_career', 'experienced'
    """
    text_lower = resume_text.lower()

    # Strong experience signals — multi-year industry roles
    exp_years = re.findall(
        r"(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:experience|exp)",
        text_lower
    )
    if exp_years and any(int(y) >= 3 for y in exp_years):
        return "experienced"

    # Date ranges indicating multiple roles (e.g. "Jan 2020 – Dec 2022")
    date_ranges = re.findall(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).{0,20}20\d\d",
        text_lower
    )

    # Company/employer indicators
    employer_signals = sum(
        1 for kw in ["pvt", "ltd", "inc", "llc", "technologies", "solutions",
                     "systems", "services", "corp", "company"]
        if kw in text_lower
    )

    # Internship indicators
    internship_signals = any(
        kw in text_lower
        for kw in ["internship", "intern", "apprentice", "trainee"]
    )

    if employer_signals >= 2 or len(date_ranges) >= 3:
        return "experienced"
    elif internship_signals or employer_signals >= 1 or len(date_ranges) >= 1:
        return "early_career"
    else:
        return "fresher"


def _get_weights(career_stage: str) -> dict:
    """Return the appropriate weight table for the detected career stage."""
    if career_stage == "experienced":
        return _WEIGHTS_EXPERIENCED
    elif career_stage == "early_career":
        return _WEIGHTS_EARLY_CAREER
    else:
        return _WEIGHTS_FRESHER


def calculate_resume_score(resume_text: str) -> int:
    """
    Calculate the overall Resume Score (0–100).

    Scoring is evidence-based with dynamic weights per career stage.
    No free base scores — every point must be earned from actual resume content.
    Career stage shifts weights only; it never caps the maximum achievable score.

    Args:
        resume_text: The cleaned resume text.

    Returns:
        Integer score from 0 to 100.
    """
    career_stage = _detect_career_stage(resume_text)
    weights = _get_weights(career_stage)

    sub_scores = {
        "header":         _score_header(resume_text),
        "education":      _score_education(resume_text),
        "projects":       _score_projects(resume_text),
        "skills":         _score_skills(resume_text),
        "experience":     _score_experience(resume_text),
        "summary":        _score_summary(resume_text),
        "quantification": _score_quantification(resume_text),
    }

    total = sum(
        (sub_scores[section] / 100.0) * weight
        for section, weight in weights.items()
    )

    return max(0, min(100, round(total)))


def calculate_complete_metrics(resume_text: str, structured_resume: dict) -> dict:
    """
    Calculate unified metrics: Resume Score, ATS Score, and sub-category ratings.
    Resume Score and ATS Score are computed independently — neither influences the other.
    """
    from analyzer.ats import calculate_ats_score

    resume_score = calculate_resume_score(resume_text)
    ats_score    = calculate_ats_score(resume_text)

    # Sub-category ratings (1–10) derived from individual sub-scores
    proj_score   = _score_projects(resume_text)
    skills_score = _score_skills(resume_text)
    edu_score    = _score_education(resume_text)
    exp_score    = _score_experience(resume_text)
    quant_score  = _score_quantification(resume_text)

    summary_text = structured_resume.get("summary", "")
    raw_summary  = len(summary_text) > 60

    def _to_rating(score_val: float) -> int:
        """Convert 0–100 sub-score to 1–10 rating. 10/10 requires ≥95."""
        r = round(score_val / 10)
        if r >= 10 and score_val < 95:
            r = 9
        return max(1, min(10, r))

    return {
        "resume_score": resume_score,
        "ats_score":    ats_score,
        "career_stage": _detect_career_stage(resume_text),
        "category_ratings": {
            "ats_friendliness":    _to_rating(ats_score),
            "project_quality":     _to_rating(proj_score),
            "technical_skills":    _to_rating(skills_score),
            "professional_summary":_to_rating(80.0 if raw_summary else 40.0),
            "placement_readiness": _to_rating(proj_score * 0.4 + skills_score * 0.35 + quant_score * 0.25),
            "faang_readiness":     _to_rating(proj_score * 0.35 + skills_score * 0.3 + exp_score * 0.25 + quant_score * 0.1),
        },
    }


def get_score_explanation(
    resume_text: str,
    structured_resume: dict,
    resume_score: int,
    ats_score: int,
) -> dict:
    """
    Generate 3–4 short, evidence-based reasons for both Resume Score and ATS Score.

    These reasons are injected into the Gemini prompt to ensure the written
    review is always internally consistent with the numerical scores.

    Returns:
        dict with keys 'resume_score_reasons' and 'ats_score_reasons',
        each a list of 3–4 concise evidence-based strings.
    """
    from analyzer.ats import _score_keywords, _score_sections, _score_contact, _ats_keyword_details

    text_lower     = resume_text.lower()
    career_stage   = _detect_career_stage(resume_text)
    proj_score     = _score_projects(resume_text)
    skills_score   = _score_skills(resume_text)
    quant_score    = _score_quantification(resume_text)
    exp_score      = _score_experience(resume_text)
    header_score   = _score_header(resume_text)
    edu_score      = _score_education(resume_text)
    summary_text   = structured_resume.get("summary", "")

    resume_reasons: list[str] = []
    ats_reasons:    list[str] = []

    # ── Resume Score Reasons ─────────────────────────────────────────────────

    # Projects
    if proj_score >= 75:
        resume_reasons.append("Strong project depth — multiple projects with clear tech stack and implementation detail.")
    elif proj_score >= 45:
        resume_reasons.append("Projects are present but lack depth or quantified outcomes.")
    else:
        resume_reasons.append("Project section is weak or absent — this is the biggest gap for a tech resume.")

    # Quantification
    if quant_score >= 70:
        resume_reasons.append("Bullet points contain measurable impact (numbers, percentages, outcomes).")
    elif quant_score >= 35:
        resume_reasons.append("Some metrics present, but most bullet points lack quantified impact.")
    else:
        resume_reasons.append("Zero or near-zero quantified metrics — recruiters cannot verify impact from this resume.")

    # Experience / Internship
    if career_stage == "experienced":
        if exp_score >= 70:
            resume_reasons.append("Solid industry experience with clear company names and date ranges.")
        else:
            resume_reasons.append("Experience section lacks sufficient detail for the career level.")
    elif career_stage == "early_career":
        resume_reasons.append("Internship or early-career experience detected — adds credibility but depth is limited.")
    else:
        resume_reasons.append("No industry experience or internship — project quality carries the full weight.")

    # Summary
    if len(summary_text) > 80:
        resume_reasons.append("Professional summary provides useful context and differentiation.")
    elif len(summary_text) > 20:
        resume_reasons.append("Summary is present but generic — it adds little differentiation.")
    else:
        resume_reasons.append("No professional summary — the recruiter has no immediate context for the candidate.")

    # ── ATS Score Reasons ────────────────────────────────────────────────────

    kw_details   = _ats_keyword_details(text_lower)
    section_score = _score_sections(resume_text)
    contact_score = _score_contact(resume_text)

    matched_count = kw_details["matched_count"]
    total_kw      = kw_details["total"]
    stuffed       = kw_details["stuffed_count"]

    if matched_count >= int(total_kw * 0.45):
        ats_reasons.append(f"Strong keyword coverage — {matched_count}/{total_kw} ATS-relevant terms found.")
    elif matched_count >= int(total_kw * 0.25):
        ats_reasons.append(f"Moderate keyword coverage — {matched_count}/{total_kw} ATS terms matched; several role-specific keywords missing.")
    else:
        ats_reasons.append(f"Low keyword coverage — only {matched_count}/{total_kw} ATS terms detected; likely to be filtered in automated screening.")

    if stuffed > 0:
        ats_reasons.append(f"{stuffed} keyword(s) appear excessively repeated — modern ATS systems may flag this as keyword stuffing.")

    if section_score >= 75:
        ats_reasons.append("Standard section headings (Education, Experience, Skills, Projects) detected in parseable order.")
    elif section_score >= 40:
        ats_reasons.append("Some expected section headings present but ordering or naming is non-standard — some ATS may mis-parse.")
    else:
        ats_reasons.append("Missing standard section headings — ATS systems may fail to categorize resume content correctly.")

    if contact_score >= 80:
        ats_reasons.append("Contact information complete — email, phone, and profile links all present.")
    elif contact_score >= 50:
        ats_reasons.append("Contact information partially complete — one or more profile links (LinkedIn, GitHub) are missing.")
    else:
        ats_reasons.append("Critical contact information missing — ATS cannot route the application correctly.")

    return {
        "resume_score_reasons": resume_reasons[:4],
        "ats_score_reasons":    ats_reasons[:4],
    }


# ─── Individual Subscorers ────────────────────────────────────────────────────
# All subscorers start at 0.0 — no free base points.


def _score_header(text: str) -> float:
    """Score contact header completeness (0–100). Zero-based — all points earned."""
    score = 0.0
    if extract_email(text):
        score += 30.0
    if extract_phone(text):
        score += 22.0
    links = extract_links(text)
    if links.get("github"):
        score += 28.0
    if links.get("linkedin"):
        score += 15.0
    # Portfolio / personal site bonus
    if links.get("portfolio") or re.search(r"https?://(?!github|linkedin)\S+", text):
        score += 5.0
    return min(score, 100.0)


def _score_education(text: str) -> float:
    """
    Score education section completeness (0–100). Zero-based.
    College name and prestige are NEVER evaluated — only completeness of information.
    """
    text_lower = text.lower()
    score = 0.0

    # Education section exists
    if any(kw in text_lower for kw in ["education", "academics", "qualification", "academic background"]):
        score += 30.0

    # Degree type mentioned
    if any(kw in text_lower for kw in [
        "b.tech", "btech", "b.e", "bachelor", "m.tech", "mtech", "master",
        "mba", "bca", "mca", "b.sc", "bsc", "b.com", "phd", "ph.d",
        "be ", "me ", "ms ", "msc",
    ]):
        score += 30.0

    # Graduation year present
    if re.search(r"20(1[5-9]|2[0-9])", text):
        score += 25.0

    # CGPA / GPA / percentage mentioned
    if re.search(r"(cgpa|gpa|percentage|marks)[:\s]*[\d.]+", text_lower):
        score += 15.0

    return min(score, 100.0)


def _score_projects(text: str) -> float:
    """Score projects section quality (0–100). Zero-based."""
    text_lower = text.lower()
    score = 0.0

    # Projects section heading
    if any(kw in text_lower for kw in ["project", "personal project", "academic project", "key project"]):
        score += 15.0

    # Count action verbs indicating project implementation depth
    action_matches = len(re.findall(
        r"\b(built|developed|created|designed|implemented|deployed|launched|"
        r"integrated|architected|engineered|automated|optimized|migrated|"
        r"containerized|scaled|published|shipped)\b",
        text_lower
    ))
    if action_matches >= 6:
        score += 30.0
    elif action_matches >= 4:
        score += 22.0
    elif action_matches >= 2:
        score += 14.0
    elif action_matches >= 1:
        score += 6.0

    # GitHub project links (evidence of real work)
    github_links = len(re.findall(r"github\.com/\S+", text_lower))
    if github_links >= 3:
        score += 20.0
    elif github_links >= 1:
        score += 12.0

    # Deployment / live evidence
    if any(kw in text_lower for kw in ["deployed", "live", "production", "heroku", "vercel", "netlify", "railway", "aws", "gcp", "azure"]):
        score += 15.0

    # Tech stack depth (distinct relevant technologies)
    tech_keywords = [
        "python", "react", "node", "django", "flask", "fastapi", "spring",
        "sql", "mongodb", "postgresql", "redis", "kafka", "rabbitmq",
        "javascript", "typescript", "java", "golang", "rust", "c++",
        "docker", "kubernetes", "ci/cd", "aws", "gcp", "azure",
        "machine learning", "tensorflow", "pytorch", "rest api", "graphql",
    ]
    tech_count = sum(1 for kw in tech_keywords if kw in text_lower)
    if tech_count >= 8:
        score += 20.0
    elif tech_count >= 5:
        score += 13.0
    elif tech_count >= 3:
        score += 7.0
    elif tech_count >= 1:
        score += 3.0

    return min(score, 100.0)


def _score_skills(text: str) -> float:
    """Score technical skills section (0–100). Zero-based."""
    text_lower = text.lower()
    score = 0.0

    # Skills section exists
    if any(kw in text_lower for kw in ["skills", "technical skills", "technologies", "tech stack", "core competencies"]):
        score += 20.0

    tech_keywords = [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "react", "angular", "vue", "node", "django", "flask", "fastapi", "spring",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "terraform",
        "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy",
        "html", "css", "tailwind", "bootstrap", "graphql", "rest api", "microservices",
        "kafka", "rabbitmq", "ci/cd", "jenkins", "github actions",
    ]
    skill_count = sum(1 for kw in tech_keywords if kw in text_lower)

    # Calibrated points — diminishing returns after a point to avoid inflation
    if skill_count >= 15:
        score += 80.0
    elif skill_count >= 12:
        score += 70.0
    elif skill_count >= 9:
        score += 58.0
    elif skill_count >= 6:
        score += 44.0
    elif skill_count >= 4:
        score += 30.0
    elif skill_count >= 2:
        score += 18.0
    elif skill_count >= 1:
        score += 8.0

    return min(score, 100.0)


def _score_experience(text: str) -> float:
    """Score experience / internship section (0–100). Zero-based."""
    text_lower = text.lower()
    score = 0.0

    # Section heading
    if any(kw in text_lower for kw in [
        "experience", "internship", "work experience",
        "employment", "professional experience", "work history",
    ]):
        score += 30.0

    # Company / employer name signals
    company_signals = sum(
        1 for kw in ["pvt", "ltd", "inc", "llc", "technologies", "solutions",
                     "systems", "services", "corp", "company"]
        if kw in text_lower
    )
    if company_signals >= 2:
        score += 30.0
    elif company_signals >= 1:
        score += 18.0

    # Date ranges (signals real employment)
    date_matches = re.findall(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).{0,20}20\d\d",
        text_lower
    )
    if len(date_matches) >= 3:
        score += 25.0
    elif len(date_matches) >= 1:
        score += 15.0

    # Role / title mentions
    if any(kw in text_lower for kw in [
        "software engineer", "developer", "intern", "analyst", "consultant",
        "manager", "lead", "architect", "devops", "sde ", "sde1", "sde2",
    ]):
        score += 15.0

    return min(score, 100.0)


def _score_summary(text: str) -> float:
    """Score professional summary / objective quality (0–100). Zero-based."""
    text_lower = text.lower()
    score = 0.0

    # Summary section exists
    has_summary = any(kw in text_lower for kw in [
        "summary", "profile", "about me", "objective",
        "professional summary", "career objective",
    ])
    if not has_summary:
        return 0.0
    score += 25.0

    # Find and evaluate actual summary text length
    summary_match = re.search(
        r"(summary|profile|about me|objective|professional summary|career objective)"
        r"[:\s]+([\s\S]{20,500}?)(?=\n[A-Z]|\Z)",
        text, re.IGNORECASE
    )
    if summary_match:
        summary_text = summary_match.group(2).strip()
        word_count = len(summary_text.split())
        if word_count >= 50:
            score += 50.0
        elif word_count >= 25:
            score += 35.0
        elif word_count >= 10:
            score += 20.0

        # Contains specific technology or role mentions (not generic)
        specific_signals = sum(
            1 for kw in ["backend", "frontend", "fullstack", "data", "ml",
                         "ai", "cloud", "devops", "python", "java", "react"]
            if kw in summary_text.lower()
        )
        if specific_signals >= 2:
            score += 25.0
        elif specific_signals >= 1:
            score += 12.0

    return min(score, 100.0)


def _score_quantification(text: str) -> float:
    """
    Score quantification quality — measures whether bullet points contain
    numbers, percentages, or measurable outcomes (0–100). Zero-based.
    No metrics = significant penalty from career-weighted total.
    """
    score = 0.0

    # Count all numeric evidence patterns in bullet points
    # Percentages: 40%, 3x, 2x
    percentage_matches = len(re.findall(r"\d+(\.\d+)?%|\d+x\b|\d+X\b", text))
    # Raw numbers with context (not just years)
    metric_matches = len(re.findall(
        r"\b\d{2,}(?:\+)?\s*(?:users?|requests?|transactions?|queries?|"
        r"records?|ms\b|seconds?|hours?|days?|calls?|customers?|"
        r"products?|features?|services?|endpoints?|lines?|tests?)\b",
        text, re.IGNORECASE
    ))
    # Dollar / revenue mentions
    revenue_matches = len(re.findall(r"\$[\d,.]+|\d+[kKmM]\b", text))

    total_metrics = percentage_matches + metric_matches + revenue_matches

    if total_metrics >= 8:
        score = 95.0
    elif total_metrics >= 5:
        score = 80.0
    elif total_metrics >= 3:
        score = 62.0
    elif total_metrics >= 2:
        score = 45.0
    elif total_metrics >= 1:
        score = 28.0
    else:
        score = 0.0   # Zero metrics = 0 on this dimension

    return score
