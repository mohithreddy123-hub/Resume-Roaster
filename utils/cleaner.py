"""
utils/cleaner.py
----------------
Cleans raw extracted resume text before sending it to the AI.
Removes noise: extra spaces, excessive newlines, junk characters,
non-printable characters, and unicode artifacts.
Returns a clean, readable text string.
Does NOT modify content — only cleans formatting noise.
"""

import re
import unicodedata


def clean_text(raw_text: str) -> str:
    """
    Clean raw text extracted from a resume file.

    Operations performed (in order):
        1. Normalize unicode characters (handles special characters from PDFs).
        2. Replace non-printable/control characters with a space.
        3. Replace multiple consecutive spaces with a single space.
        4. Replace more than 2 consecutive newlines with exactly 2.
        5. Strip leading/trailing whitespace from each line.
        6. Remove lines that are completely empty after stripping.
        7. Strip overall leading/trailing whitespace.

    Args:
        raw_text: The raw text string from the parser.

    Returns:
        A cleaned text string ready for AI processing.
    """
    if not raw_text:
        return ""

    # Step 1: Normalize unicode (NFC form handles ligatures, accents, etc.)
    text = unicodedata.normalize("NFC", raw_text)

    # Step 2: Replace non-printable and control characters (except \n and \t)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", " ", text)

    # Step 3: Replace tabs with a single space
    text = text.replace("\t", " ")

    # Step 4: Replace multiple consecutive spaces with a single space
    text = re.sub(r" {2,}", " ", text)

    # Step 5: Normalize line endings (Windows \r\n → \n)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Step 6: Strip each line individually
    lines = [line.strip() for line in text.split("\n")]

    # Step 7: Collapse more than 2 consecutive blank lines into 2
    cleaned_lines: list[str] = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)

    # Step 8: Join and final strip
    cleaned_text = "\n".join(cleaned_lines).strip()

    return cleaned_text


def truncate_for_prompt(text: str, max_chars: int = 8000) -> str:
    """
    Truncate cleaned resume text to fit within LLM prompt limits.

    Args:
        text:      Cleaned resume text.
        max_chars: Maximum character count (default 8000 — safe for Gemini).

    Returns:
        Text truncated at the nearest sentence boundary if over limit.
    """
    if len(text) <= max_chars:
        return text

    # Truncate and add notice
    truncated = text[:max_chars]
    # Try to end at the last newline for cleanliness
    last_newline = truncated.rfind("\n")
    if last_newline > max_chars * 0.8:
        truncated = truncated[:last_newline]

    return truncated + "\n\n[Resume text truncated for processing]"
