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


def classify_resume(score: int) -> str:
    """
    Classify a resume into an internal category based on its score.

    Categories (internal only — never shown as badges):
        Excellent  → score >= 80   (Very strong resume)
        Good       → score >= 60   (Above average, needs minor improvements)
        Average    → score >= 40   (Has several weaknesses, needs improvement)
        Bad        → score < 40    (Missing key info, weak projects, poor presentation)

    Args:
        score: The overall resume score (0–100) from calculate_resume_score().

    Returns:
        One of: "Excellent", "Good", "Average", "Bad"
    """
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
