"""
parser/pdf_parser.py
--------------------
Extracts raw text from PDF files using PyMuPDF (fitz).
Handles: password-protected PDFs, blank pages, corrupted files.
Returns raw text string — no cleaning done here.
"""

import fitz  # PyMuPDF


class PDFParseError(Exception):
    """Raised when a PDF cannot be parsed for any reason."""
    pass


class PasswordProtectedPDFError(PDFParseError):
    """Raised when a PDF is encrypted/password protected."""
    pass


class BlankPDFError(PDFParseError):
    """Raised when a PDF has no extractable text on any page."""
    pass


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract raw text from a PDF file given its bytes.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Raw extracted text as a single string.

    Raises:
        PasswordProtectedPDFError: If the PDF is encrypted.
        BlankPDFError: If no text could be extracted from any page.
        PDFParseError: For all other parsing failures.
    """
    try:
        # Open PDF from bytes stream
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise PDFParseError(f"Could not open PDF file. It may be corrupted.") from e

    # Check if password protected
    if doc.is_encrypted:
        doc.close()
        raise PasswordProtectedPDFError(
            "This PDF is password protected. Please remove the password first."
        )

    pages_text: list[str] = []

    try:
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            page_text = page.get_text("text")  # type: ignore[arg-type]

            # Only include pages that have actual content
            if page_text and page_text.strip():
                pages_text.append(page_text.strip())
    except Exception as e:
        raise PDFParseError(f"Failed to extract text from PDF pages.") from e
    finally:
        doc.close()

    if not pages_text:
        raise BlankPDFError(
            "This PDF appears to be empty or contains only images with no readable text."
        )

    # Join all pages with double newline as separator
    raw_text = "\n\n".join(pages_text)
    return raw_text
