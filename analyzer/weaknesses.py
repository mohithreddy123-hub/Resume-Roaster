"""
analyzer/weaknesses.py
----------------------
Identifies meaningful weaknesses in a resume.
Each weakness includes WHY it is weak.
Only flags weaknesses that are genuinely present — never invents problems.
"""

from dataclasses import dataclass
from utils.helper import detect_sections, extract_email, extract_phone, extract_links
from config import MAX_WEAKNESSES


@dataclass
class Weakness:
    """
    Represents a single resume weakness.

    Attributes:
        label:  Short name of the weakness.
        reason: Why this is a weakness — shown to the user.
    """
    label: str
    reason: str


def extract_weaknesses(resume_text: str) -> list[Weakness]:
    """
    Identify meaningful weaknesses in the resume.

    Each weakness is only included if there's clear evidence it exists.
    Returns up to MAX_WEAKNESSES weaknesses.

    Args:
        resume_text: The cleaned resume text.

    Returns:
        List of Weakness objects. Can be empty if the resume is strong.
    """
    weaknesses: list[Weakness] = []
    text_lower = resume_text.lower()
    sections = detect_sections(resume_text)
    links = extract_links(resume_text)

    # ── Missing contact info ──────────────────────────────────────────────────
    if not extract_email(resume_text):
        weaknesses.append(Weakness(
            label="Missing email address",
            reason="Recruiters can't contact you without an email. This is the most basic requirement."
        ))

    if not extract_phone(resume_text):
        weaknesses.append(Weakness(
            label="Missing phone number",
            reason="A phone number is essential for interview calls. Add it to your header."
        ))

    if not links["github"]:
        weaknesses.append(Weakness(
            label="No GitHub profile linked",
            reason="For a tech resume, GitHub is critical. Recruiters want to see your actual code."
        ))

    if not links["linkedin"]:
        weaknesses.append(Weakness(
            label="No LinkedIn profile",
            reason="LinkedIn adds credibility and makes it easier for recruiters to verify your background."
        ))

    # ── Missing or weak sections ──────────────────────────────────────────────
    if not sections.get("projects") and not sections.get("experience"):
        weaknesses.append(Weakness(
            label="No projects or experience",
            reason="This is the most critical gap. Without projects or experience, "
                   "there's nothing to prove your technical ability."
        ))
    elif sections.get("projects"):
        # Check if project descriptions are thin
        import re
        action_count = len(re.findall(
            r"\b(built|developed|created|designed|implemented|deployed|launched)\b",
            text_lower
        ))
        if action_count < 2:
            weaknesses.append(Weakness(
                label="Weak project descriptions",
                reason="Your project descriptions don't explain what you actually built or contributed. "
                       "Recruiters can't evaluate your skills from project names alone."
            ))

    if not sections.get("skills"):
        weaknesses.append(Weakness(
            label="Missing skills section",
            reason="ATS systems and recruiters scan for a skills section first. "
                   "Without it, your resume may be filtered out before a human reads it."
        ))
    else:
        # Check if skills section is too thin
        tech_keywords = [
            "python", "java", "javascript", "react", "node", "django",
            "sql", "mongodb", "aws", "docker", "git", "typescript"
        ]
        skill_count = sum(1 for kw in tech_keywords if kw in text_lower)
        if skill_count < 3:
            weaknesses.append(Weakness(
                label="Too few technical skills listed",
                reason=f"Only {skill_count} recognizable technical skills found. "
                       "A tech resume needs at least 5–8 relevant skills to pass ATS filters."
            ))

    if not sections.get("education"):
        weaknesses.append(Weakness(
            label="Missing education section",
            reason="For fresh graduates, education is one of the most important sections. "
                   "Recruiters expect to see your degree, college, and graduation year."
        ))
    else:
        # Check graduation year
        if not re.search(r"20(1[5-9]|2[0-9])", resume_text):
            weaknesses.append(Weakness(
                label="Graduation year not mentioned",
                reason="Recruiters want to know when you graduated. "
                       "Missing graduation year creates unnecessary confusion."
            ))

    # ── Professional summary ──────────────────────────────────────────────────
    if not sections.get("summary"):
        weaknesses.append(Weakness(
            label="No professional summary",
            reason="A strong summary is often the first thing a recruiter reads. "
                   "Without one, your resume starts cold with no introduction."
        ))

    # ── Metrics and quantification ────────────────────────────────────────────
    import re
    has_metrics = bool(re.search(r"\d+%|\d+x|\d+\s*(users|requests|records|ms|seconds|hours)", text_lower))
    if not has_metrics:
        weaknesses.append(Weakness(
            label="No metrics or quantifiable achievements",
            reason="Numbers make achievements real. "
                   "'Improved performance' means nothing. "
                   "'Reduced load time by 40%' makes recruiters pay attention."
        ))

    # ── Resume length ─────────────────────────────────────────────────────────
    word_count = len(resume_text.split())
    if word_count < 150:
        weaknesses.append(Weakness(
            label="Resume is too short",
            reason=f"Only ~{word_count} words found. A complete resume needs at least 250–400 words "
                   "to give recruiters enough information to evaluate you."
        ))

    # ── Action verbs ──────────────────────────────────────────────────────────
    action_verbs = ["developed", "built", "designed", "implemented", "deployed",
                    "optimized", "automated", "led", "launched", "managed"]
    action_count = sum(1 for v in action_verbs if v in text_lower)
    if action_count == 0:
        weaknesses.append(Weakness(
            label="No action verbs used",
            reason="Passive writing makes your resume forgettable. "
                   "Start bullet points with action verbs like Built, Developed, Designed, Led."
        ))

    return weaknesses[:MAX_WEAKNESSES]
