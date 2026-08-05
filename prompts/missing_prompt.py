"""
prompts/missing_prompt.py
-------------------------
Single-responsibility prompt for requesting missing information from the user.
Used when a resume is classified as 'Bad' or lacks critical sections (email, phone, degree, grad year, projects, skills, links).
"""

from prompts.json_schema import get_json_schema_instructions


def get_missing_info_prompt(missing_fields: list[str], structured_resume: dict) -> str:
    """
    Build a prompt requesting missing information from the candidate.

    Args:
        missing_fields: List of missing field descriptions detected in Python.
        structured_resume: Dictionary of extracted resume sections.

    Returns:
        JSON prompt string for Gemini.
    """
    json_instructions = get_json_schema_instructions(category="Bad")
    missing_str = ", ".join(missing_fields) if missing_fields else "critical contact or project details"

    return f"""
The candidate's resume is currently missing important information: {missing_str}.

RESUME SECTIONS DETECTED:
- Header: {structured_resume.get('header', '')[:200]}
- Summary: {structured_resume.get('summary', '')[:200]}
- Education: {structured_resume.get('education', '')[:200]}
- Projects: {structured_resume.get('projects', '')[:200]}
- Skills: {structured_resume.get('skills', '')[:200]}

YOUR TASK:
Act as a 20-year veteran recruiter. Do NOT generate a full resume review or fake advice.
Formulate a friendly, direct initial response asking the candidate specifically for the missing details: {missing_str}.

{json_instructions}
""".strip()
