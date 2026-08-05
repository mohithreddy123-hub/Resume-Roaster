"""
analyzer/score.py
-----------------
Calculates the Overall Resume Score (0–100) using weighted section scoring.
Score is based on actual resume content — never random.
Uses section weights defined in config.py.
"""

from utils.helper import detect_sections, extract_email, extract_phone, extract_links
from config import SECTION_WEIGHTS


def calculate_resume_score(resume_text: str) -> int:
    """
    Calculate the overall resume score from 0–100.

    Scoring is based on weighted sections:
        header      10%  — name, email, phone, links
        education   15%  — education section presence and detail
        projects    30%  — projects section presence and detail
        skills      20%  — skills presence and count
        experience  15%  — experience/internship presence
        formatting   5%  — basic formatting signals
        grammar      5%  — basic text quality signals

    Args:
        resume_text: The cleaned resume text.

    Returns:
        Integer score from 0 to 100.
    """
    scores: dict[str, float] = {}

    # Header score (10%)
    scores["header"] = _score_header(resume_text)

    # Education score (15%)
    scores["education"] = _score_education(resume_text)

    # Projects score (30%)
    scores["projects"] = _score_projects(resume_text)

    # Skills score (20%)
    scores["skills"] = _score_skills(resume_text)

    # Experience score (15%)
    scores["experience"] = _score_experience(resume_text)

    # Formatting score (5%)
    scores["formatting"] = _score_formatting(resume_text)

    # Grammar score (5%)
    scores["grammar"] = _score_grammar(resume_text)

    # Weighted total
    total = sum(
        (scores[section] / 100) * weight
        for section, weight in SECTION_WEIGHTS.items()
    )

    return max(0, min(100, round(total)))


def calculate_complete_metrics(resume_text: str, structured_resume: dict) -> dict:
    """
    Calculate unified mathematical metrics for the entire resume.
    Ensures 100% mathematical consistency across Resume Score, ATS Score,
    and Sub-Category Ratings (1-10).

    Career-Stage Calibration Rules:
    - Freshers/Students without industry experience are capped at 85/100 max.
    - 10/10 sub-category ratings are strictly reserved for world-class scores (>=95).
    """
    from analyzer.ats import calculate_ats_score

    resume_score = calculate_resume_score(resume_text)
    ats_score    = calculate_ats_score(resume_text)

    # Sub-category ratings (scale 1-10, derived mathematically from sub-scores)
    header_score = _score_header(resume_text)
    proj_score   = _score_projects(resume_text)
    skills_score = _score_skills(resume_text)
    edu_score    = _score_education(resume_text)
    exp_score    = _score_experience(resume_text)

    # Career-stage score cap: if no industry experience/internship, cap resume_score at 85
    has_experience = exp_score >= 50
    if not has_experience:
        resume_score = min(resume_score, 85)

    summary_text = structured_resume.get("summary", "")
    summary_rating = 8 if len(summary_text) > 40 else (5 if summary_text else 3)

    # Convert scores (0-100) to sub-category ratings (1-10) with realistic scaling
    def _to_rating(score_val: float) -> int:
        r = round(score_val / 10)
        # 10/10 requires score >= 95
        if r >= 10 and score_val < 95:
            r = 9
        return max(1, min(10, r))

    ats_rating        = _to_rating(ats_score)
    project_rating    = _to_rating(proj_score)
    skills_rating     = _to_rating(skills_score)
    summary_rating    = _to_rating(summary_rating * 10)
    placement_rating  = _to_rating(proj_score * 0.4 + skills_score * 0.4 + edu_score * 0.2)
    faang_rating      = _to_rating(proj_score * 0.4 + skills_score * 0.3 + exp_score * 0.3)

    return {
        "resume_score": resume_score,
        "ats_score": ats_score,
        "category_ratings": {
            "ats_friendliness": ats_rating,
            "project_quality": project_rating,
            "technical_skills": skills_rating,
            "professional_summary": summary_rating,
            "placement_readiness": placement_rating,
            "faang_readiness": faang_rating,
        }
    }


def _score_header(text: str) -> float:
    """Score the header section (0–100)."""
    score = 0.0
    has_email = extract_email(text) is not None
    has_phone = extract_phone(text) is not None
    links = extract_links(text)
    has_github = links["github"] is not None
    has_linkedin = links["linkedin"] is not None

    # Email is essential
    if has_email:
        score += 35
    # Phone is important
    if has_phone:
        score += 25
    # GitHub is very important for tech resumes
    if has_github:
        score += 25
    # LinkedIn is good to have
    if has_linkedin:
        score += 15

    return score


def _score_education(text: str) -> float:
    """Score the education section (0–100)."""
    text_lower = text.lower()
    score = 0.0

    # Education section exists
    if any(kw in text_lower for kw in ["education", "academics", "qualification"]):
        score += 40

    # Has degree mention
    if any(kw in text_lower for kw in ["b.tech", "btech", "b.e", "bachelor", "m.tech",
                                         "mtech", "master", "mba", "bca", "mca", "b.sc", "b.com"]):
        score += 30

    # Has graduation year
    import re
    if re.search(r"20(1[5-9]|2[0-9])", text):
        score += 20

    # Has college/university name
    if any(kw in text_lower for kw in ["university", "college", "institute", "iit", "nit", "bits"]):
        score += 10

    return min(score, 100.0)


def _score_projects(text: str) -> float:
    """Score the projects section (0–100) — highest weight as most important for freshers."""
    text_lower = text.lower()
    score = 0.0

    # Projects section exists
    if any(kw in text_lower for kw in ["project", "personal project", "academic project"]):
        score += 30

    # Count rough number of project entries (look for bullet patterns or numbered items)
    import re
    project_indicators = len(re.findall(
        r"(built|developed|created|designed|implemented|deployed|made)\b",
        text_lower
    ))
    if project_indicators >= 3:
        score += 30
    elif project_indicators >= 2:
        score += 20
    elif project_indicators >= 1:
        score += 10

    # Has GitHub links (project evidence)
    if extract_links(text)["github"]:
        score += 20

    # Has tech stack mentions in projects
    tech_keywords = ["python", "react", "node", "django", "flask", "sql", "mongodb",
                     "javascript", "java", "html", "css", "aws", "docker", "api"]
    tech_count = sum(1 for kw in tech_keywords if kw in text_lower)
    if tech_count >= 5:
        score += 20
    elif tech_count >= 3:
        score += 10
    elif tech_count >= 1:
        score += 5

    return min(score, 100.0)


def _score_skills(text: str) -> float:
    """Score the skills section (0–100)."""
    text_lower = text.lower()
    score = 0.0

    # Skills section exists
    if any(kw in text_lower for kw in ["skills", "technical skills", "technologies", "tech stack"]):
        score += 30

    # Count technical keywords as a proxy for skill depth
    tech_keywords = [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "react", "angular", "vue", "node", "django", "flask", "fastapi", "spring",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
        "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
        "html", "css", "tailwind", "bootstrap"
    ]
    skill_count = sum(1 for kw in tech_keywords if kw in text_lower)

    if skill_count >= 10:
        score += 70
    elif skill_count >= 7:
        score += 55
    elif skill_count >= 5:
        score += 40
    elif skill_count >= 3:
        score += 25
    elif skill_count >= 1:
        score += 10

    return min(score, 100.0)


def _score_experience(text: str) -> float:
    """Score experience/internship section (0–100)."""
    text_lower = text.lower()
    score = 0.0

    # Has experience or internship section
    if any(kw in text_lower for kw in ["experience", "internship", "work experience",
                                         "employment", "professional experience"]):
        score += 50

    # Has company name indicators
    if any(kw in text_lower for kw in ["pvt", "ltd", "inc", "llc", "technologies",
                                         "solutions", "systems", "services"]):
        score += 25

    # Has duration/date indicators
    import re
    if re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).{0,20}20\d\d", text_lower):
        score += 25

    return min(score, 100.0)


def _score_formatting(text: str) -> float:
    """Score basic formatting quality (0–100)."""
    score = 50.0  # Start at 50 — basic formatting assumed present

    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return 0.0

    # Penalty for very short lines (suggests poor formatting)
    short_lines = sum(1 for l in lines if len(l.strip()) < 5)
    short_ratio = short_lines / len(lines)
    if short_ratio > 0.5:
        score -= 20

    # Bonus for consistent section structure (lines that look like headers)
    import re
    header_like = sum(1 for l in lines if re.match(r"^[A-Z][a-zA-Z\s]{2,25}$", l.strip()))
    if header_like >= 4:
        score += 30
    elif header_like >= 2:
        score += 15

    # Bonus if resume isn't too short (word count)
    word_count = len(text.split())
    if word_count >= 300:
        score += 20
    elif word_count >= 150:
        score += 10
    elif word_count < 80:
        score -= 20

    return max(0.0, min(score, 100.0))


def _score_grammar(text: str) -> float:
    """Score basic grammar and readability signals (0–100)."""
    score = 60.0  # Base score — assume acceptable grammar

    # Penalty for excessive capitalization (ALL CAPS sections suggest poor formatting)
    import re
    all_caps_words = len(re.findall(r"\b[A-Z]{4,}\b", text))
    if all_caps_words > 10:
        score -= 15

    # Penalty for very long lines (no line breaks — wall of text)
    long_lines = sum(1 for line in text.split("\n") if len(line) > 200)
    if long_lines > 3:
        score -= 20

    # Bonus for action verb usage (signals professional writing)
    action_verbs = [
        "developed", "built", "created", "designed", "implemented", "led",
        "managed", "improved", "achieved", "delivered", "deployed", "launched",
        "optimized", "automated", "reduced", "increased", "collaborated"
    ]
    action_count = sum(1 for verb in action_verbs if verb in text.lower())
    if action_count >= 5:
        score += 40
    elif action_count >= 3:
        score += 25
    elif action_count >= 1:
        score += 10

    return max(0.0, min(score, 100.0))
