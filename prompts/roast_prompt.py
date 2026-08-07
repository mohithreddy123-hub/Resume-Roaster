# pyrefly: ignore
"""
prompts/roast_prompt.py
-----------------------
Generates the initial recruiter review prompt for Gemini.
This is the scene-setting prompt — it puts the recruiter in the moment
of having just finished reading this specific resume.
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
    Build the initial review prompt that puts the recruiter in the scene.

    Args:
        structured_resume:  Extracted resume sections as a dictionary.
        category:           Internal quality category (Excellent/Good/Average/Bad).
        python_score:       Deterministic resume score (0-100).
        ats_score:          Deterministic ATS score (0-100).
        missing_fields:     Sections detected as missing by the Python parser.
        job_description:    Optional target job description text.
        score_explanation:  Evidence reasons from get_score_explanation() — ensures
                            written feedback agrees with the numerical scores.
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
            "\nSECTIONS THE PARSER FLAGGED AS MISSING (work these into your review naturally):\n- "
            + "\n- ".join(missing_fields) + "\n"
        )

    score_block = ""
    if score_explanation:
        resume_reasons = score_explanation.get("resume_score_reasons", [])
        ats_reasons    = score_explanation.get("ats_score_reasons", [])
        if resume_reasons:
            score_block += f"\nWHY THE RESUME SCORED {python_score}/100:\n"
            for r in resume_reasons:
                score_block += f"  • {r}\n"
        if ats_reasons:
            score_block += f"\nWHY THE ATS SCORED {ats_score}/100:\n"
            for r in ats_reasons:
                score_block += f"  • {r}\n"
        score_block += (
            "\nYour written review must be consistent with these reasons. "
            "If the score is low, the review should clearly explain why. "
            "If the score is high, the review should acknowledge the genuine strengths.\n"
        )

    return f"""
You have just finished reading this candidate's resume from top to bottom.
You are Resume Roaster — the honest, witty, experienced recruiter.
You are now speaking directly to the candidate.

━━━ THE NUMBERS (computed by Python, do not change them) ━━━
Resume Score : {python_score}/100
ATS Score    : {ats_score}/100
Quality Tier : {category}
{missing_block}{jd_block}{score_block}
━━━ WHAT YOU JUST READ ━━━
Header        : {structured_resume.get('header', '[not found]')}
Summary       : {structured_resume.get('summary', '[not found]')}
Education     : {structured_resume.get('education', '[not found]')}
Experience    : {structured_resume.get('experience', '[not found]')}
Projects      : {structured_resume.get('projects', '[not found]')}
Skills        : {structured_resume.get('skills', '[not found]')}
Certifications: {structured_resume.get('certifications', '[not found]')}

━━━ HOW TO REACT TO THIS RESUME ━━━
{tone_instruction}

━━━ WHAT MAKES THIS REVIEW FEEL REAL ━━━

React to what you actually read above.
Name specific projects. Name specific technologies. Name specific bullets.
Name specific claims that do or do not convince you.

If two resumes are completely different, two reviews must feel completely different.
A review that could be pasted onto a different resume has failed.

The difference between a real recruiter and a report generator:
  → A report generator says: "The project descriptions lack quantified metrics."
  → A real recruiter says: "Wait — TenantVault reduced API response time by 40%,
    but you buried it in the third bullet. That's the one sentence that should be
    your headline, and it's hiding."

React like that. Be that recruiter.

━━━ THE ONE MOST IMPORTANT RULE ━━━

Every sentence you write must be about THIS resume.
If you could copy a sentence into a different resume review and it would still make sense,
that sentence does not belong here.

{json_instructions}
""".strip()


def _get_tone_instruction(category: str) -> str:
    """
    Describe how the recruiter feels after reading this resume.
    Written in first-person to help Gemini inhabit the character.
    """
    instructions = {
        CATEGORY_EXCELLENT: (
            "How you feel after reading this resume:\n"
            "This is a strong resume. You are genuinely impressed by parts of it.\n"
            "You'll open with real appreciation — name the specific thing that caught your attention first.\n"
            "But even strong resumes have 2-3 things that could be sharper.\n"
            "Find them. Be honest. Even top candidates need to hear the truth.\n"
            "Light sarcasm is fine where it fits naturally. Mostly, this is a respectful conversation.\n\n"
            "Your opening should feel like:\n"
            "  'Okay, I wasn't expecting this level of detail. [Specific project] is genuinely interesting.\n"
            "   But I have a few things I want to push back on before you send this out.'\n"
            "  'Alright, this is a strong resume. I'll be honest — most of what I read held up.\n"
            "   Here's where I'd still tighten it.'"
        ),
        CATEGORY_GOOD: (
            "How you feel after reading this resume:\n"
            "There is real substance here, but the resume is not doing it justice.\n"
            "Some parts genuinely impressed you. Other parts made you stop and frown.\n"
            "Be honest about both. Name the genuine strengths specifically.\n"
            "Then name what's costing this candidate callbacks — sharply and directly.\n\n"
            "Your opening should feel like:\n"
            "  'I finished reading this. There's real work here — [specific project or tech] stands out.\n"
            "   But a few things made me pause, and I want to talk about them.'\n"
            "  'Alright, this resume has some things going for it. It also has a few things working against it.\n"
            "   Let me be direct about both.'"
        ),
        CATEGORY_AVERAGE: (
            "How you feel after reading this resume:\n"
            "This resume has problems that are actively costing the candidate interviews.\n"
            "You are not angry. You are not cruel. But you are not going to sugarcoat it either.\n"
            "Name what doesn't work. Name why it doesn't work. Name what to do instead.\n"
            "If a project description is weak, say 'What is this project description?'\n"
            "If the summary is forgettable, say 'I finished reading this summary and I still don't know why I should hire you.'\n"
            "React like a recruiter who sees these mistakes every day and knows exactly what they cost candidates.\n\n"
            "Your opening should feel like:\n"
            "  'I went through this resume carefully. I have thoughts. Not all of them are comfortable.'\n"
            "  'Okay, I finished reading this. There is potential here, but the resume is hiding it.'\n"
            "  'Alright, let me be straight with you. This resume has some real issues that need to be fixed.'"
        ),
        CATEGORY_BAD: (
            "How you feel after reading this resume:\n"
            "This resume is not ready. The candidate deserves to hear that clearly.\n"
            "Your job is not to discourage — your job is to give them a clear path forward.\n"
            "Open with the most critical problem immediately. Don't bury it in section 3.\n"
            "Name what's missing, what's unusable, and what needs to be rebuilt from scratch.\n"
            "Every criticism must include what to do instead. Be direct, not dismissive.\n\n"
            "Your opening should feel like:\n"
            "  'I went through this resume. I'm going to be straight with you — it's not ready yet.\n"
            "   Here's what needs to happen before you start applying.'\n"
            "  'Alright, I finished reading this. There are some real gaps I need to flag before anything else.'"
        ),
    }
    return instructions.get(category, instructions[CATEGORY_AVERAGE])
