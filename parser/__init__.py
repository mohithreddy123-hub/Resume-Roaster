"""
parser/__init__.py
------------------
Exposes the unified parse_resume function as the public interface.
Internal parsers (pdf, docx) are not meant to be imported directly.
"""

from parser.parser import parse_resume, ParseResult

__all__ = ["parse_resume", "ParseResult"]
