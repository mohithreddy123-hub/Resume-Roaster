"""
prompts/skill_prompt.py
-----------------------
Generates prompts for skill suggestions based on target role.
Only activated when: user explicitly asks, OR resume has very few skills.
Suggests 5–10 high-impact skills with a one-line reason for each.
Never generates roadmaps. Never suggests 50 skills.
"""

from config import TARGET_ROLES, MIN_SKILLS_TO_SUGGEST, MAX_SKILLS_TO_SUGGEST


def get_skill_suggestion_prompt(target_role: str, resume_text: str) -> str:
    """
    Build a prompt to suggest relevant skills for a target role.

    Args:
        target_role:  The role the user is targeting (from TARGET_ROLES list).
        resume_text:  The full resume text for context (to avoid suggesting duplicates).

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    return f"""
You are suggesting skills for a resume based on the user's target role.

## RESUME CONTEXT (to avoid suggesting skills they already have)
{resume_text}

## TARGET ROLE
{target_role}

## YOUR TASK
Suggest {MIN_SKILLS_TO_SUGGEST}–{MAX_SKILLS_TO_SUGGEST} high-impact skills for this role.

Format each suggestion exactly like this:
• [Skill Name]
  Reason: [One concise sentence on why this skill matters for the role]

---

RULES:
- Do NOT suggest skills already listed in the resume.
- Suggest only skills that are genuinely in demand for {target_role} jobs.
- Keep each reason to ONE sentence maximum.
- Do NOT generate a learning roadmap.
- Do NOT list 20+ skills — stick to {MIN_SKILLS_TO_SUGGEST}–{MAX_SKILLS_TO_SUGGEST} impactful ones.
- Focus on skills that will have the most impact on getting hired.
- After the list, add: "Want me to explain how to learn any of these, or suggest resources?"
""".strip()


def get_few_skills_prompt(current_skills: str, resume_text: str) -> str:
    """
    Build a prompt used when the resume has very few skills listed.
    Asks the user if they want suggestions without assuming.

    Args:
        current_skills: The skills currently listed in the resume.
        resume_text:    Full resume text for context.

    Returns:
        A complete prompt string ready to be sent to Gemini.
    """
    return f"""
You are reviewing a resume that has very few skills listed.

## RESUME
{resume_text}

## CURRENT SKILLS LISTED
{current_skills if current_skills.strip() else "[No skills section found]"}

## YOUR TASK
Point out that the skills section is thin, and offer to help.
Do this in a natural, conversational way — not robotic.

Example approach:
"You've only listed [X skills]. That's a short list for a tech resume.
If you know more technologies, I'd recommend adding them.
If you'd like, I can suggest skills based on your target role — just tell me what you're aiming for."

Then STOP. Wait for the user to respond.

RULES:
- Do NOT automatically dump a list of skill suggestions.
- Do NOT assume the user's target role.
- Keep the message brief and conversational.
- Mention the available roles naturally if the user seems open to suggestions:
  {', '.join(TARGET_ROLES[:-1])}, or {TARGET_ROLES[-1]}.
""".strip()


def get_available_roles_text() -> str:
    """Return formatted list of available target roles for display."""
    return "\n".join(f"• {role}" for role in TARGET_ROLES)
