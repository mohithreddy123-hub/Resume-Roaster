"""
analyzer/strengths.py
---------------------
Identifies genuine strengths in a resume.
Only returns real strengths based on actual resume content.
Never invents strengths. If none exist, returns an empty list.
Generates 3–8 strength strings.
"""

from utils.helper import detect_sections, extract_email, extract_phone, extract_links
from config import MIN_STRENGTHS, MAX_STRENGTHS


def extract_strengths(resume_text: str) -> list[str]:
    """
    Identify genuine strengths present in the resume.

    Each strength is only included if there is actual evidence in the resume text.
    Returns 3–8 strengths maximum. Returns fewer if fewer exist.

    Args:
        resume_text: The cleaned resume text.

    Returns:
        List of strength strings. Empty list if no strengths found.
    """
    strengths: list[str] = []
    text_lower = resume_text.lower()
    sections = detect_sections(resume_text)
    links = extract_links(resume_text)

    # ── Contact completeness ──────────────────────────────────────────────────
    has_email = extract_email(resume_text) is not None
    has_phone = extract_phone(resume_text) is not None

    if has_email and has_phone and links["linkedin"] and links["github"]:
        strengths.append("Complete contact information — email, phone, LinkedIn, and GitHub all present.")
    elif has_email and has_phone:
        strengths.append("Contact information is present — email and phone included.")

    # ── GitHub presence ───────────────────────────────────────────────────────
    if links["github"]:
        strengths.append("GitHub profile is linked — shows recruiters your actual work.")

    # ── LinkedIn presence ─────────────────────────────────────────────────────
    if links["linkedin"]:
        strengths.append("LinkedIn profile is included — supports professional credibility.")

    # ── Strong skills section ─────────────────────────────────────────────────
    tech_keywords = [
        "python", "java", "javascript", "react", "node", "django", "flask",
        "sql", "mongodb", "aws", "docker", "git", "machine learning",
        "typescript", "kubernetes", "fastapi", "spring", "tensorflow"
    ]
    skill_count = sum(1 for kw in tech_keywords if kw in text_lower)
    if skill_count >= 8:
        strengths.append(f"Strong technical skill set — {skill_count}+ relevant technologies listed.")
    elif skill_count >= 5:
        strengths.append(f"Solid technical skills — {skill_count} relevant technologies mentioned.")

    # ── Education ────────────────────────────────────────────────────────────
    if sections.get("education"):
        has_degree = any(kw in text_lower for kw in [
            "b.tech", "btech", "b.e", "bachelor", "m.tech", "mtech", "master",
            "mba", "bca", "mca", "b.sc"
        ])
        has_year = __import__("re").search(r"20(1[5-9]|2[0-9])", resume_text) is not None
        if has_degree and has_year:
            strengths.append("Education section is complete — degree and graduation year are present.")
        elif has_degree:
            strengths.append("Degree is clearly mentioned in the education section.")

    # ── Projects section ──────────────────────────────────────────────────────
    if sections.get("projects"):
        import re
        project_count = len(re.findall(
            r"(built|developed|created|designed|implemented|deployed|launched)\b",
            text_lower
        ))
        if project_count >= 3:
            strengths.append(f"Multiple projects demonstrated — {project_count}+ project contributions mentioned.")
        elif project_count >= 1:
            strengths.append("Projects section is present — shows hands-on experience.")

    # ── Experience/Internship ────────────────────────────────────────────────
    if sections.get("experience"):
        has_internship = any(kw in text_lower for kw in ["intern", "internship", "trainee"])
        if has_internship:
            strengths.append("Internship experience included — demonstrates real-world exposure.")
        else:
            strengths.append("Professional experience section is present.")

    # ── Certifications ────────────────────────────────────────────────────────
    if sections.get("certifications"):
        strengths.append("Certifications listed — shows commitment to continuous learning.")

    # ── Achievements ─────────────────────────────────────────────────────────
    if sections.get("achievements"):
        strengths.append("Achievements section present — stands out from generic resumes.")

    # ── Action verbs (strong writing signal) ─────────────────────────────────
    action_verbs = ["developed", "built", "designed", "implemented", "deployed",
                    "optimized", "automated", "led", "launched", "managed"]
    action_count = sum(1 for v in action_verbs if v in text_lower)
    if action_count >= 5:
        strengths.append("Strong use of action verbs — writing is results-oriented.")

    # Cap at MAX_STRENGTHS
    return strengths[:MAX_STRENGTHS]
