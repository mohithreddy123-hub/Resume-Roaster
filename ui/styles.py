# pyrefly: ignore
# type: ignore
"""
ui/styles.py
------------
Injects the custom CSS stylesheet into Streamlit.
Provides helper functions for rendering styled components matching the multi-layered design system.
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
    """Render the hero section — logo badge, title, subtitle."""
    st.markdown("""
    <div class="rr-hero rr-animate">
        <div class="rr-logo-badge">🔥</div>
        <h1 class="rr-title">Resume Roaster</h1>
        <p class="rr-subtitle">
            If it's good, I'll respect it.<br>
            If it's bad, I'll roast it.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Score Cards (Apple / Notion Minimal Layered Style) ────────

def render_score_cards(resume_score: int, ats_score: int) -> None:
    """
    Render Apple/Notion-style minimal dual score cards with depth.

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


# ── Step-by-Step Analysis Progress Experience ─────────────────

def render_analysis_steps(current_step_index: int = 0) -> None:
    """
    Display a dynamic step-by-step progress indicator to show the AI is genuinely reading the resume.

    Steps:
        0. Reading resume...
        1. Extracting content...
        2. Calculating Resume Score...
        3. Calculating ATS Score...
        4. Generating Recruiter Feedback...
        5. Finalizing analysis...
    """
    steps = [
        "Reading resume...",
        "Extracting content...",
        "Calculating Resume Score...",
        "Calculating ATS Score...",
        "Generating Recruiter Feedback...",
        "Finalizing analysis...",
    ]

    steps_html = '<div class="rr-progress-card rr-animate">'
    for idx, step in enumerate(steps):
        if idx < current_step_index:
            steps_html += f'''
            <div class="rr-progress-step done">
                <span>✓</span> <span>{step}</span>
            </div>'''
        elif idx == current_step_index:
            steps_html += f'''
            <div class="rr-progress-step active">
                <div class="rr-progress-spinner"></div> <span>{step}</span>
            </div>'''
        else:
            steps_html += f'''
            <div class="rr-progress-step">
                <span style="opacity: 0.3;">○</span> <span style="opacity: 0.5;">{step}</span>
            </div>'''
    steps_html += '</div>'

    st.markdown(steps_html, unsafe_allow_html=True)


# ── Section Header ────────────────────────────────────────────

def render_section_header(title: str) -> None:
    """Render a clean section header."""
    st.markdown(
        f'<div class="rr-section-header">{title}</div>',
        unsafe_allow_html=True
    )


# ── Multi-Resume Prompt Banner ────────────────────────────────

def render_multi_resume_banner(resumes: list[dict]) -> tuple[bool, bool, int]:
    """
    Render a prompt when multiple resumes exist in the current session.

    Returns:
        Tuple of (compare_clicked, review_new_independently_clicked, selected_resume_index).
    """
    if len(resumes) < 2:
        return False, False, 0

    latest = resumes[-1]["filename"]
    previous = resumes[-2]["filename"]

    st.markdown(f"""
    <div class="rr-multi-resume-banner rr-animate">
        <div class="rr-multi-resume-title">💡 Multiple Resumes Detected</div>
        <div class="rr-multi-resume-desc">
            You currently have <strong>{len(resumes)} resumes</strong> in this session (e.g. <em>{previous}</em> and <em>{latest}</em>).
            Would you like me to compare them or review <em>{latest}</em> independently?
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        compare_clicked = st.button(
            f"⚡ Compare {previous} vs {latest}",
            key="btn_compare_resumes",
            use_container_width=True,
        )
    with col2:
        review_new_clicked = st.button(
            f"📄 Review {latest} Independently",
            key="btn_review_independently",
            use_container_width=True,
        )

    return compare_clicked, review_new_clicked, len(resumes) - 1


# ── Divider & Utilities ───────────────────────────────────────

def render_divider() -> None:
    """Render a subtle dark divider line."""
    st.markdown('<hr style="border:none; border-top:1px solid #2A2E39; margin:1.25rem 0;">', unsafe_allow_html=True)


def render_error(message: str) -> None:
    """Render a styled error message."""
    st.markdown(
        f'<div class="rr-error">⚠️ &nbsp;{message}</div>',
        unsafe_allow_html=True
    )


def render_chat_message(role: str, content: str) -> None:
    """Render a chat message bubble."""
    if role == "user":
        st.markdown(f"""
        <div class="rr-msg-user">
            <div class="rr-msg-user-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="rr-msg-ai">
            <div class="rr-msg-ai-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)
