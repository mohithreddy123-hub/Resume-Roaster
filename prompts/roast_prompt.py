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


def get_roast_prompt(
    resume_text: str, category: str, job_description: str = ""
) -> str:
    """
    Build the initial analysis prompt based on resume text, category, and optional target Job Description.

    Args:
        resume_text:     The cleaned resume text.
        category:        Internal category — Excellent / Good / Average / Bad.
        job_description: Optional target Job Description text.

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    tone_instruction = _get_tone_instruction(category)

    jd_block = ""
    if job_description.strip():
        jd_block = f"""
## TARGET JOB DESCRIPTION
{job_description.strip()}

CRITICAL INSTRUCTION FOR SCORING & MATCHING:
Evaluate the resume SPECIFICALLY against this Job Description.
Score match, keyword alignment, required experience, and skill fit for this specific position.
Highlight missing tools or requirements from this Job Description.
"""

    return f"""
You are performing an EXHAUSTIVE INITIAL ANALYSIS of the following resume.
Act with the rigor and detail of top AI models (ChatGPT, Claude, Grok) and the authority of a 20-year veteran recruiter.

## RESUME CONTENT
{resume_text}
{jd_block}
## INTERNAL QUALITY CATEGORY (for your tone only — DO NOT reveal this to the user)
Category: {category}

## TONE INSTRUCTION
{tone_instruction}

## YOUR TASK
Analyze the resume thoroughly and respond in this EXACT structure. Use markdown formatting. Do NOT hold back on any section.

---

**Resume Score: [X]/100**
[One sentence explaining the score honestly based on candidate quality and role fit]

**ATS Score: [X]/100** *(estimated)*
[One sentence on why this ATS score was given based on formatting, parsing, and keywords]

**First Impression & Executive Summary**
[2–3 sentences giving a high-level recruiter perception of the candidate]

**Strengths**
List 3–6 genuine strengths. Only include real achievements and well-written sections.
Format each as: • [Strength]: [brief explanation]

**Weaknesses, Red Flags & Bad Placements**
List 3–6 critical weaknesses or poor section placements (even if the resume is good!). Explain WHY each is a problem.
Format each as: • [Weakness/Red Flag]: [why it's problematic] → *Fix: [how to fix it]*

**Line-by-Line Bullet Point Audit**
Identify 2–4 specific weak or vague bullet points from the resume. Quote them directly and show how to rewrite them with metrics.
Format each as:
• **Original Bullet**: "[quote weak bullet from resume]"
  • **Problem**: [vague language, missing metrics, weak verb, etc.]
  • **Better Version**: "[suggested strong rewritten bullet with metrics/impact]"

**Skill Depth & Market Alignment**
• **Skills to Keep/Highlight**: [List 3–5 of the candidate's strongest relevant skills]
• **Missing / Recommended Skills**: [List 3–5 critical market or JD skills missing from the resume, e.g. Docker, CI/CD, AWS, specific frameworks]
• **Project & Skill Alignment**: [Point out technologies mentioned in projects that were omitted from the Skills section, or vice versa]

**Overall Feedback**
Write 3–5 lines summarizing the turnaround strategy for this candidate.
{_get_feedback_guide(category)}

---

IMPORTANT RULES:
- Assign honest, realistic scores ([X] MUST be an integer between 0 and 100). Do not default to high scores unless earned.
- NEVER skip the Weaknesses or Line-by-Line Audit sections, even if the resume scores above 80/100!
- Do NOT reveal the internal category label.
- After your response, STOP. The user will ask follow-up questions.
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
