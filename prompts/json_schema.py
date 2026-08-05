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
  "first_reaction": "I honestly expected another average student resume. Then I reached your [Specific Project Name]. Alright... now you've got my attention.",
  "recruiter_opinion": "<2-3 sentence opinionated recruiter assessment referencing actual projects>",
  "strengths": [
    {
      "title": "<Specific Strength Title>",
      "explanation": "<Specific praise referencing actual project names or tech combinations>"
    }
  ],
  "weaknesses": [
    {
      "issue": "<Executive Polish Point>",
      "roast": "<Light roast on vague wording>",
      "why": "<Why it could be even sharper>",
      "solution": "<Immediate fix>"
    }
  ],
  "curiosity_question": "<1 recruiter curiosity question challenging a claim or asking about deployment/metrics>",
  "closing_question": "<1 natural conversational prompt inviting user's next step>"
}
"""
    elif category == "Good":
        schema_text = """
{
  "first_reaction": "This is actually better than I expected. You've clearly put effort into your projects. Now let's talk about why this still isn't interview-ready.",
  "recruiter_opinion": "<2-3 sentence opinionated recruiter assessment referencing actual projects>",
  "strengths": [
    {
      "title": "<Specific Strength Title>",
      "explanation": "<Specific praise referencing actual project names or tech stacks>"
    }
  ],
  "key_roasts_and_fixes": [
    {
      "issue": "<Specific Project / Section>",
      "roast": "<Memorable, witty roast of the resume writing (never person)>",
      "why": "<Why a screening recruiter gets confused in 15 seconds>",
      "solution": "<Immediate metric rewrite or practical solution>"
    }
  ],
  "curiosity_question": "<1 natural curiosity question, e.g. 'I noticed Docker in [Project]. Did you deploy to cloud or run locally?'>",
  "closing_question": "<1 sharp follow-up question inviting next step>"
}
"""
    elif category == "Average":
        schema_text = """
{
  "first_reaction": "I can already see the problem. You did the work. Your resume forgot to tell me.",
  "recruiter_opinion": "<2-3 sentence direct recruiter assessment referencing exact project names>",
  "key_roasts_and_fixes": [
    {
      "issue": "<Specific Project / Section>",
      "roast": "<Memorable, witty roast calling out vague descriptions>",
      "why": "<Why this fails the 20-second recruiter scan>",
      "solution": "<Exact metric rewrite or structural fix>"
    }
  ],
  "curiosity_question": "<1 natural challenge question, e.g. 'You wrote optimized performance—optimized by how much?'>",
  "closing_question": "<1 direct follow-up question asking which section to rewrite first>"
}
"""
    else:  # Bad / Missing Info
        schema_text = """
{
  "first_reaction": "I'm going to be honest. This resume is making your job search much harder than it needs to. Let's fix it.",
  "recruiter_opinion": "<2 sentence assessment pointing out missing sections or metrics>",
  "missing_info_questions": [
    "<Question asking for missing degree, grad year, email, phone, project details, GitHub, or LinkedIn>"
  ],
  "closing_prompt": "<Request asking candidate to reply with missing details before proceeding with full review>"
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
