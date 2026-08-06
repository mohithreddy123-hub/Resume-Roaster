"""
prompts/json_schema.py
----------------------
Defines lightweight category-specific JSON schemas for Gemini responses.
Prevents giant report dumps and enforces dynamic category-based reviews.
"""

import json
import re


def get_json_schema_instructions(category: str) -> str:
    """
    Return category-specific lightweight JSON schema instructions for Gemini.
    Generates a single continuous conversational review without rigid report subsections.
    """
    if category == "Bad":
        schema_text = """
{
  "first_reaction": "I'm going to be honest. This resume is making your job search much harder than it needs to. Let's fix it.",
  "conversational_review": "<2-3 sentence honest assessment pointing out missing details>",
  "missing_info_questions": [
    "<Question asking for missing degree, grad year, email, phone, project details, GitHub, or LinkedIn>"
  ],
  "closing_prompt": "<Request asking candidate to reply with missing details before proceeding with full review>"
}
"""
    else:
        schema_text = """
{
  "first_reaction": "<Spontaneous human recruiter reaction opening quote calibrated to resume category>",
  "conversational_review": "<Continuous, opinionated recruiter review paragraph(s). Prioritizes ONLY the top 2-3 biggest issues, ignores good sections, evolves opinions while reading ('I almost ignored this project... wait, I kept reading...'), compares sections ('Your projects are much stronger than your summary'), and weaves roasts naturally with WHY it fails and HOW to fix it>",
  "closing_proposal": "<Natural recruiter conversation ending proposal (e.g., 'I'd personally fix the summary before touching anything else. Want to start there?')>"
}
"""

    return f"""
CRITICAL REQUIREMENT: YOU MUST RESPOND IN VALID JSON FORMAT ONLY.
Do NOT wrap your response in markdown text or natural language intro.
Your output must be a single parseable JSON object matching this schema:

{schema_text.strip()}
""".strip()


def parse_and_validate_analysis_json(raw_text: str, category: str, fallback_score: int = 70, fallback_ats: int = 70) -> dict:
    """
    Parse raw AI response text into a validated dictionary matching category schema.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Fallback dictionary if parsing fails
    if category == "Bad":
        return {
            "first_impression": "Your resume seems to be missing several key details like education, project metrics, or links.",
            "missing_info_questions": [
                "Could you share your degree and graduation year?",
                "What technologies did you use in your main projects?",
                "Do you have a GitHub or LinkedIn profile link?"
            ],
            "closing_prompt": "Reply with these details so I can give you a real recruiter review!"
        }

    return {
        "first_impression": "Reviewed your resume structure and technical stack.",
        "strengths": [{"title": "Technical Focus", "explanation": "Includes relevant software development keywords."}],
        "weaknesses": [{"issue": "Metric Impact", "why": "Lacks quantified results.", "fix": "Add numbers and percentages to bullet points."}],
        "overall_feedback": "Resume loaded cleanly. Ask me any follow-up question to rewrite sections or suggest skills!",
        "closing_question": "Which section would you like to rewrite or improve first?"
    }
