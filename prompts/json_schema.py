"""
prompts/json_schema.py
----------------------
Defines category-specific JSON schema instructions for Gemini responses.
Controls structure, tone, and scannability of the initial recruiter review.
"""

import json
import re


def get_json_schema_instructions(category: str) -> str:
    """
    Return category-specific JSON schema instructions for Gemini.

    The first response after uploading a resume must feel like a real
    recruiter who has genuinely read the document from top to bottom.
    The user should think: "This AI actually read my resume."
    """
    if category == "Bad":
        schema_text = """{
  "opening": "<2-4 natural lines. The recruiter has just finished reading and needs more information before proceeding. Reference something specific that IS present in the resume — even if the overall content is sparse. Sound like a real person, not a system message.>",
  "review_markdown": "### Before I Can Give You a Real Review\\n\\nThere are some critical gaps I need filled before this resume can be evaluated properly:\\n\\n<3-4 bullets naming the specific missing sections or details detected in THIS resume>",
  "follow_up_questions": [
    "<Question about the most critical missing information — be specific about what IS in the resume and what's absent>",
    "<Question about a second missing or unclear section>",
    "<Question about something ambiguous or underdeveloped that you noticed>"
  ]
}"""
    else:
        schema_text = """{
  "opening": "<REQUIRED. 2-4 natural, conversational lines. This is the recruiter speaking after genuinely reading the resume. Rules:\\n- Must reference at least ONE specific thing from this resume: a project name, a technology, a section, a specific claim.\\n- Tone must match quality: excellent resumes get genuine appreciation + one honest concern; average resumes get direct honesty; weak resumes get unflinching criticism.\\n- Vary the opening phrase naturally. Do NOT use the same opener every time. Examples of good openers (adapt, don't copy): 'I finished reading your resume and I have thoughts.' | 'I went through every section of this carefully.' | 'I've spent a few minutes with this resume, and here is what genuinely stood out.' | 'Alright, I have gone through this line by line. Let me be straight with you.'\\n- FORBIDDEN: 'Your resume has a solid technical foundation.' | 'I have reviewed your resume.' | 'Thank you for sharing.' | any opener that could apply to any resume without modification.>",
  "review_markdown": "<Scannable Markdown. Follow this EXACT order, no deviations, no extra sections:\\n\\n### [Strengths heading — choose dynamically: 'What Stood Out' / 'What's Working' / 'What Impressed Me' / 'What I'd Keep']\\n<Bullet list. Number of bullets should match reality: 2-4 for excellent, 1-2 for average, 0-1 for weak. Each bullet MUST name a specific project, technology, achievement, or section from THIS resume. No bullet can be written without referencing actual resume content. Format: '• [Specific observation from resume] — [why this is strong]'>\\n\\n### [Weaknesses heading — choose dynamically: 'What's Holding This Resume Back' / 'What Made Me Pause' / 'What Recruiters Will Question' / 'Where I'd Push Back']\\n<Bullet list. This is the heart of the review. Number of bullets matches reality: 2-3 for excellent/good, 4-6 for average/weak. Each bullet has THREE parts in ONE concise statement: (1) what is wrong (specific, reference actual content), (2) why a recruiter would care, (3) what should change. Be direct. Do not soften valid criticism. Roast the resume, never the person. No corporate language. No filler. No 'consider improving'. Say: 'This doesn't convince me.' / 'This is wasting space.' / 'No recruiter believes this without evidence.'>\\n\\n### 🎯 What I'd Fix First\\n<2-3 sentences. ONE highest-priority action. Decisive and specific. Name the actual section or project to fix. Stop here — do not continue the review after this section.>",
  "follow_up_questions": [
    "<REQUIRED. Question 1: Based on a specific gap, unclear claim, or missing evidence in THIS resume. Must reference an actual project name, technology, or section you observed. Examples: 'I noticed TenantVault is listed but no deployment info — was it ever live?' | 'Docker appears in your skills but I cannot find it used in any project. Did you forget to include something?' | 'I could not tell from the resume whether your internship at [company] involved any independent work — what specifically did you build there?'>",
    "<REQUIRED. Question 2: A different specific observation — different topic from Question 1. Must reference actual resume content.>",
    "<OPTIONAL. Question 3: Only include if a genuine third specific gap or ambiguity exists. If nothing meaningful remains, leave this as an empty string and it will be filtered out.>"
  ]
}"""

    return f"""
CRITICAL REQUIREMENT: RESPOND IN VALID JSON FORMAT ONLY.
Do NOT wrap your response in markdown or add any text before or after the JSON object.
Your output must be one parseable JSON object matching this schema exactly:

{schema_text}

━━━ ABSOLUTE RULES FOR THIS RESPONSE ━━━

RULE 1 — PROVE YOU READ THE RESUME:
Every sentence in the opening and every strength bullet MUST reference something specific
from the extracted resume content above. If you write a sentence that could describe any resume
without modification, delete it and rewrite it with actual evidence from this resume.

RULE 2 — THREE-PART WEAKNESS STRUCTURE:
Every weakness bullet must cover: (1) what is wrong, (2) why a recruiter cares, (3) what to change.
All three in one concise, direct statement. No bullet should be a single vague claim.

RULE 3 — STOP AFTER "WHAT I'D FIX FIRST":
Do NOT continue the review beyond the "What I'd Fix First" section.
Do NOT add closing remarks, encouragement, or additional sections in review_markdown.
The follow_up_questions field handles the closing — not review_markdown.

RULE 4 — DYNAMIC POINT COUNT:
Do NOT force a fixed number of strengths or weaknesses.
Excellent resume: 3-4 strengths, 2-3 weaknesses.
Good resume: 2-3 strengths, 3-4 weaknesses.
Average resume: 1-2 strengths, 4-5 weaknesses.
Weak resume: 0-1 strengths, 5-6 weaknesses.
Match the evidence. Never add filler points to reach a target count.

RULE 5 — FOLLOW-UP QUESTIONS MUST PROVE YOU READ THE RESUME:
Each question must reference something specific you observed: a project name, a technology,
a section gap, an unclear claim, or an unexplained achievement.
BANNED questions: "Which section would you like to improve?" | "What are your career goals?"
| "How can I help you?" | "Would you like me to rewrite anything?" | any generic question.
""".strip()


def parse_and_validate_analysis_json(
    raw_text: str,
    category: str,
    fallback_score: int = 70,
    fallback_ats: int = 70,
) -> dict:
    """
    Parse raw AI response text into a validated dictionary matching the schema.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            # Filter empty strings from follow_up_questions
            if "follow_up_questions" in data:
                data["follow_up_questions"] = [
                    q for q in data["follow_up_questions"]
                    if q and q.strip() and not q.startswith("<")
                ]
            return data
    except Exception:
        pass

    # Fallback if JSON parsing fails entirely
    if category == "Bad":
        return {
            "opening": "I went through your resume. There are some key details I need before I can give you a proper review.",
            "review_markdown": (
                "### Before I Can Give You a Real Review\n\n"
                "• Education section is missing — degree, year, and institution.\n"
                "• No project names or technology stack visible.\n"
                "• GitHub or LinkedIn link would help significantly."
            ),
            "follow_up_questions": [
                "What degree are you pursuing or have completed, and when do you graduate?",
                "What's one project you've built — what did it do and what technology stack did you use?",
            ],
        }

    return {
        "opening": "I've gone through your resume. Here's my honest read.",
        "review_markdown": (
            "### What's Working\n\n"
            "• Resume contains a recognizable technical stack.\n\n"
            "### What's Holding This Resume Back\n\n"
            "• Bullet points have no measurable outcomes — recruiters cannot verify impact without numbers.\n"
            "• Project descriptions don't explain the technical decisions made, only the tools used.\n\n"
            "### 🎯 What I'd Fix First\n\n"
            "Rewrite your project bullets to include what you built, how it works, and what it achieved. "
            "A single strong project description with real metrics outweighs a page of vague bullets."
        ),
        "follow_up_questions": [
            "Did any of your projects have real users or measurable outcomes that aren't mentioned in the resume?",
            "Is there a GitHub link I can look at for your main projects?",
        ],
    }
