"""
analyzer/classifier.py
-----------------------
Classifies a resume into one of four internal categories:
Excellent / Good / Average / Bad

This classification is INTERNAL ONLY — never displayed to the user.
It controls the AI's tone and personality in responses.
Classification is based on the overall resume score.
"""

from config import (
    CATEGORY_EXCELLENT,
    CATEGORY_GOOD,
    CATEGORY_AVERAGE,
    CATEGORY_BAD,
    SCORE_THRESHOLDS,
)


def classify_resume(score: int, missing_fields: list[str] | None = None) -> str:
    """
    Classify a resume into an internal category based on score and missing fields.

    Categories:
        Excellent  → score >= 80 and no critical fields missing
        Good       → score >= 65 and minimal missing fields
        Average    → score >= 50
        Bad        → score < 50 or critical contact/education/project fields missing

    Args:
        score: The overall resume score (0–100).
        missing_fields: Optional list of missing field strings.

    Returns:
        One of: "Excellent", "Good", "Average", "Bad"
    """
    missing = missing_fields or []
    critical_missing = [
        m for m in missing
        if m in ("Email Address", "Phone Number", "Education Section", "Projects Section", "Technical Skills Section")
    ]

    # If critical structural sections are missing, classify as Bad to ask missing info questions
    if len(critical_missing) >= 2 or ("Education Section" in missing and "Projects Section" in missing):
        return CATEGORY_BAD

    if score >= SCORE_THRESHOLDS[CATEGORY_EXCELLENT]:
        return CATEGORY_EXCELLENT
    elif score >= SCORE_THRESHOLDS[CATEGORY_GOOD]:
        return CATEGORY_GOOD
    elif score >= SCORE_THRESHOLDS[CATEGORY_AVERAGE]:
        return CATEGORY_AVERAGE
    else:
        return CATEGORY_BAD


def get_category_description(category: str) -> str:
    """
    Return a brief internal description of what each category means.
    Used for logging and debugging — not shown to users.

    Args:
        category: The category string.

    Returns:
        A description string for internal use.
    """
    descriptions = {
        CATEGORY_EXCELLENT: "Very strong resume. Respectful tone. Minimal roasting.",
        CATEGORY_GOOD: "Above average. Light humor. Point out weak spots gently.",
        CATEGORY_AVERAGE: "Several weaknesses. Direct sarcasm. Always follow with advice.",
        CATEGORY_BAD: "Needs serious work. Stronger roasting. Constructive throughout.",
    }
    return descriptions.get(category, "Unknown category.")
