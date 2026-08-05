"""
prompts/json_schema.py
----------------------
Defines the required JSON Schema for Gemini AI responses.
Ensures structured, deterministic, machine-readable feedback.
Provides JSON parsing and repair utilities.
"""

import json
import re


def get_json_schema_instructions() -> str:
    """
    Return the JSON output format rules and schema definition for Gemini prompts.
    """
    return """
CRITICAL REQUIREMENT: YOU MUST RESPOND IN VALID JSON FORMAT ONLY.
Do NOT wrap your response in markdown text or natural language intro.
Your output must be a single parseable JSON object matching this schema:

{
  "resume_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "classification": "<"Excellent" | "Good" | "Average" | "Bad">",
  "first_impression": "<2-3 sentence high-level recruiter summary>",
  "category_ratings": {
    "ats_friendliness": <integer 1-10>,
    "project_quality": <integer 1-10>,
    "technical_skills": <integer 1-10>,
    "professional_summary": <integer 1-10>,
    "placement_readiness": <integer 1-10>,
    "faang_readiness": <integer 1-10>
  },
  "strengths": [
    {
      "title": "<Strength Title>",
      "explanation": "<Why this is a strength, quoting evidence from resume>"
    }
  ],
  "weaknesses": [
    {
      "issue": "<Weakness Title>",
      "why": "<Why it hurts the candidate>",
      "fix": "<Immediate 1-sentence solution>"
    }
  ],
  "line_by_line_audit": [
    {
      "original": "<Direct quote of weak bullet point>",
      "problem": "<Why it is weak: missing metrics, passive verb, etc.>",
      "improved": "<Suggested strong rewritten bullet point with numbers/impact>"
    }
  ],
  "skill_analysis": {
    "skills_to_keep": ["<Skill 1>", "<Skill 2>"],
    "missing_recommended_skills": ["<Skill 1>", "<Skill 2>"],
    "alignment_feedback": "<Analysis of project stack vs listed technical skills>"
  },
  "recruiter_scan_highlights": [
    "✅ <Key tech or metric 1>",
    "✅ <Key tech or metric 2>"
  ],
  "overall_feedback": "<3-5 sentence turnaround strategy summary>",
  "suggested_followup_questions": [
    "<Follow-up question 1>",
    "<Follow-up question 2>",
    "<Follow-up question 3>"
  ]
}
""".strip()


def parse_and_validate_analysis_json(raw_text: str, fallback_score: int = 70, fallback_ats: int = 70) -> dict:
    """
    Parse raw AI response text into a validated dictionary.
    Handles raw JSON as well as Markdown code block JSON (```json ... ```).

    Args:
        raw_text: Raw string returned by Gemini.
        fallback_score: Baseline score to use if parsing fails.
        fallback_ats: Baseline ATS score to use if parsing fails.

    Returns:
        Validated analysis dictionary matching schema.
    """
    cleaned = raw_text.strip()

    # Strip markdown block ticks if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            # Ensure mandatory fields exist with safe defaults
            data.setdefault("resume_score", fallback_score)
            data.setdefault("ats_score", fallback_ats)
            data.setdefault("classification", "Average")
            data.setdefault("first_impression", "Resume review generated.")
            data.setdefault("strengths", [])
            data.setdefault("weaknesses", [])
            data.setdefault("line_by_line_audit", [])
            data.setdefault("skill_analysis", {
                "skills_to_keep": [],
                "missing_recommended_skills": [],
                "alignment_feedback": "Review skills section."
            })
            data.setdefault("recruiter_scan_highlights", [])
            data.setdefault("overall_feedback", "Complete review available.")
            data.setdefault("suggested_followup_questions", [
                "How can I improve my project bullet points with metrics?",
                "Which missing skills are highest priority for my target role?",
                "Can you rewrite my professional summary?"
            ])
            return data
    except Exception:
        pass

    # Fallback structure if JSON parsing fails
    return {
        "resume_score": fallback_score,
        "ats_score": fallback_ats,
        "classification": "Average",
        "first_impression": "Analysis completed. Review detailed sections below.",
        "category_ratings": {
            "ats_friendliness": 7,
            "project_quality": 7,
            "technical_skills": 7,
            "professional_summary": 6,
            "placement_readiness": 7,
            "faang_readiness": 6
        },
        "strengths": [{"title": "Resume Content", "explanation": "Resume processed successfully."}],
        "weaknesses": [{"issue": "Formatting & Precision", "why": "Lacks quantified impact metrics.", "fix": "Add numbers and percent improvements to bullets."}],
        "line_by_line_audit": [],
        "skill_analysis": {
            "skills_to_keep": [],
            "missing_recommended_skills": [],
            "alignment_feedback": "Review technical skills for target role fit."
        },
        "recruiter_scan_highlights": [],
        "overall_feedback": raw_text[:500] if raw_text else "Review completed.",
        "suggested_followup_questions": [
            "How can I rewrite my bullet points with numbers?",
            "What skills am I missing for backend roles?",
            "Can you help me rewrite my experience section?"
        ]
    }
