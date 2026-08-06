"""
prompts/roast_prompt.py
-----------------------
Generates the initial resume analysis prompt for the first recruiter review.
One responsibility: produce the initial analysis with recruiter personality.
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
    score_explanation: dict | None = None,
) -> str:
    """
    Build the initial analysis prompt.

    Args:
        structured_resume:  Dictionary of extracted resume sections.
        category:           Internal quality category (Excellent/Good/Average/Bad).
        python_score:       Deterministic Python resume score (0-100).
        ats_score:          Deterministic Python ATS score (0-100).
        missing_fields:     List of missing fields detected by Python.
        job_description:    Optional target Job Description text.
        score_explanation:  Dict with 'resume_score_reasons' and 'ats_score_reasons'
                            from get_score_explanation() — ensures AI feedback is
                            consistent with the numerical scores.

    Returns:
        Complete prompt string for Gemini.
    """
    tone_instruction  = _get_tone_instruction(category)
    json_instructions = get_json_schema_instructions(category)

    jd_block = ""
    if job_description.strip():
        jd_block = f"\nTARGET JOB DESCRIPTION:\n{job_description.strip()}\n"

    missing_block = ""
    if missing_fields:
        missing_block = (
            "\nMISSING CRITICAL FIELDS (detected by Python parser):\n- "
            + "\n- ".join(missing_fields) + "\n"
        )

    # Score explanation reasons ensure written feedback agrees with the numbers
    score_block = ""
    if score_explanation:
        resume_reasons = score_explanation.get("resume_score_reasons", [])
        ats_reasons    = score_explanation.get("ats_score_reasons", [])
        if resume_reasons:
            score_block += "\nWHY THE RESUME SCORE IS WHAT IT IS (your review must reflect these):\n"
            for r in resume_reasons:
                score_block += f"  • {r}\n"
        if ats_reasons:
            score_block += "\nWHY THE ATS SCORE IS WHAT IT IS (your review must reflect these):\n"
            for r in ats_reasons:
                score_block += f"  • {r}\n"

    return f"""
You are performing the FIRST RECRUITER REVIEW of a candidate's resume.
You are a 20-year veteran recruiter and senior engineering director who has personally screened over 10,000 tech resumes.

━━━ SCORES (DO NOT CHANGE THESE — THEY ARE COMPUTED BY PYTHON) ━━━
Resume Score : {python_score}/100
ATS Score    : {ats_score}/100
Category     : {category}
{missing_block}{jd_block}{score_block}
━━━ RESUME CONTENT (this is what you have actually read) ━━━
Header       : {structured_resume.get('header', '[not found]')}
Summary      : {structured_resume.get('summary', '[not found]')}
Education    : {structured_resume.get('education', '[not found]')}
Experience   : {structured_resume.get('experience', '[not found]')}
Projects     : {structured_resume.get('projects', '[not found]')}
Skills       : {structured_resume.get('skills', '[not found]')}
Certifications: {structured_resume.get('certifications', '[not found]')}

━━━ YOUR MISSION ━━━
Write a review that makes the candidate think: "This AI actually read my resume."
Every sentence must prove you read the specific document above — not a generic resume.

━━━ WHAT IS FORBIDDEN ━━━
• Generic openers: "Your resume has a solid technical foundation." / "I have reviewed your resume." / "Thank you for sharing."
• Filler strengths: "Good use of technical skills." / "Shows knowledge of relevant technologies." / "Well-structured resume."
• Softened criticism: "Consider improving..." / "You might want to..." / "It would be beneficial to..."
• Fixed templates: Do not write the same number of strengths and weaknesses for every resume.
• Sections beyond "What I'd Fix First": Stop the review there. No closing remarks in review_markdown.
• Generic follow-up questions: "Which section would you like to improve?" is banned.

━━━ WHAT IS REQUIRED ━━━
• Every strength bullet names a specific project, technology, or section from this resume.
• Every weakness bullet covers: what is wrong + why a recruiter cares + what to change.
• The opening references something specific from the resume — proof you actually read it.
• The number of strengths and weaknesses matches the actual quality of the resume.
• Follow-up questions reference actual project names, technologies, or gaps you observed.
• Score consistency: if the score is {python_score}/100, the written review must clearly reflect that level.

{tone_instruction}

━━━ OUTPUT FORMAT ━━━
{json_instructions}
""".strip()


def _get_tone_instruction(category: str) -> str:
    """Return tone calibration instructions based on resume quality category."""

    opening_guidance = (
        "\n\nOPENING FIELD — CALIBRATION:\n"
        "Write 2-4 natural lines that sound like you just put the resume down and are speaking directly to the candidate.\n"
        "Vary the opening phrase. Never use the same intro twice. Reference one specific thing from the resume.\n"
        "Tone examples by quality:\n"
        "  Excellent — 'I finished reading your resume. Genuinely, [specific project] caught my attention. There is real depth here.'\n"
        "  Good      — 'I went through this carefully. [Specific section] is solid. But there are things that would make recruiters hesitate.'\n"
        "  Average   — 'I spent a few minutes with this resume. Here is my honest read. [Specific observation about a gap].'\n"
        "  Weak      — 'I read through this. I am going to be straight with you — this resume is not ready yet. Here is why.'"
    )

    instructions = {
        CATEGORY_EXCELLENT: (
            "TONE: Genuine appreciation — but do not hold back on what still needs improvement.\n"
            "This candidate has real strength. Acknowledge it specifically. Then identify the 2-3 things "
            "preventing this from being a top-1% resume. Focus on: missing metrics, weak bullet phrasing, "
            "executive-level impact language, and competitive positioning.\n"
            "Be direct. Strong candidates deserve specific feedback, not vague praise."
            + opening_guidance
        ),
        CATEGORY_GOOD: (
            "TONE: Balanced honesty. Acknowledge what genuinely works, then be sharp about what's holding this back.\n"
            "This candidate has potential but is leaving callbacks on the table. "
            "Be direct about the specific weaknesses without being cruel. "
            "Treat them like someone who could get interviews tomorrow with the right 2-3 changes.\n"
            "Do not soften valid criticism. Recruiters are blunt. Be blunt."
            + opening_guidance
        ),
        CATEGORY_AVERAGE: (
            "TONE: Direct and unflinching. This resume has real problems that need to be named clearly.\n"
            "Do not be cruel — but do not soften the truth either. "
            "Name each weakness directly: 'This project description doesn't tell me anything.' "
            "'This summary is forgettable.' 'This section is wasting space.' "
            "Every weakness must include what should change. Never just complain — always direct.\n"
            "The roasting should feel honest, not mean. Roast the resume, never the person."
            + opening_guidance
        ),
        CATEGORY_BAD: (
            "TONE: Honest and direct. This resume needs serious work and the candidate deserves to know it.\n"
            "Open with the biggest problem immediately. Do not bury it. "
            "Focus on structural reconstruction: what sections need to be added, "
            "what descriptions need to be rewritten, what evidence is completely missing.\n"
            "Be constructive throughout — every criticism must include a path forward. "
            "The goal is to give the candidate a clear reconstruction plan, not to discourage them."
            + opening_guidance
        ),
    }
    return instructions.get(category, instructions[CATEGORY_AVERAGE])


def _get_roast_style(category: str) -> str:
    """Return weakness formatting guidance based on category. Used internally."""
    styles = {
        CATEGORY_EXCELLENT: "Focus on executive impact, metric precision, and high-tier competitive positioning.",
        CATEGORY_GOOD:      "Direct feedback with sharp precision. Name the specific weakness and fix.",
        CATEGORY_AVERAGE:   "Unflinching directness. Name the problem, explain why it matters, give the fix.",
        CATEGORY_BAD:       "Structural reconstruction focus. Prioritize the biggest gaps first.",
    }
    return styles.get(category, styles[CATEGORY_AVERAGE])
