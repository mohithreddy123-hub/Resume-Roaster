"""
prompts/rewrite_prompt.py
-------------------------
Generates prompts for rewriting specific resume sections on user request.
NEVER activates automatically — only called when the user explicitly asks.
Produces 3 versions: Simple, Professional, Highly Professional.
One responsibility: section rewriting only.
"""


def get_rewrite_prompt(
    section_name: str,
    section_content: str,
    resume_text: str,
    user_instruction: str = "",
) -> str:
    """
    Build a prompt to rewrite a specific resume section.

    Args:
        section_name:     Name of the section being rewritten (e.g., "project description").
        section_content:  The current content of that section.
        resume_text:      Full resume text for context.
        user_instruction: Any specific instruction from the user (optional).

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    extra = f"\nUser's specific request: {user_instruction}" if user_instruction else ""

    return f"""
You are rewriting a specific section of a resume. Do NOT touch any other section.

## FULL RESUME CONTEXT (for reference only — do not rewrite this)
{resume_text}

## SECTION TO REWRITE
Section: {section_name}
Current Content:
{section_content}
{extra}

## YOUR TASK
Rewrite ONLY the above section. Produce exactly 3 versions:

**Version 1 — Simple**
[Clean, straightforward, easy to read. Entry-level friendly.]

**Version 2 — Professional**
[Strong action verbs, quantified results where possible, clear impact.]

**Version 3 — Highly Professional**
[Executive-level language, metrics, technical depth, maximum impact.]

---

RULES FOR ALL VERSIONS:
- Keep it resume-friendly (concise, bullet-point style where appropriate).
- Use strong action verbs (Built, Developed, Designed, Implemented, Led, etc.).
- Show: Problem → Technologies used → Your contribution → Outcome.
- Do NOT add information that isn't in the original resume.
- Do NOT rewrite any other section.
- Do NOT invent projects, skills, or achievements.
- After the 3 versions, add one line: "Which version would you like to use, or should I adjust any of them?"
""".strip()


def get_summary_rewrite_prompt(current_summary: str, resume_text: str) -> str:
    """
    Build a prompt specifically for rewriting the professional summary.

    Args:
        current_summary: The user's current summary text.
        resume_text:     Full resume for context.

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    return f"""
You are rewriting the professional summary of a resume.

## FULL RESUME CONTEXT (for understanding background — do not rewrite this)
{resume_text}

## CURRENT SUMMARY
{current_summary if current_summary.strip() else "[No summary provided — write one based on the resume]"}

## YOUR TASK
Write exactly 3 versions of the professional summary:

**Version 1 — Simple**
[2–3 lines. Clear and direct. Easy to understand. Good for first-time applicants.]

**Version 2 — Professional**
[3–4 lines. Strong language, mentions key skills and goals. Good for most applications.]

**Version 3 — Highly Professional**
[4–5 lines. Compelling opening, quantified experience if available, clear value proposition.]

---

RULES:
- Base the summary on information actually present in the resume.
- Do NOT invent experience, achievements, or skills.
- Each version must feel natural, not like a template.
- End with: "Which version works best for you, or should I tweak any of them?"
""".strip()


def get_bullet_rewrite_prompt(bullets: str, context: str) -> str:
    """
    Build a prompt for improving resume bullet points.

    Args:
        bullets: The current bullet points to improve.
        context: Brief context about what section these belong to.

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    return f"""
You are improving resume bullet points.

Context: {context}

Current bullets:
{bullets}

## YOUR TASK
Rewrite each bullet point to be stronger:
- Start with a strong action verb.
- Be specific — show what was done, how, and the result.
- Keep each bullet to 1–2 lines maximum.
- Do NOT add information that isn't there.
- If a bullet is already strong, keep it (you can note "already strong").

After rewriting, explain in one line what made each original bullet weak.
""".strip()
