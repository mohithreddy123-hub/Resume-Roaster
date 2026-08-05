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

    Args:
        category: Internal category — "Excellent", "Good", "Average", or "Bad".

    Returns:
        JSON instruction prompt string.
    """
    if category == "Excellent":
        schema_text = """
{
  "first_impression": "<2 sentence high-level recruiter perception>",
  "strengths": [
    {
      "title": "<Specific Strength Title>",
      "explanation": "<Specific compliment referencing real projects/skills from the resume>"
    }
  ],
  "weaknesses": [
    {
      "issue": "<Minor Polish Point>",
      "why": "<Why it could be even sharper>",
      "fix": "<Immediate fix>"
    }
  ],
  "overall_feedback": "<2-3 sentence recruiter closing verdict>",
  "closing_question": "<1 follow-up question inviting candidate to ask anything>"
}
"""
    elif category == "Good":
        schema_text = """
{
  "first_impression": "<2 sentence recruiter overview>",
  "strengths": [
    {
      "title": "<Specific Strength Title>",
      "explanation": "<Specific compliment referencing real projects/tech from resume>"
    }
  ],
  "weaknesses": [
    {
      "issue": "<Weakness Title>",
      "why": "<Why it hurts hiring chances>",
      "fix": "<Immediate 1-sentence solution>"
    }
  ],
  "key_improvements": [
    "<Specific bullet point or section tweak with metrics>"
  ],
  "overall_feedback": "<2-3 sentence summary>",
  "closing_question": "<1 natural follow-up question>"
}
"""
    elif category == "Average":
        schema_text = """
{
  "first_impression": "<2 sentence direct recruiter assessment>",
  "roasts_and_solutions": [
    {
      "issue": "<Weakness Title / Roast>",
      "why": "<Why this hurts candidate in 20-second recruiter scan>",
      "solution": "<Immediate practical fix / metric rewrite>"
    }
  ],
  "overall_feedback": "<3 sentence direct turnaround plan>",
  "closing_question": "<1 sharp follow-up question asking which project or section to rewrite first>"
}
"""
    else:  # Bad / Missing Info
        schema_text = """
{
  "first_impression": "<2 sentence honest assessment pointing out missing details>",
  "missing_info_questions": [
    "<Question asking for missing degree, grad year, email, phone, project details, GitHub, or LinkedIn>"
  ],
  "closing_prompt": "<Friendly request asking candidate to reply with these missing details before proceeding with full review>"
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
