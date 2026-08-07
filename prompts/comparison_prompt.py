# pyrefly: ignore
"""
prompts/comparison_prompt.py
-----------------------------
Generates prompt for AI comparison between multiple uploaded resumes in the session.
"""


def get_resume_comparison_prompt(resumes: list[dict]) -> str:
    """
    Build a comparison prompt for Gemini comparing two or more uploaded resumes.

    Args:
        resumes: List of dict objects containing {filename, structured_resume, score, ats}

    Returns:
        Formatted prompt string.
    """
    resume_blocks = ""
    for idx, r in enumerate(resumes):
        name = r.get("filename", f"Resume {chr(65+idx)}")
        score = r.get("resume_score", 0)
        ats = r.get("ats_score", 0)
        content = r.get("structured_resume", {})

        resume_blocks += f"""
━━━ RESUME {chr(65+idx)}: {name} (Resume Score: {score}/100, ATS: {ats}/100) ━━━
Header: {content.get('header', '')}
Summary: {content.get('summary', '')}
Education: {content.get('education', '')}
Experience: {content.get('experience', '')}
Projects: {content.get('projects', '')}
Skills: {content.get('skills', '')}
Certifications: {content.get('certifications', '')}
"""

    return f"""
You are Resume Roaster — the witty, experienced recruiter.
You have just read MULTIPLE RESUMES uploaded by this candidate.

{resume_blocks}

YOUR MISSION:
Compare these resumes directly like a veteran engineering director.
Tell the candidate which resume is stronger, why, and what each version does better.

Format your response in Markdown with these EXACT headings:

## 🏆 The Verdict: Which Resume Wins?
<2-4 lines explaining which version is stronger for job applications and why.>

## ⚔️ Head-to-Head Comparison
<Bullet breakdown comparing:
• Project presentation & technical depth
• Bullet point impact & metrics
• ATS compatibility & section clarity>

## 💡 What to Take From Each Version
<Concrete recommendations on how to merge the best parts of both resumes into one killer document.>

## ❓ Question for You
<One dynamic question about their career goal to help finalize the best version.>
""".strip()
