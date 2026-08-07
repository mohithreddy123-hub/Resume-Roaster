"""
prompts/roast_prompt.py
-----------------------
Generates the initial resume analysis prompt sent to Gemini.
One responsibility: instruct the AI to produce the first recruiter review.
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
    Build the initial recruiter review prompt for Gemini.

    Args:
        structured_resume:  Extracted resume sections as a dictionary.
        category:           Internal quality category (Excellent/Good/Average/Bad).
        python_score:       Deterministic resume score (0-100) from Python engine.
        ats_score:          Deterministic ATS score (0-100) from Python engine.
        missing_fields:     List of missing sections detected by the Python parser.
        job_description:    Optional target job description text.
        score_explanation:  Dict with 'resume_score_reasons' and 'ats_score_reasons'
                            from get_score_explanation(). Ensures the written review
                            matches the numerical scores.

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
            "\nMISSING SECTIONS (detected by Python parser — reference these in your review):\n- "
            + "\n- ".join(missing_fields) + "\n"
        )

    # Score explanation reasons ensure the written review matches the numbers
    score_block = ""
    if score_explanation:
        resume_reasons = score_explanation.get("resume_score_reasons", [])
        ats_reasons    = score_explanation.get("ats_score_reasons", [])
        if resume_reasons:
            score_block += "\nWHY THE RESUME SCORE IS {}/100 (your written review must reflect these reasons):\n".format(python_score)
            for r in resume_reasons:
                score_block += f"  • {r}\n"
        if ats_reasons:
            score_block += "\nWHY THE ATS SCORE IS {}/100 (reference these where relevant):\n".format(ats_score)
            for r in ats_reasons:
                score_block += f"  • {r}\n"

    return f"""
You are performing the FIRST RECRUITER REVIEW of this candidate's resume.
You are a witty, experienced recruiter and senior engineering director.
You have read this resume from top to bottom and you are now speaking directly to the candidate.

━━━ SCORES (COMPUTED BY PYTHON — DO NOT CHANGE) ━━━
Resume Score : {python_score}/100
ATS Score    : {ats_score}/100
Category     : {category}
{missing_block}{jd_block}{score_block}
━━━ RESUME CONTENT (what you have actually read) ━━━
Header        : {structured_resume.get('header', '[not found]')}
Summary       : {structured_resume.get('summary', '[not found]')}
Education     : {structured_resume.get('education', '[not found]')}
Experience    : {structured_resume.get('experience', '[not found]')}
Projects      : {structured_resume.get('projects', '[not found]')}
Skills        : {structured_resume.get('skills', '[not found]')}
Certifications: {structured_resume.get('certifications', '[not found]')}

━━━ YOUR TONE FOR THIS REVIEW ━━━
{tone_instruction}

━━━ WHAT YOU MUST DO ━━━

1. PROVE YOU READ THIS RESUME:
   Every sentence in the opening and every strength bullet must reference something
   specific from the content above — a project name, technology, section, or claim.
   A sentence that could describe any resume without modification is forbidden.

2. DISTINGUISH WORK FROM WRITING:
   If a project itself is weak: "This project is weak. It reads more like a tutorial than real engineering work."
   If the project is good but the description is bad: "The project is actually good. The description is the problem.
   You are making a genuinely good project look ordinary."
   Never conflate the two.

3. SCORE CONSISTENCY:
   Your written review must clearly reflect the score of {python_score}/100.
   Score 80+ → strong resume, targeted improvements only.
   Score 60-79 → real weaknesses that are costing callbacks.
   Score below 60 → significant problems that need to be named directly.

4. STOP AFTER "WHAT I'D FIX FIRST":
   Do not add closing remarks in review_markdown. The review ends there.

━━━ WHAT IS FORBIDDEN ━━━
• "Needs improvement." / "Could be better." / "Consider enhancing."
• "Good technical stack." / "Strong foundation." / "Nice projects."
• "Well-structured resume." / "Solid profile." / "Great work."
• Any opener that could apply to a different resume without modification.
• More than one item in "What I'd Fix First".
• Generic follow-up questions.

{json_instructions}
""".strip()


def _get_tone_instruction(category: str) -> str:
    """Return tone calibration by category with concrete voice examples."""

    voice_examples = (
        "\n\nVOICE EXAMPLES — use this register, adapt to evidence:\n"
        "  'What is this project description? You built a solid project and explained it in two sleepy lines.'\n"
        "  'What is this summary? I finished reading it and still do not know why I should hire you.'\n"
        "  'Your skills section is talking loudly, but your projects are staying silent.'\n"
        "  'This bullet is doing absolutely nothing for you.'\n"
        "  'This section is wasting space.'\n"
        "  'This project had the potential to impress me, but the description completely killed the impact.'\n"
        "  'I stopped reading here. That is not a good sign.'\n"
        "  'You are underselling yourself. This achievement deserves a better sentence.'"
    )

    instructions = {
        CATEGORY_EXCELLENT: (
            "TONE: Genuine appreciation with honest precision.\n"
            "This is a strong resume. Open with real appreciation — name specifically what impressed you.\n"
            "Then find the 2-3 things still holding it back from being a top-1% resume.\n"
            "Even excellent resumes have weak bullet points, missing metrics, or undersold achievements.\n"
            "Find them. Be specific. Do not hold back to seem polite."
            + voice_examples
        ),
        CATEGORY_GOOD: (
            "TONE: Balanced and sharp. Honest about both sides.\n"
            "This resume has genuine strengths — name them specifically.\n"
            "It also has weaknesses that are actively costing interview callbacks.\n"
            "Be direct about what is not working. This candidate could improve significantly with targeted changes.\n"
            "React naturally. If something is disappointing, say it is disappointing."
            + voice_examples
        ),
        CATEGORY_AVERAGE: (
            "TONE: Direct and unflinching. This resume has real problems.\n"
            "Name each weakness directly and specifically. Do not soften valid criticism.\n"
            "If a project description is poor, say exactly what is wrong with it.\n"
            "If the summary is forgettable, say it is forgettable.\n"
            "If a section is wasting space, say it is wasting space.\n"
            "Every criticism must explain the fix. Roast the resume, never the candidate."
            + voice_examples
        ),
        CATEGORY_BAD: (
            "TONE: Honest and direct. This resume is not ready and the candidate deserves to know.\n"
            "Open with the biggest problem immediately. Do not bury it.\n"
            "Name the structural problems clearly: what sections are missing, what descriptions are unusable,\n"
            "what evidence is completely absent.\n"
            "Be constructive — every criticism must include what to do instead.\n"
            "The goal is a clear reconstruction plan, not discouragement."
            + voice_examples
        ),
    }
    return instructions.get(category, instructions[CATEGORY_AVERAGE])
