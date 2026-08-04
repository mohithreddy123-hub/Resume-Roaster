"""
config.py
---------
Central configuration for Resume Roaster.
All constants, thresholds, and weights are defined here.
No business logic — only configuration values.
"""

# ─── File Validation ─────────────────────────────────────────────────────────

MAX_FILE_SIZE_MB: int = 10
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_FORMATS: list[str] = [".pdf", ".docx"]

# ─── Resume Category Labels ───────────────────────────────────────────────────
# Internal use only — never displayed to the user as badges

CATEGORY_EXCELLENT: str = "Excellent"
CATEGORY_GOOD: str = "Good"
CATEGORY_AVERAGE: str = "Average"
CATEGORY_BAD: str = "Bad"

# ─── Score Thresholds ─────────────────────────────────────────────────────────
# Determines which category a resume falls into based on overall score

SCORE_THRESHOLDS: dict[str, int] = {
    CATEGORY_EXCELLENT: 80,   # 80–100
    CATEGORY_GOOD: 60,        # 60–79
    CATEGORY_AVERAGE: 40,     # 40–59
    CATEGORY_BAD: 0,          # 0–39
}

# ─── Section Scoring Weights (must sum to 100) ────────────────────────────────

SECTION_WEIGHTS: dict[str, int] = {
    "header": 10,
    "education": 15,
    "projects": 30,
    "skills": 20,
    "experience": 15,
    "formatting": 5,
    "grammar": 5,
}

# ─── Resume Sections to Detect ───────────────────────────────────────────────

RESUME_SECTIONS: list[str] = [
    "education",
    "skills",
    "projects",
    "experience",
    "certifications",
    "achievements",
    "summary",
    "objective",
    "languages",
    "publications",
    "awards",
    "volunteer",
    "interests",
]

# ─── Critical Fields That Must Exist ─────────────────────────────────────────
# If these are missing, ask the user before proceeding

CRITICAL_FIELDS: list[str] = [
    "name",
    "email",
    "phone",
    "education",
    "skills",
    "projects",
]

# ─── Section Heading Patterns ─────────────────────────────────────────────────
# Used by helper.py to detect sections via regex (case-insensitive)

SECTION_PATTERNS: dict[str, list[str]] = {
    "education": ["education", "academic background", "academics", "qualification"],
    "skills": ["skills", "technical skills", "technologies", "tech stack", "core competencies"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "works"],
    "experience": ["experience", "work experience", "internship", "employment", "professional experience"],
    "certifications": ["certifications", "certificates", "courses", "training"],
    "achievements": ["achievements", "accomplishments", "awards", "honors"],
    "summary": ["summary", "profile", "about me", "objective", "professional summary", "career objective"],
    "languages": ["languages", "language proficiency"],
    "links": ["github", "linkedin", "portfolio", "website"],
}

# ─── Gemini Model ─────────────────────────────────────────────────────────────

GEMINI_MODEL: str = "gemini-1.5-flash"
GEMINI_MAX_RETRIES: int = 3
GEMINI_RETRY_DELAY_SECONDS: int = 2

# ─── Strength & Weakness Limits ───────────────────────────────────────────────

MIN_STRENGTHS: int = 3
MAX_STRENGTHS: int = 8
MIN_WEAKNESSES: int = 2
MAX_WEAKNESSES: int = 8

# ─── Skill Suggestion Limits ──────────────────────────────────────────────────

MIN_SKILLS_TO_SUGGEST: int = 5
MAX_SKILLS_TO_SUGGEST: int = 10
FEW_SKILLS_THRESHOLD: int = 4  # If resume has ≤ this many skills, proactively mention it

# ─── Target Roles for Skill Suggestions ──────────────────────────────────────

TARGET_ROLES: list[str] = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "AI Engineer",
    "ML Engineer",
    "Data Analyst",
    "Data Scientist",
    "Cloud Engineer",
    "DevOps Engineer",
    "Cyber Security",
    "Other",
]

# ─── App Display ──────────────────────────────────────────────────────────────

APP_TITLE: str = "Resume Roaster 🔥"
APP_SUBTITLE: str = (
    "Upload your resume.\n"
    "If it's good, I'll respect it.\n"
    "If it's bad, I'll roast it."
)
APP_ICON: str = "🔥"
