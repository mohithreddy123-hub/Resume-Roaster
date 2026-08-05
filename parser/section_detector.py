"""
parser/section_detector.py
---------------------------
Python-based section detection and structured information extraction.
Splits cleaned resume text into logical sections (Header, Summary, Education,
Projects, Experience, Skills, Certifications) using deterministic regex rules.
"""

from dataclasses import dataclass, field
import re


@dataclass
class StructuredResume:
    """Dataclass holding structured sections extracted from resume text."""
    header: str = ""
    summary: str = ""
    education: str = ""
    projects: str = ""
    experience: str = ""
    skills: str = ""
    certifications: str = ""
    links: list[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> dict:
        """Convert structured resume into dictionary format."""
        return {
            "header": self.header,
            "summary": self.summary,
            "education": self.education,
            "projects": self.projects,
            "experience": self.experience,
            "skills": self.skills,
            "certifications": self.certifications,
            "links": self.links,
        }


# Section header regex patterns
SECTION_PATTERNS = {
    "summary": re.compile(
        r"^(?:professional\s+)?(?:summary|profile|about\s+me|objective|career\s+objective)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(?:education|academic\s+background|qualifications|academic\s+details)\b",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^(?:projects|key\s+projects|academic\s+projects|personal\s+projects)\b",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^(?:work\s+experience|experience|employment\s+history|internships|professional\s+experience)\b",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^(?:technical\s+skills|skills|skills\s*&\s*competencies|technologies|core\s+competencies)\b",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^(?:certifications|certificates|licenses\s*&\s*certifications|achievements)\b",
        re.IGNORECASE,
    ),
}

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+|www\.[^\s<>\"']+|github\.com/[^\s<>\"']+|linkedin\.com/in/[^\s<>\"']+",
    re.IGNORECASE,
)


def extract_structured_resume(cleaned_text: str) -> StructuredResume:
    """
    Parse cleaned resume text and extract structured sections using regex.

    Args:
        cleaned_text: Cleaned resume text string.

    Returns:
        StructuredResume object with extracted section strings and link list.
    """
    if not cleaned_text or not cleaned_text.strip():
        return StructuredResume(raw_text=cleaned_text)

    lines = cleaned_text.split("\n")
    sections_map: dict[str, list[str]] = {
        "header": [],
        "summary": [],
        "education": [],
        "projects": [],
        "experience": [],
        "skills": [],
        "certifications": [],
    }

    current_section = "header"

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # Check if line is a section header (short line matching header pattern)
        detected_header = None
        if len(stripped_line) < 40:
            clean_hdr = re.sub(r"[^\w\s]", "", stripped_line).strip()
            for key, pattern in SECTION_PATTERNS.items():
                if pattern.match(clean_hdr):
                    detected_header = key
                    break

        if detected_header:
            current_section = detected_header
        else:
            sections_map[current_section].append(stripped_line)

    # Extract all links
    found_links = list(set(URL_PATTERN.findall(cleaned_text)))

    return StructuredResume(
        header="\n".join(sections_map["header"]),
        summary="\n".join(sections_map["summary"]),
        education="\n".join(sections_map["education"]),
        projects="\n".join(sections_map["projects"]),
        experience="\n".join(sections_map["experience"]),
        skills="\n".join(sections_map["skills"]),
        certifications="\n".join(sections_map["certifications"]),
        links=found_links,
        raw_text=cleaned_text,
    )
