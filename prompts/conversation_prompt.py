"""
prompts/conversation_prompt.py
------------------------------
Generates context-aware prompts for follow-up chat interactions.
Ensures the AI answers ONLY the user's current question without dumping
full reviews or unsolicited roadmaps.
"""


def build_conversation_user_prompt(
    user_message: str,
    structured_resume: dict,
    python_score: int,
    ats_score: int,
    missing_fields: list[str],
    job_description: str = "",
) -> str:
    """
    Build a context-rich user message for follow-up conversation turns.

    Args:
        user_message: The user's input question or command.
        structured_resume: Dictionary of extracted resume sections.
        python_score: Deterministic Python resume score.
        ats_score: Deterministic Python ATS score.
        missing_fields: List of missing fields detected in Python.
        job_description: Optional target Job Description text.

    Returns:
        Formatted prompt string for conversation execution.
    """
    jd_info = f"\nTARGET JOB DESCRIPTION:\n{job_description}\n" if job_description else ""
    missing_info = f"\nMISSING FIELDS DETECTED: {', '.join(missing_fields)}\n" if missing_fields else ""

    return f"""
CONTEXT INFORMATION:
- Deterministic Resume Score: {python_score}/100
- Deterministic ATS Score: {ats_score}/100
{missing_info}{jd_info}
RESUME STRUCTURE:
- Header: {structured_resume.get('header', '')[:200]}
- Summary: {structured_resume.get('summary', '')[:300]}
- Skills: {structured_resume.get('skills', '')[:300]}
- Projects: {structured_resume.get('projects', '')[:500]}
- Experience: {structured_resume.get('experience', '')[:500]}
- Education: {structured_resume.get('education', '')[:300]}

USER QUESTION / REQUEST:
"{user_message}"

CONVERSATION RULES:
1. DIRECT-ANSWER FIRST: Answer the user's specific question at the very top of your response. Put requested information (skills, project feedback, rewrites) first!
2. CHATGPT/CLAUDE READABILITY: Format in clean, scannable Markdown. Use short paragraphs (1-2 sentences max) and concise bullet points (•). NO walls of text or 6-10 paragraph essays.
3. CONTEXT MEMORY: Remember all previous user choices (target role, excluded tools, fixed sections). Build continuously on past turns.
4. ANTI-REPETITION: Never re-critique or re-suggest a section already discussed unless asked.
5. REWRITE SPECIFIC SECTION: If a rewrite is requested, provide 3 versions (Simple, Professional, Highly Professional) for that specific bullet/section only.
6. NATURAL RECRUITER ENDING: End your response with a natural 1-line recruiter proposal (e.g., "I'd personally fix the summary before touching anything else. Want to start there?").
""".strip()
