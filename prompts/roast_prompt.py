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
You are performing an EXHAUSTIVE, HIGHLY DETAILED INITIAL ANALYSIS of the following resume.
Act with the rigor, depth, and exact structure of top AI models (ChatGPT, Claude, Grok) and the authority of a 20-year veteran recruiter.

## RESUME CONTENT
{resume_text}
{jd_block}
## INTERNAL QUALITY CATEGORY (for your tone only — DO NOT reveal this to the user)
Category: {category}

## TONE INSTRUCTION
{tone_instruction}

## YOUR TASK
Analyze the resume thoroughly and respond in this EXACT structure. Use markdown formatting.

---

**Resume Score: [X]/100**
[One sentence explaining the overall score honestly]

**ATS Score: [X]/100** *(estimated)*
[One sentence explaining the ATS friendliness score]

I went through your resume carefully. Overall, this is a [brief 2-sentence summary of candidate level, core stack, and target role suitability].

### Overall Rating

| Category | Rating |
| --- | ---: |
| ATS Friendliness | **[X]/10** |
| Project Quality | **[X]/10** |
| Technical Skills | **[X]/10** |
| Professional Summary | **[X]/10** |
| Freshers / Placement Readiness | **[X]/10** |
| FAANG / Top Product Companies | **[X]/10** |

---

## What is Very Good

### 1. [Key Strength Title 1] ⭐⭐⭐⭐⭐
[Detailed explanation of why this section is strong, quoting good bullet points from the resume]

### 2. [Key Strength Title 2]
[Detailed explanation, highlighting impact metrics or good phrasing]

### 3. [Key Strength Title 3]
[Detailed explanation of stack or project uniqueness]

---

## Things I Would Improve

### 1. Professional Summary (or Intro Section)
Current:
> "[Quote current summary or intro text from resume]"

It's good, but it could be even more targeted. For example:
> "[Exact rewritten version of the summary tailored for their target role]"

### 2. Technical Skills & Ordering
Current order: [List current order of skills section]
Suggested improvement:
[List improved ordering and grouping to highlight core stack]

### 3. Bullet Point & Metrics Audit
Current:
> "[Quote weak or vague bullet point from resume]"

Suggested Rewrite:
> "[Exact rewritten bullet point with quantifiable metrics, impact, and strong action verbs]"

### 4. Experience / Projects / Education Tweaks
[Detailed specific improvements for remaining sections, pointing out vague parts or missing details]

---

## Things Recruiters Will Notice (First 15–20 Seconds)

Within 15–20 seconds, recruiters will scan and see:
✅ [Key technology/skill 1]
✅ [Key technology/skill 2]
✅ [Key project/metric 3]
✅ [Key technology/skill 4]

---

## What's Missing?

Not required, but these would make the resume even stronger:
• [Missing skill/tool 1, e.g. Docker, CI/CD, Pytest, Cloud]
• [Missing profile link / portfolio / GitHub]
• [Missing architectural or testing detail]

---

## ATS Keywords Found

Your resume already includes valuable keywords:
`[Keyword 1]`, `[Keyword 2]`, `[Keyword 3]`, `[Keyword 4]`, `[Keyword 5]`, `[Keyword 6]`

---

## Final Verdict

[2–3 closing sentences giving the recruiter's final decision on whether they would shortlist this resume for an interview, along with immediate next steps].

---

IMPORTANT RULES:
- Assign honest, realistic scores ([X] MUST be an integer). Do NOT make every resume a 99/100.
- ALWAYS provide the exact rewritten examples for "Things I Would Improve" (Summary rewrite + Bullet rewrites).
- Do NOT skip any section of this template.
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
