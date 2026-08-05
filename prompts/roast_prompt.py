"""
prompts/roast_prompt.py
-----------------------
Generates the initial resume analysis prompt.
Takes resume text and internal category as input.
Instructs the AI to produce score, ATS, strengths, weaknesses, and feedback.
One responsibility: initial analysis with personality-driven roasting.
"""

from config import (
    CATEGORY_EXCELLENT,
    CATEGORY_GOOD,
    CATEGORY_AVERAGE,
    CATEGORY_BAD,
)


from prompts.json_schema import get_json_schema_instructions


def get_roast_prompt(
    structured_resume: dict,
    category: str,
    python_score: int,
    ats_score: int,
    missing_fields: list[str],
    job_description: str = "",
) -> str:
    """
    Build the initial analysis prompt passing Python deterministic scores and context.

    Args:
        structured_resume: Dictionary of extracted resume sections.
        category:          Internal quality category (Excellent/Good/Average/Bad).
        python_score:      Deterministic Python resume score.
        ats_score:         Deterministic Python ATS score.
        missing_fields:    List of missing fields detected by Python.
        job_description:   Optional target Job Description text.

    Returns:
        A complete JSON-formatted prompt string for Gemini.
    """
    tone_instruction = _get_tone_instruction(category)
    json_instructions = get_json_schema_instructions()

    jd_block = ""
    if job_description.strip():
        jd_block = f"\nTARGET JOB DESCRIPTION:\n{job_description.strip()}\n"

    missing_block = ""
    if missing_fields:
        missing_block = f"\nMISSING CRITICAL FIELDS DETECTED BY PYTHON:\n- " + "\n- ".join(missing_fields) + "\n"

    return f"""
You are performing an EXHAUSTIVE INITIAL ANALYSIS of the candidate's resume.
Act with the rigor and analytical depth of top AI models (ChatGPT, Claude, Grok) and the personality of a 20-year veteran recruiter.

DETERMINISTIC SCORE BASELINES (COMPUTED BY PYTHON):
- Baseline Resume Score: {python_score}/100
- Baseline ATS Score: {ats_score}/100
- Quality Category: {category}
{missing_block}{jd_block}
EXTRACTED RESUME SECTIONS:
- Header: {structured_resume.get('header', '')}
- Summary: {structured_resume.get('summary', '')}
- Education: {structured_resume.get('education', '')}
- Projects: {structured_resume.get('projects', '')}
- Experience: {structured_resume.get('experience', '')}
- Skills: {structured_resume.get('skills', '')}
- Certifications: {structured_resume.get('certifications', '')}

TONE & BEHAVIOR INSTRUCTION:
{tone_instruction}

{json_instructions}
""".strip()


def _get_tone_instruction(category: str) -> str:
    """Return tone-specific instructions based on category."""
    instructions = {
        CATEGORY_EXCELLENT: (
            "This is a strong resume, but do NOT hold back. Focus on executive polish, "
            "missing quantifiable metrics, high-impact phrasing, and top-tier market standards. "
            "Even strong resumes have weak bullet points — find them and fix them."
        ),
        CATEGORY_GOOD: (
            "Use direct feedback with sharp humor. Point out weak spots, missing metrics, "
            "and missing skills without holding back. Treat them like a candidate who has potential but is sloppy."
        ),
        CATEGORY_AVERAGE: (
            "Be direct with sharp recruiter sarcasm. Point out weaknesses clearly and memorably. "
            "Expose vague descriptions, bad section layout, and missing core skills."
        ),
        CATEGORY_BAD: (
            "Unfiltered directness. This resume needs serious work. Roast terrible formatting and lack of depth, "
            "providing an immediate step-by-step turnaround plan."
        ),
    }
    return instructions.get(category, instructions[CATEGORY_AVERAGE])


def _get_roast_style(category: str) -> str:
    """Return weakness formatting guidance based on category."""
    styles = {
        CATEGORY_EXCELLENT: (
            "Focus on executive impact, metric precision, and high-tier competitive positioning."
        ),
        CATEGORY_GOOD: (
            "Mention weaknesses with directness and sharp humor."
        ),
        CATEGORY_AVERAGE: (
            "Use direct, memorable language calling out vague bullets and missing impact."
        ),
        CATEGORY_BAD: (
            "Be aggressive on weak structure and lack of metrics, followed by immediate fixes."
        ),
    }
    return styles.get(category, styles[CATEGORY_AVERAGE])


def _get_feedback_guide(category: str) -> str:
    """Return overall feedback tone guide based on category."""
    guides = {
        CATEGORY_EXCELLENT: (
            "Example tone: 'This is a strong resume foundation. Fine-tuning the bullet points with metrics "
            "and highlighting your core architectural skills will push this into top 1% territory.'"
        ),
        CATEGORY_GOOD: (
            "Example tone: 'This resume is decent but currently leaves recruiters with questions. "
            "Implementing the line-by-line bullet rewrites will make it stand out immediately.'"
        ),
        CATEGORY_AVERAGE: (
            "Example tone: 'This resume has potential, but right now it isn't showcasing your abilities effectively. "
            "Follow the bullet point rewrites and add the missing technical skills.'"
        ),
        CATEGORY_BAD: (
            "Example tone: 'This resume needs serious work before applying. "
            "Follow the turnaround plan to rebuild your project descriptions and skills section.'"
        ),
    }
    return guides.get(category, guides[CATEGORY_AVERAGE])
