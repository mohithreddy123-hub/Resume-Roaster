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
1. Internally follow the 9-step reasoning chain (understand candidate level, market alignment, section comparison, honest opinion).
2. Answer ONLY the user's specific question or request.
3. Reference ACTUAL project titles, technologies, and quotes from the candidate's resume in your response.
4. Do NOT re-dump the entire initial analysis or score cards.
5. If the user asks for a rewrite, rewrite ONLY the specific section or bullet requested (giving Simple, Professional, Highly Professional versions).
6. Speak with the authentic voice of a 20-year recruiter: direct, honest, witty, and immediately helpful.
7. Always follow every roast or critique with WHY it matters to a recruiter and HOW to fix it.
""".strip()
