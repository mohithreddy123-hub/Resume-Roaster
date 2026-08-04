"""
parser/parser.py
----------------
Unified resume parser interface.
Detects file type and routes to the correct internal parser.
Returns a standardized ParseResult — callers only deal with this one interface.
"""

from dataclasses import dataclass
from pathlib import Path

from parser.pdf_parser import (
    parse_pdf,
    PDFParseError,
    PasswordProtectedPDFError,
    BlankPDFError,
)
from parser.docx_parser import (
    parse_docx,
    DOCXParseError,
    BlankDOCXError,
)
from config import SUPPORTED_FORMATS


@dataclass
class ParseResult:
    """
    Standardized result returned by parse_resume().

    Attributes:
        success: True if parsing succeeded, False otherwise.
        text:    Extracted raw text (empty string if failed).
        error:   User-friendly error message (None if success).
    """
    success: bool
    text: str
    error: str | None = None


def parse_resume(file_bytes: bytes, filename: str) -> ParseResult:
    """
    Parse a resume file and return its raw text.

    Routes to the appropriate parser based on file extension.
    All internal errors are caught here and converted to user-friendly messages.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename including extension.

    Returns:
        ParseResult with success status, raw text, and optional error message.
    """
    extension = Path(filename).suffix.lower()

    # Check for unsupported format before attempting to parse
    if extension not in SUPPORTED_FORMATS:
        return ParseResult(
            success=False,
            text="",
            error=(
                f"Unsupported file format '{extension}'. "
                f"Please upload a PDF or DOCX file."
            ),
        )

    try:
        if extension == ".pdf":
            raw_text = parse_pdf(file_bytes)
        elif extension == ".docx":
            raw_text = parse_docx(file_bytes)
        else:
            # Should never reach here due to the check above, but kept for safety
            return ParseResult(
                success=False,
                text="",
                error="Unsupported file format. Please upload a PDF or DOCX.",
            )

        return ParseResult(success=True, text=raw_text)

    except PasswordProtectedPDFError as e:
        return ParseResult(success=False, text="", error=str(e))

    except BlankPDFError as e:
        return ParseResult(success=False, text="", error=str(e))

    except PDFParseError as e:
        return ParseResult(
            success=False,
            text="",
            error="We couldn't read this resume. Try uploading another PDF.",
        )

    except BlankDOCXError as e:
        return ParseResult(success=False, text="", error=str(e))

    except DOCXParseError as e:
        return ParseResult(success=False, text="", error=str(e))

    except Exception:
        # Catch-all: never expose raw Python errors to the user
        return ParseResult(
            success=False,
            text="",
            error=(
                "Something went wrong while reading your resume. "
                "Please try uploading it again."
            ),
        )
