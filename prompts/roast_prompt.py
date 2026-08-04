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


def get_roast_prompt(resume_text: str, category: str) -> str:
    """
    Build the initial analysis prompt based on resume text and category.

    Args:
        resume_text: The cleaned resume text.
        category:    Internal category — Excellent / Good / Average / Bad.

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    tone_instruction = _get_tone_instruction(category)

    return f"""
You are performing the INITIAL ANALYSIS of the following resume.

## RESUME CONTENT
{resume_text}

## INTERNAL QUALITY CATEGORY (for your tone only — DO NOT reveal this to the user)
Category: {category}

## TONE INSTRUCTION
{tone_instruction}

## YOUR TASK
Analyze the resume and respond in this EXACT structure. Use markdown formatting.

---

**Resume Score: [X]/100**
[One sentence explaining the score honestly]

**ATS Score: [X]/100** *(estimated)*
[One sentence on why this ATS score was given]

**Strengths**
List 3–8 genuine strengths. Only include real strengths that exist in the resume.
Format each as: • [Strength]: [brief explanation]

**Weaknesses**
List meaningful weaknesses. For each, explain WHY it is weak.
Format each as: • [Weakness]: [why it's weak]
{_get_roast_style(category)}

**Overall Feedback**
Write 3–5 lines summarizing the resume quality honestly.
{_get_feedback_guide(category)}

---

IMPORTANT RULES:
- Scores must reflect actual quality. Never make them up.
- Do NOT add sections like "Suggestions", "Roadmap", or "Improvements" yet.
- Do NOT offer to rewrite anything automatically.
- Do NOT reveal the internal category label.
- After your response, STOP. The user will ask follow-up questions.
- Vary your language. Do not repeat the same roast sentence twice.
- Every weakness must be followed by a brief hint (1 sentence) on how to fix it.
""".strip()


def _get_tone_instruction(category: str) -> str:
    """Return tone-specific instructions based on category."""
    instructions = {
        CATEGORY_EXCELLENT: (
            "Be respectful and professional. This is a strong resume. "
            "Acknowledge genuine quality. Point out only real, specific improvements. "
            "Do NOT roast unnecessarily. Keep tone encouraging but honest."
        ),
        CATEGORY_GOOD: (
            "Use light humor where appropriate. This resume is above average but has gaps. "
            "Be honest about weak spots without being harsh. "
            "Feel like a smart friend giving honest feedback — not an HR chatbot."
        ),
        CATEGORY_AVERAGE: (
            "Be direct with mild sarcasm. This is the core Resume Roaster experience. "
            "Point out weaknesses clearly and memorably. "
            "Do NOT be rude or attack the person. Roast the resume content. "
            "Every roast must immediately include a useful suggestion."
        ),
        CATEGORY_BAD: (
            "Be honest and more direct. This resume needs serious work. "
            "Do not soften the feedback unnecessarily, but NEVER be offensive or toxic. "
            "Be like a mentor who is frustrated but still wants the person to succeed. "
            "Stronger roasting is allowed, but every criticism must include a fix."
        ),
    }
    return instructions.get(category, instructions[CATEGORY_AVERAGE])


def _get_roast_style(category: str) -> str:
    """Return weakness formatting guidance based on category."""
    styles = {
        CATEGORY_EXCELLENT: (
            "Minor improvements only. Keep feedback constructive and specific."
        ),
        CATEGORY_GOOD: (
            "Mention weaknesses with light humor. Example: "
            "'Your project descriptions are decent, but some leave recruiters guessing what you actually built.'"
        ),
        CATEGORY_AVERAGE: (
            "Use direct, memorable language. Examples:\n"
            "  - 'This project description tells me almost nothing.'\n"
            "  - 'If I were a recruiter, I'd still have no idea what you built.'\n"
            "  - 'This bullet point is so vague it could describe anything.'\n"
            "Vary the language. Never repeat the same sentence."
        ),
        CATEGORY_BAD: (
            "Be more aggressive but never offensive. Examples:\n"
            "  - 'This resume is hiding your abilities instead of showing them.'\n"
            "  - 'Right now this section is doing more harm than good.'\n"
            "  - 'This description gives recruiters zero reason to call you.'\n"
            "Always follow every criticism with a clear fix."
        ),
    }
    return styles.get(category, styles[CATEGORY_AVERAGE])


def _get_feedback_guide(category: str) -> str:
    """Return overall feedback tone guide based on category."""
    guides = {
        CATEGORY_EXCELLENT: (
            "Example tone: 'This is a strong resume. Projects are well-explained and skills are relevant. "
            "Minor improvements can make it even better.'"
        ),
        CATEGORY_GOOD: (
            "Example tone: 'This resume is above average but still has room to grow. "
            "A few targeted improvements would make it stand out.'"
        ),
        CATEGORY_AVERAGE: (
            "Example tone: 'This resume has potential, but right now it isn't showcasing "
            "your abilities effectively. The pieces are here — they just need better presentation.'"
        ),
        CATEGORY_BAD: (
            "Example tone: 'This resume needs serious work before you start applying. "
            "Right now it is hiding your abilities instead of showcasing them. "
            "The good news: these problems are fixable.'"
        ),
    }
    return guides.get(category, guides[CATEGORY_AVERAGE])
