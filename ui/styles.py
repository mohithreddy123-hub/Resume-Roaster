"""
ui/styles.py
------------
Injects the custom CSS stylesheet into Streamlit.
Also provides helper functions for rendering styled HTML components.
All design is centralized here — no inline styles scattered across files.
"""

import streamlit as st
from pathlib import Path


def load_css() -> None:
    """
    Inject the custom CSS stylesheet into the Streamlit app.
    Must be called once at the top of app.py after set_page_config.
    """
    css_path = Path(__file__).parent.parent / "static" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── Hero Section ──────────────────────────────────────────────

def render_hero() -> None:
    """Render the landing page hero — logo, title, subtitle."""
    st.markdown("""
    <div class="rr-hero rr-animate">
        <div class="rr-logo">🔥</div>
        <h1 class="rr-title">Resume Roaster</h1>
        <p class="rr-subtitle">
            Upload your resume.<br>
            If it's good, I'll respect it.&nbsp;&nbsp;If it's bad, I'll roast it.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Score Cards ───────────────────────────────────────────────

def render_score_cards(resume_score: int, ats_score: int) -> None:
    """
    Render the dual score cards (Resume Score + ATS Score).

    Args:
        resume_score: Overall resume score (0–100).
        ats_score:    Estimated ATS score (0–100).
    """
    st.markdown(f"""
    <div class="rr-scores-row rr-animate">
        <div class="rr-score-card">
            <div class="rr-score-number">{resume_score}</div>
            <div class="rr-score-label">Resume Score</div>
            <div class="rr-score-sublabel">out of 100</div>
        </div>
        <div class="rr-score-card">
            <div class="rr-score-number">{ats_score}</div>
            <div class="rr-score-label">ATS Score</div>
            <div class="rr-score-sublabel">estimated</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Section Header ────────────────────────────────────────────

def render_section_header(title: str) -> None:
    """Render a styled section header."""
    st.markdown(
        f'<div class="rr-section-header">{title}</div>',
        unsafe_allow_html=True
    )


# ── Strengths ─────────────────────────────────────────────────

def render_strengths(strengths: list[str]) -> None:
    """
    Render the strengths list with green styled items.

    Args:
        strengths: List of strength strings.
    """
    render_section_header(f"Strengths &nbsp;·&nbsp; {len(strengths)} found")

    if not strengths:
        st.markdown(
            '<div class="rr-info">No clear strengths detected in the resume.</div>',
            unsafe_allow_html=True
        )
        return

    items_html = ""
    for s in strengths:
        items_html += f"""
        <div class="rr-strength-item rr-animate">
            <span class="rr-strength-dot"></span>{s}
        </div>"""

    st.markdown(items_html, unsafe_allow_html=True)


# ── Weaknesses ────────────────────────────────────────────────

def render_weaknesses(weaknesses: list) -> None:
    """
    Render the weaknesses list with amber styled items.

    Args:
        weaknesses: List of Weakness objects (with .label and .reason).
    """
    render_section_header(f"Weaknesses &nbsp;·&nbsp; {len(weaknesses)} found")

    if not weaknesses:
        st.markdown(
            '<div class="rr-info">No major weaknesses detected. Strong resume!</div>',
            unsafe_allow_html=True
        )
        return

    items_html = ""
    for w in weaknesses:
        items_html += f"""
        <div class="rr-weakness-item rr-animate">
            <span class="rr-weakness-dot"></span>
            <span class="rr-weakness-label">{w.label}</span>
            <span class="rr-weakness-reason">{w.reason}</span>
        </div>"""

    st.markdown(items_html, unsafe_allow_html=True)


# ── Overall Feedback ──────────────────────────────────────────

def render_overall_feedback(feedback_text: str) -> None:
    """
    Render the overall feedback card.

    Args:
        feedback_text: The AI-generated overall feedback paragraph.
    """
    render_section_header("Overall Feedback")
    st.markdown(
        f'<div class="rr-feedback-card rr-animate">{feedback_text}</div>',
        unsafe_allow_html=True
    )


# ── Divider ───────────────────────────────────────────────────

def render_divider() -> None:
    """Render a styled horizontal divider."""
    st.markdown('<hr class="rr-divider">', unsafe_allow_html=True)


# ── Error Box ─────────────────────────────────────────────────

def render_error(message: str) -> None:
    """
    Render a styled error message.

    Args:
        message: The user-friendly error string.
    """
    st.markdown(
        f'<div class="rr-error">⚠️ &nbsp;{message}</div>',
        unsafe_allow_html=True
    )


# ── Chat Message ──────────────────────────────────────────────

def render_chat_message(role: str, content: str) -> None:
    """
    Render a chat message bubble.

    Args:
        role:    "user" or "model"
        content: The message text (markdown supported for AI messages).
    """
    if role == "user":
        st.markdown(f"""
        <div class="rr-msg-user">
            <div class="rr-msg-user-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # For AI messages, use st.markdown directly to render markdown properly
        with st.container():
            st.markdown(f"""
            <div class="rr-msg-ai">
                <div class="rr-msg-ai-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Wait Prompt ───────────────────────────────────────────────

def render_chat_prompt_hint() -> None:
    """Render a subtle hint to guide user conversation."""
    st.markdown("""
    <div class="rr-info" style="text-align:center; margin-top: 1.5rem;">
        Ask me anything about your resume — improve a project, suggest skills, rewrite your summary...
    </div>
    """, unsafe_allow_html=True)
