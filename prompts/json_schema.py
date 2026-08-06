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

    The initial review must feel like a real recruiter who has genuinely
    read the resume from top to bottom — never like an AI report template.

    Schema fields:
        opening        — 2-4 natural lines summarizing the overall impression.
                         Calibrated to resume quality. Sounds like the recruiter
                         just finished reading the resume.
        review_markdown — Scannable Markdown: strengths, biggest weaknesses,
                          what to fix first. NO Roast labels. Dynamic headings.
        follow_up_questions — 2-3 intelligent, resume-specific questions based
                              on missing info, unclear claims, or improvement
                              opportunities. Never generic.
    """
    if category == "Bad":
        schema_text = """{
  "opening": "I went through your resume carefully. Honestly, there are some gaps I need to fill before I can give you a fair review.",
  "review_markdown": "### What I Need Before We Go Further\\\\nYour resume is missing information that every recruiter expects to see at first glance.\\\\n\\\\n• **Education**: Degree, year, and institution are not visible.\\\\n• **Projects**: No project names or technology stack I can evaluate.\\\\n• **Links**: GitHub or LinkedIn would make a huge difference here.",
  "follow_up_questions": [
    "What degree are you pursuing or have completed, and when do you graduate?",
    "What's one project you've built that you're proud of — what did it do and what technology did you use?",
    "Do you have a GitHub profile, even if it only has a couple of repositories?"
  ]
}"""
    else:
        schema_text = """{
  "opening": "<2-4 natural lines. Sounds like the recruiter just finished reading. CALIBRATE TO QUALITY:\\n  - Excellent resume: genuine appreciation, specific praise.\\n  - Good resume: balanced, honest, mentions one strong area and one concern.\\n  - Average: honest about weaknesses, but not dismissive.\\n  - Weak: direct and critical, but constructive.\\n  Examples: 'I went through this resume line by line. There is real technical depth here, but a few things are holding it back from landing interviews at top companies.' OR 'I spent a few minutes with this resume. It reads like a list of things you learned, not a record of things you built. That gap is costing you callbacks.'>",
  "review_markdown": "<Scannable Markdown in this EXACT ORDER — no deviations:\\n\\n1. ### ⭐ [Dynamic heading: 'What Stood Out' / 'What Impressed Me' / 'What's Working'] (2-4 bullets, genuine strengths only with specific resume evidence — NO filler like 'good technical skills')\\n\\n2. ### ⚠️ [Dynamic heading: 'What's Holding This Resume Back' / 'What Made Me Pause' / 'What Recruiters Will Question'] (3-5 bullets, each with: the problem + why it matters + one-line concrete fix)\\n\\n3. ### 🎯 What I'd Fix First (2-3 sentences. ONE highest-priority action only. Be decisive and specific.)>",
  "follow_up_questions": [
    "<Question 1: Based on a specific gap, unclear claim, or missing evidence in THIS resume. E.g. 'Did you deploy [actual project name] anywhere, or was it local-only?'>",
    "<Question 2: Based on a different specific observation. E.g. 'You listed Docker in skills but I couldn't find it used in any project — was it used somewhere not mentioned?'>",
    "<Optional Question 3: A third resume-specific question if a third genuine gap exists. If not, omit this field or leave it empty.>"
  ]
}"""

    return f"""
CRITICAL REQUIREMENT: YOU MUST RESPOND IN VALID JSON FORMAT ONLY.
Do NOT wrap your response in markdown text or natural language intro.
Your output must be a single parseable JSON object matching this schema exactly:

{schema_text}

FOLLOW-UP QUESTION RULES:
- Generate ONLY 2-3 questions maximum.
- Every question MUST reference a specific detail from THIS resume (project name, technology, gap, or unclear claim).
- NEVER ask: "Which section would you like to improve?" or "What are your career goals?" or any generic question.
- Each question should make the user feel the recruiter genuinely studied their resume.
- Questions must naturally lead to the next conversation turn.

OPENING RULES:
- 2-4 lines maximum. Natural, conversational. Not a template.
- Calibrate tone exactly to resume quality: exceptional praise for exceptional resumes, honest criticism for weak ones.
- Never start with "I" three times in a row. Vary the phrasing.
- Examples of good openings (adapt to evidence):
  * "I went through this resume from top to bottom. Here's my honest read."
  * "I spent a few minutes with this. There's real potential here, but it's not showing yet."
  * "I've read this carefully. This is a strong resume — I'll tell you exactly what I'd change."
  * "Alright, I've gone through this line by line. I have thoughts."
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
            return data
    except Exception:
        pass

    # Fallback if JSON parsing fails
    if category == "Bad":
        return {
            "opening": "I went through your resume. There are some key details missing before I can give you a proper review.",
            "review_markdown": "### What I Need Before We Go Further\n\n• Education details are missing.\n• No project names or technology stack visible.\n• GitHub or LinkedIn would help significantly.",
            "follow_up_questions": [
                "What degree are you pursuing or have completed?",
                "What's one project you're proud of? What did it do and what technology did you use?",
            ],
        }

    return {
        "opening": "I've gone through your resume. Here's my honest take.",
        "review_markdown": (
            "### What's Working\n\n• Resume has a technical foundation to build on.\n\n"
            "### What's Holding This Resume Back\n\n• Bullet points lack quantified impact — no numbers, no metrics.\n"
            "• Project descriptions are too vague to evaluate technical depth.\n\n"
            "### What I'd Fix First\n\nAdd measurable outcomes to every project bullet. "
            "Recruiters cannot verify impact without numbers."
        ),
        "follow_up_questions": [
            "Did any of your projects have real users or measurable outcomes you haven't mentioned yet?",
            "Is there a GitHub link I can look at for your main projects?",
        ],
    }
