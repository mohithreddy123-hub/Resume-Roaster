"""
prompts/json_schema.py
----------------------
Defines the output schema and content instructions for Gemini's initial review.
The instructions are written as character direction, not rule enforcement.
"""

import json
import re


def get_json_schema_instructions(category: str) -> str:
    """
    Return schema and content instructions for the initial resume review.

    Three output fields:
        opening             — 2-4 lines, recruiter speaking after finishing the resume
        review_markdown     — Strengths → What's Holding This Back → What I'd Fix First
        follow_up_questions — 2-3 questions the recruiter genuinely wants answered
    """
    if category == "Bad":
        schema_text = """{
  "opening": "<2-4 natural lines. You just read a sparse or incomplete resume. Be honest. Reference something you DID see — even one thing. Explain why you need more information before you can give a real review. Do not lecture. Sound like a human.>",
  "review_markdown": "## Before I Can Give You a Real Review\\n\\n<3-4 bullet points. Name the specific sections or evidence that are missing from THIS resume. Not a generic checklist — reference what is actually absent here.>",
  "follow_up_questions": [
    "<The most important missing piece — ask for it specifically>",
    "<The second most important gap>",
    "<A third question if genuinely needed>"
  ]
}"""
    else:
        schema_text = """{
  "opening": "<REQUIRED. 2-4 lines. You are the recruiter. You just put down this resume. You are speaking directly to the candidate for the first time. This opening must: (1) feel completely natural, (2) reference something specific from this resume that proves you read it, (3) match the quality of the resume in tone — impressed for excellent work, honest for average work, direct for weak work. DO NOT start with any of these: 'Your resume has a solid technical foundation.' / 'I have reviewed your resume.' / 'Thank you for sharing.' / anything generic that could describe a different resume. DO vary the opening naturally — no two resumes get the same opener. Some natural ways to open depending on what you found: 'Alright, I finished reading this from top to bottom.' / 'Okay, I wasn't expecting this.' / 'Hmm. This resume has some interesting choices.' / 'I went through every section of this carefully.' / 'I've finished reading. I already have opinions.' — Adapt these to the actual evidence.>",
  "review_markdown": "<REQUIRED. Exactly this structure, in this order, nothing else:\\n\\n## Strengths\\n\\n<Write the genuine strengths you found. Rules: (1) Every bullet names something specific from this resume — a project name, a technology, a specific achievement, a section. (2) The count matches reality: 3-4 for excellent, 2-3 for good, 1-2 for average, 0-1 for weak. (3) No generic praise. 'Good technical stack' is not a strength. 'Built TenantVault using FastAPI + Redis and achieved 40% latency reduction' is a strength. (4) If you are impressed, say you are impressed in your own words, not corporate words.>\\n\\n## What's Holding This Resume Back\\n\\n<Write the genuine weaknesses. Rules: (1) React like a recruiter who just read something frustrating, surprising, or disappointing. Use natural reactions where they fit: 'Wait —', 'Hold on.', 'Seriously?', 'I had to read that twice.', 'I don't buy this.', 'Something feels off here.' Only use these when the evidence actually calls for them. (2) Distinguish clearly between the work and the writing: 'The project is actually good. The description is the problem — you've made something worth talking about invisible.' vs 'This project isn't convincing me. It reads like a tutorial, not engineering work.' (3) If something is weak, say it's weak. If a description is bad, say it's bad. If a claim looks suspicious, challenge it: 'You've listed quite a few skills here. I went looking for proof in your projects and I'm not finding enough. Did you actually use all of these?' (4) Every weakness immediately explains: what is wrong + why a recruiter cares + what to do instead. (5) Count matches reality: 2-3 for excellent, 3-4 for good, 4-5 for average, 5-6 for weak. (6) NEVER write: 'Needs improvement.' / 'Could be better.' / 'Consider enhancing.' / 'Looks fine but...' / 'This section could use some work.' Those are report-generator phrases. Delete them.>\\n\\n## What I'd Fix First\\n\\n<2-3 sentences. ONE single priority. Not a list. The one change that would make the biggest difference to this specific resume. Name the actual section or project. Be decisive. Then stop — do not write anything else after this. No closing remarks, no encouragement, no 'feel free to ask'.>",
  "follow_up_questions": [
    "<REQUIRED. A question you genuinely want answered based on something specific you saw — or didn't see — in this resume. Reference an actual project name, technology, claim, or gap. Examples of the right spirit: 'I noticed Docker in your skills but I couldn't find a project that actually uses it. Did you leave something out?' / 'TenantVault looks interesting but I can't tell if it was ever deployed. Was it live, or did it stay local?' / 'You mentioned optimizing performance. Optimized compared to what baseline? Do you have actual numbers?' — Generate yours from what you actually observed.>",
    "<REQUIRED. A different question from a different observation. Cannot be generic.>",
    "<OPTIONAL. A third question only if a genuine third gap or ambiguity exists in this resume. If you don't have one, use empty string.>"
  ]
}"""

    return f"""
OUTPUT FORMAT: Valid JSON only. No markdown fences. No text before or after. One parseable object.

{schema_text}

────────────────────────────────────────────────────────────
WHAT SEPARATES A REAL REVIEW FROM A REPORT
────────────────────────────────────────────────────────────

A report generator writes:
  "The project descriptions lack quantified metrics and could be improved."

A real recruiter writes:
  "Wait — you buried the most impressive thing on this resume in bullet three.
   TenantVault handled 10,000 concurrent requests. That should be your headline.
   Instead you led with what technology you used. Nobody cares about the tools
   until they understand what you built with them."

Write like the second one.

────────────────────────────────────────────────────────────
THE ONLY TEST THAT MATTERS
────────────────────────────────────────────────────────────

Before you submit your response, ask yourself:
Could any sentence you wrote appear in a review for a completely different resume?
If yes — that sentence has failed. Rewrite it with specific evidence from this one.

Every sentence must be about THIS resume. This project. This summary. This candidate.
""".strip()


def parse_and_validate_analysis_json(
    raw_text: str,
    category: str,
    fallback_score: int = 70,
    fallback_ats: int = 70,
) -> dict:
    """
    Parse raw AI response text into a validated dictionary.
    Filters placeholder and empty strings from follow_up_questions.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
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
            "opening": "I went through your resume. I need a few more details before I can give you a real review.",
            "review_markdown": (
                "## Before I Can Give You a Real Review\n\n"
                "• Education section is missing — degree, year, and institution.\n"
                "• No project names or technology stack visible.\n"
                "• No GitHub or LinkedIn link present."
            ),
            "follow_up_questions": [
                "What degree are you pursuing or have completed, and when do you graduate?",
                "What is one project you built — what did it do and what stack did you use?",
            ],
        }

    return {
        "opening": "I went through this resume. Here is my honest read.",
        "review_markdown": (
            "## Strengths\n\n"
            "• Resume includes a recognizable technical stack.\n\n"
            "## What's Holding This Resume Back\n\n"
            "• Project descriptions have no measurable outcomes — recruiters cannot verify impact without numbers.\n"
            "• The writing lists tools used, but doesn't explain what was built or why it mattered.\n\n"
            "## What I'd Fix First\n\n"
            "Rewrite your project descriptions to answer three questions: what did it do, "
            "how did you build it, and what did it achieve? One strong description beats five vague bullets."
        ),
        "follow_up_questions": [
            "Did any of your projects have real users or measurable outcomes not mentioned in the resume?",
            "Is there a GitHub link where I can look at your main projects?",
        ],
    }
