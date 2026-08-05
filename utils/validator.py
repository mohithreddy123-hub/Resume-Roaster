"""
utils/validator.py
------------------
Validates uploaded resume files BEFORE any parsing happens.
Checks: file size, file type, and non-empty bytes.
Also validates extracted text after parsing (non-blank).
Returns friendly error messages — never technical exceptions.
"""

from dataclasses import dataclass
from pathlib import Path

from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, SUPPORTED_FORMATS


@dataclass
class ValidationResult:
    """
    Result of a file or text validation check.

    Attributes:
        valid:   True if validation passed.
        error:   User-friendly error message if validation failed, else None.
    """
    valid: bool
    error: str | None = None


def validate_file(file_bytes: bytes, filename: str) -> ValidationResult:
    """
    Validate an uploaded resume file before parsing.

    Checks performed (in order):
        1. File is not empty (0 bytes).
        2. File extension is supported (.pdf or .docx).
        3. File size does not exceed the maximum limit.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename including extension.

    Returns:
        ValidationResult indicating pass or fail with a user-friendly message.
    """
    # Check 1: File must not be empty
    if not file_bytes or len(file_bytes) == 0:
        return ValidationResult(
            valid=False,
            error="The uploaded file is empty. Please upload a valid resume.",
        )

    # Check 2: File extension must be supported
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS).upper().replace(".", "")
        return ValidationResult(
            valid=False,
            error=(
                f"'{extension}' is not supported. "
                f"Please upload a {supported} file."
            ),
        )

    # Check 3: File size must not exceed the limit
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        actual_mb = round(len(file_bytes) / (1024 * 1024), 1)
        return ValidationResult(
            valid=False,
            error=(
                f"Your file is {actual_mb}MB, which exceeds the {MAX_FILE_SIZE_MB}MB limit. "
                f"Please compress or reduce the file size."
            ),
        )

    return ValidationResult(valid=True)


def validate_extracted_text(text: str) -> ValidationResult:
    """
    Validate the text extracted from a resume after parsing.

    Ensures the extracted text is not blank or just whitespace.

    Args:
        text: The raw text extracted from the resume file.

    Returns:
        ValidationResult indicating pass or fail.
    """
    if not text or not text.strip():
        return ValidationResult(
            valid=False,
            error=(
                "We couldn't extract any text from this resume. "
                "The file may contain only images. "
                "Please try a different version of your resume."
            ),
        )

    # Check minimum meaningful length (at least 50 characters for a real resume)
    if len(text.strip()) < 50:
        return ValidationResult(
            valid=False,
            error=(
                "The extracted text seems too short to be a complete resume. "
                "Please make sure your file is not truncated."
            ),
        )

    return ValidationResult(valid=True)


import re


def find_missing_fields(text: str) -> list[str]:
    """
    Detect missing critical fields in a resume.

    Checks for:
        - Email address
        - Phone number
        - Education section / keywords
        - Projects section / keywords
        - Technical Skills section / keywords
        - Work Experience / Internships
        - GitHub profile
        - LinkedIn profile
        - Portfolio / Website link
        - Graduation year (e.g., 2020-2026)

    Args:
        text: Cleaned resume text string.

    Returns:
        List of human-readable missing field descriptions.
    """
    missing: list[str] = []
    text_lower = text.lower()

    # 1. Email address
    if not re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text):
        missing.append("Email Address")

    # 2. Phone number
    if not re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,6}", text):
        missing.append("Phone Number")

    # 3. Education
    if not re.search(r"\b(education|b\.?tech|b\.?e|b\.?s|master|bachelor|degree|university|college|gpa)\b", text_lower):
        missing.append("Education Section")

    # 4. Graduation Year
    if not re.search(r"\b(201[5-9]|202[0-9]|203[0])\b", text):
        missing.append("Graduation Year")

    # 5. Projects
    if not re.search(r"\b(projects?|built|developed|implemented)\b", text_lower):
        missing.append("Projects Section")

    # 6. Technical Skills
    if not re.search(r"\b(skills?|technologies|languages|frameworks|tools)\b", text_lower):
        missing.append("Technical Skills Section")

    # 7. Experience / Internships
    if not re.search(r"\b(experience|internship|employment|worked|company)\b", text_lower):
        missing.append("Work Experience / Internships")

    # 8. GitHub
    if "github.com" not in text_lower and "github:" not in text_lower:
        missing.append("GitHub Profile Link")

    # 9. LinkedIn
    if "linkedin.com" not in text_lower and "linkedin:" not in text_lower:
        missing.append("LinkedIn Profile Link")

    # 10. Portfolio
    if not re.search(r"\b(portfolio|website|http|https)\b", text_lower):
        missing.append("Portfolio / Website Link")

    return missing
