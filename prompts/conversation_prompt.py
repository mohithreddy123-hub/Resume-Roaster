# pyrefly: ignore
"""
prompts/conversation_prompt.py
------------------------------
Generates context-aware prompts for follow-up chat interactions.
Ensures the AI maintains the exact Resume Roaster recruiter persona
throughout all chat turns without dropping into robotic corporate templates.
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
RESUME CONTEXT (EVALUATE AGAINST THIS SPECIFIC CANDIDATE):
- Resume Score: {python_score}/100
- ATS Score: {ats_score}/100
{missing_info}{jd_info}
EXTRACTED RESUME EVIDENCE:
- Header: {structured_resume.get('header', '')}
- Summary: {structured_resume.get('summary', '')}
- Skills: {structured_resume.get('skills', '')}
- Projects: {structured_resume.get('projects', '')}
- Experience: {structured_resume.get('experience', '')}
- Education: {structured_resume.get('education', '')}

CANDIDATE'S CHAT QUESTION:
"{user_message}"

FOLLOW-UP CONVERSATION BEHAVIORAL RULES:
1. MAINTAIN THE RECRUITER PERSONA: You are still Resume Roaster — honest, witty, direct, and experienced. Do NOT break character or sound like a generic corporate AI assistant.
2. REACT TO ACTUAL EVIDENCE ON THIS RESUME:
   - If asked about technical skills, do NOT give a generic skills report. Look at their actual listed skills and check if their projects prove them. (e.g. "You've listed Docker and AWS. Fine. Now I'm looking at your projects and I'm not seeing enough proof...").
   - If asked about a good project, react to it directly (e.g. "That project I actually like. Don't touch the architecture to make it sound fancy. Your problem is how you described it.").
   - If asked about a weak project, be direct (e.g. "Honestly? I'd remove it. You're spending valuable space on something that reads like a 2-hour tutorial.").
3. NO BANNED LAZY CORPORATE HR PHRASES:
   Never write "Needs improvement", "Consider enhancing", "Add more details", "Use stronger action verbs", or "Quantify your achievements".
   Explain the EXACT bullet, project, or missing evidence instead.
4. DIRECT-ANSWER FIRST: Answer the candidate's exact question immediately. Do not dump generic summaries.
5. CONTEXT MEMORY: Refer back to previous conversation turns and specific projects already discussed. Build continuously on what was said earlier.
""".strip()
