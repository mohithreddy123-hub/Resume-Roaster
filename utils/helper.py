"""
utils/helper.py
---------------
General-purpose helper utilities for Resume Roaster.
Contains pure functions for: section detection, missing field detection,
and basic information extraction (name, email, phone, links).
No side effects — all functions are stateless and reusable.
"""

import re
from config import SECTION_PATTERNS, CRITICAL_FIELDS


# ─── Section Detection ────────────────────────────────────────────────────────

def detect_sections(text: str) -> dict[str, bool]:
    """
    Detect which resume sections are present in the extracted text.

    Uses keyword matching (case-insensitive) against known section headings.

    Args:
        text: Cleaned resume text.

    Returns:
        Dict mapping section name → True if detected, False if not.
        Example: {"education": True, "projects": True, "experience": False, ...}
    """
    text_lower = text.lower()
    detected: dict[str, bool] = {}

    for section, patterns in SECTION_PATTERNS.items():
        found = any(pattern in text_lower for pattern in patterns)
        detected[section] = found

    return detected


# ─── Missing Field Detection ──────────────────────────────────────────────────

def find_missing_fields(text: str) -> list[str]:
    """
    Identify which critical fields are absent from the resume.

    Args:
        text: Cleaned resume text.

    Returns:
        List of field names that appear to be missing.
        Example: ["github", "phone"]
    """
    missing: list[str] = []

    # Check email
    if not extract_email(text):
        missing.append("email")

    # Check phone
    if not extract_phone(text):
        missing.append("phone")

    # Check links
    links = extract_links(text)
    if not links.get("github"):
        missing.append("github")
    if not links.get("linkedin"):
        missing.append("linkedin")

    # Check sections
    sections = detect_sections(text)
    if not sections.get("education"):
        missing.append("education")
    if not sections.get("skills"):
        missing.append("skills")
    if not sections.get("projects") and not sections.get("experience"):
        missing.append("projects or experience")

    return missing


# ─── Information Extraction ───────────────────────────────────────────────────

def extract_name(text: str) -> str | None:
    """
    Attempt to extract the candidate's name from the resume.

    Strategy: The name is typically in the first 3–5 lines of a resume,
    is 2–4 words, and does not contain digits or common section keywords.

    Args:
        text: Cleaned resume text.

    Returns:
        Best-guess name string, or None if not found.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Look through the first 5 lines for a plausible name
    section_keywords = {
        "resume", "curriculum", "vitae", "cv", "profile", "summary",
        "objective", "email", "phone", "address", "linkedin", "github",
    }

    for line in lines[:5]:
        # Name: 2–4 words, only alphabetic characters and spaces/hyphens
        words = line.split()
        if 2 <= len(words) <= 4:
            # Must not contain digits
            if re.search(r"\d", line):
                continue
            # Must not be a known section keyword
            if any(kw in line.lower() for kw in section_keywords):
                continue
            # Must not contain @ (email) or : (label)
            if "@" in line or ":" in line:
                continue
            # All words should start with a capital letter (likely a proper name)
            if all(word[0].isupper() for word in words if word.isalpha()):
                return line

    return None


def extract_email(text: str) -> str | None:
    """
    Extract an email address from the resume text using regex.

    Args:
        text: Cleaned resume text.

    Returns:
        First matched email address, or None if not found.
    """
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """
    Extract a phone number from the resume text.

    Handles common formats: +91-9876543210, 9876543210, (987) 654-3210, etc.

    Args:
        text: Cleaned resume text.

    Returns:
        First matched phone number string, or None if not found.
    """
    # Pattern handles: international prefix, spaces, dashes, dots, parentheses
    pattern = r"(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-\.]?)(\d{3}[\s\-\.]?\d{4})"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None


def extract_links(text: str) -> dict[str, str | None]:
    """
    Extract GitHub, LinkedIn, and Portfolio links from the resume text.

    Args:
        text: Cleaned resume text.

    Returns:
        Dict with keys: "github", "linkedin", "portfolio"
        Each value is the URL string or None if not found.
    """
    links: dict[str, str | None] = {
        "github": None,
        "linkedin": None,
        "portfolio": None,
    }

    # GitHub URL pattern
    github_match = re.search(
        r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-\.]+)?",
        text,
        re.IGNORECASE,
    )
    if github_match:
        links["github"] = github_match.group(0)

    # LinkedIn URL pattern
    linkedin_match = re.search(
        r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-]+/?",
        text,
        re.IGNORECASE,
    )
    if linkedin_match:
        links["linkedin"] = linkedin_match.group(0)

    # Portfolio — any URL that isn't GitHub or LinkedIn
    # Look for common portfolio hosting patterns
    portfolio_match = re.search(
        r"https?://(?:www\.)?(?!github|linkedin)[a-zA-Z0-9_\-]+\."
        r"(?:com|io|dev|me|co|net|in)/[a-zA-Z0-9_\-/\.]*",
        text,
        re.IGNORECASE,
    )
    if portfolio_match:
        links["portfolio"] = portfolio_match.group(0)

    return links


# ─── Text Utilities ────────────────────────────────────────────────────────────

def count_words(text: str) -> int:
    """Return the word count of a text string."""
    return len(text.split())


def get_resume_summary_stats(text: str) -> dict[str, int | bool]:
    """
    Return basic statistics about the resume text.
    Useful for quick sanity checks and scoring hints.

    Args:
        text: Cleaned resume text.

    Returns:
        Dict with word_count, line_count, has_email, has_phone, has_github.
    """
    return {
        "word_count": count_words(text),
        "line_count": len([l for l in text.split("\n") if l.strip()]),
        "has_email": extract_email(text) is not None,
        "has_phone": extract_phone(text) is not None,
        "has_github": extract_links(text)["github"] is not None,
        "has_linkedin": extract_links(text)["linkedin"] is not None,
    }
