"""
utils/__init__.py
-----------------
Exposes the main utility functions as the public interface.
"""

from utils.validator import validate_file, ValidationResult
from utils.cleaner import clean_text
from utils.helper import (
    detect_sections,
    find_missing_fields,
    extract_name,
    extract_email,
    extract_phone,
    extract_links,
)

__all__ = [
    "validate_file",
    "ValidationResult",
    "clean_text",
    "detect_sections",
    "find_missing_fields",
    "extract_name",
    "extract_email",
    "extract_phone",
    "extract_links",
]
