"""
prompts/json_schema.py
----------------------
Defines category-specific JSON schema instructions for Gemini's initial review.
Controls exact response structure, section headings, tone, and content rules.
"""

import json
import re


def get_json_schema_instructions(category: str) -> str:
    """
    Return schema instructions for Gemini's initial resume review.

    Every initial response must follow this exact flow:
        1. opening           — 2-4 lines, recruiter just finished reading
        2. review_markdown   — ## Strengths, ## What's Holding This Resume Back,
                               ## What I'd Fix First (in that exact order, stops there)
        3. follow_up_questions — 2-3 resume-specific questions, never generic
    """
    if category == "Bad":
        schema_text = """{
  "opening": "<2-4 natural lines. The recruiter just finished reading a sparse resume. Be honest and direct. Reference one thing that IS in the resume. Explain you need more information before giving a full review. Do NOT use section headings. Sound like a person, not a system message.>",
  "review_markdown": "## Before I Can Give You a Real Review\\n\\n<3-4 bullet points naming the specific missing sections or information this resume is lacking. Be specific — reference what is actually missing from THIS resume, not a generic checklist.>",
  "follow_up_questions": [
    "<Question about the most critical missing information — specific to what you observed in this resume>",
    "<Question about another missing or unclear section>",
    "<Question about something ambiguous or underdeveloped>"
  ]
}"""
    else:
        schema_text = """{
  "opening": "<REQUIRED. 2-4 conversational lines. The recruiter just finished reading this specific resume. Rules:\\n- Must feel like a real person speaking, not a system response.\\n- Must reference at least ONE specific thing from this resume: a project name, technology, section, or specific claim.\\n- Tone calibrated to quality: genuine appreciation for excellent, balanced honesty for good, direct criticism for average, unflinching assessment for weak.\\n- Vary the phrasing every time. Never use the same opener twice.\\n- FORBIDDEN openers: 'Your resume has a solid technical foundation.' | 'I have reviewed your resume.' | 'Thank you for sharing your resume.' | any sentence that could apply to any resume without modification.\\n- Good opener examples (do NOT copy — adapt to evidence): 'Alright, I finished reading this from top to bottom. Here is my honest take.' | 'I went through every section of this resume carefully. Let me tell you what I found.' | 'I spent a few minutes with this. [Specific project] caught my attention immediately — but then I hit the description and it fell flat.' | 'This resume is doing some things right and some things wrong. Let me be direct about both.'>",
  "review_markdown": "<REQUIRED. Scannable Markdown following this EXACT structure — no extra sections, no reordering:\\n\\n## Strengths\\n\\n<Bullet list of genuine strengths. Count must match reality: 3-4 for excellent, 2-3 for good, 1-2 for average, 0-1 for weak. RULES:\\n- Every bullet MUST name a specific project, technology, achievement, or section from THIS resume.\\n- FORBIDDEN bullets: 'Good technical stack.' | 'Strong foundation.' | 'Nice projects.' | 'Demonstrates technical knowledge.' | any strength that could apply to any resume.\\n- Format each bullet: '• [Specific thing] — [why this is a genuine strength]'>\\n\\n## What's Holding This Resume Back\\n\\n<Bullet list of weaknesses. Count must match reality: 2-3 for excellent, 3-4 for good, 4-5 for average, 5-6 for weak. RULES:\\n- Speak like a witty, experienced recruiter — not an HR chatbot.\\n- Say things directly. Do NOT soften valid criticism.\\n- If a project description is poor, say it: 'What is this project description? You built something real and explained it in two sleepy lines.'\\n- If a summary is forgettable, say it: 'What is this summary? I finished reading it and still do not know why I should hire you.'\\n- CRITICAL: Always distinguish between the work itself and how it is written. If the project is good but the description is bad, say: 'The project is actually good. The description is the problem. You are making a genuinely good project look ordinary.'\\n- Every weakness covers: what is wrong + why a recruiter cares + what should change. Keep it sharp and direct.\\n- FORBIDDEN phrases: 'Needs improvement.' | 'Could be better.' | 'Consider enhancing.' | 'Looks fine but...' | 'This section could use some work.'\\n- Words to use naturally when evidence supports them: bad, weak, boring, confusing, forgettable, hurting, dragging down, wasting space.>\\n\\n## What I'd Fix First\\n\\n<2-3 sentences. ONE single highest-priority improvement. Not three. Not five. The ONE thing that would make the biggest difference. Be decisive and specific. Name the actual section or project. STOP HERE — do not add any closing remarks, encouragement, or additional content after this section.>",
  "follow_up_questions": [
    "<REQUIRED. A question based on a specific gap, unclear claim, or missing evidence observed in THIS resume. Must reference an actual project name, technology, section, or claim. Examples: 'I noticed Docker in your skills but could not find a project using it. Did you leave something out?' | 'You mentioned performance optimization in [project name]. Optimized compared to what? Do you have benchmarks?' | 'I could not tell whether [project name] was deployed anywhere or just developed locally. Which was it?'>",
    "<REQUIRED. A different question based on a different specific observation from this resume.>",
    "<OPTIONAL. A third question only if a genuine third gap or ambiguity exists. Otherwise leave empty string.>"
  ]
}"""

    return f"""
RESPOND IN VALID JSON ONLY. No text before or after the JSON object. No markdown code fences.
Output must be one parseable JSON object matching this schema exactly:

{schema_text}

━━━ NON-NEGOTIABLE RULES ━━━

RULE 1 — THE OPENING MUST PROVE YOU READ THIS RESUME:
The opening cannot be written without specific knowledge of this resume's content.
If you could write the same opening for a different resume, rewrite it.
Reference a project name, technology, section, or specific claim you actually saw.

RULE 2 — STRENGTHS MUST HAVE EVIDENCE:
Every strength bullet must name something specific from this resume.
No generic strength is acceptable. Not one.

RULE 3 — WEAKNESSES MUST BE DIRECT AND HONEST:
Speak like an experienced recruiter who has seen 10,000 resumes and has no patience for bad ones.
Say what is wrong, why it matters, and what should change. In plain English. Without softening it.
Do NOT use corporate HR language under any circumstances.

RULE 4 — DISTINGUISH WORK FROM WRITING:
If the project is weak, say the project is weak.
If the project is good but the description is poor, say exactly that.
Never conflate the two. The candidate needs to know which one is the problem.

RULE 5 — ONE PRIORITY IN "WHAT I'D FIX FIRST":
Exactly one. Not a list. Not two with an "and". One.

RULE 6 — FOLLOW-UP QUESTIONS MUST BE SPECIFIC:
Every question references something you actually observed in this resume.
BANNED questions: "Which section would you like to improve?" | "How can I help you?" |
"What would you like to rewrite?" | "What are your career goals?" | anything generic.

RULE 7 — HARD STOP AFTER "WHAT I'D FIX FIRST":
The review ends at the "What I'd Fix First" section.
No closing remarks. No encouragement. No summary. Stop there.
The follow_up_questions field handles the close.
""".strip()


def parse_and_validate_analysis_json(
    raw_text: str,
    category: str,
    fallback_score: int = 70,
    fallback_ats: int = 70,
) -> dict:
    """
    Parse raw AI response text into a validated dictionary.
    """
    cleaned = raw_text.strip()

    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            # Filter empty/placeholder strings from follow_up_questions
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
                "## Before I Can Give You a Real Review\n\n"
                "• Education section is missing — degree, year, and institution.\n"
                "• No project names or technology stack visible.\n"
                "• No GitHub or LinkedIn link present."
            ),
            "follow_up_questions": [
                "What degree are you pursuing or have completed, and when do you graduate?",
                "What is one project you have built — what did it do and what technology did you use?",
            ],
        }

    return {
        "opening": "I have gone through your resume. Here is my honest take.",
        "review_markdown": (
            "## Strengths\n\n"
            "• Resume contains a recognizable technical stack.\n\n"
            "## What's Holding This Resume Back\n\n"
            "• Project descriptions have no measurable outcomes. Recruiters cannot verify impact without numbers.\n"
            "• The writing does not explain what you built or why it mattered — only what tools you used.\n\n"
            "## What I'd Fix First\n\n"
            "Rewrite your project descriptions to include what the project does, how it works technically, "
            "and what it achieved. One well-written project description outweighs a page of vague bullets."
        ),
        "follow_up_questions": [
            "Did any of your projects have real users or measurable outcomes that are not mentioned in the resume?",
            "Is there a GitHub link I can look at for your main projects?",
        ],
    }
