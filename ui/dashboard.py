"""
ui/dashboard.py
---------------
Dashboard & Conversation module — handles rendering the initial AI review,
Apple/Notion score cards, conversation history, and follow-up chat interface.
Presentation layer only — receives data from session state.
"""

import streamlit as st
from ui.styles import render_score_cards, render_divider


def render_analysis_results() -> None:
    """
    Render presentation-only conversational resume review results.

    Flow:
        1. Natural Recruiter Opening (rendered first so recruiter words land before numbers)
        2. Apple/Notion Minimal Score Cards (Resume Score + ATS Score)
        3. Dynamic AI Review Markdown (Strengths → Weaknesses → What to Fix First)
        4. Resume-Specific Follow-Up Questions Card
    """
    resume_score   = st.session_state.get("resume_score", 0)
    ats_score      = st.session_state.get("ats_score", 0)
    category       = st.session_state.get("resume_category", "Average")
    analysis_json  = st.session_state.get("analysis_json", {})
    stage          = st.session_state.get("conversation_stage", "INITIAL_REVIEW")

    # 1. Natural Recruiter Opening — rendered FIRST before score numbers
    opening = analysis_json.get("opening", analysis_json.get("first_reaction", ""))
    if opening:
        st.markdown(
            f'<div class="rr-opening-card rr-animate">'
            f'<span>{opening}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # 2. Minimal Score Cards — rendered AFTER opening
    render_score_cards(resume_score, ats_score)

    # 3. Handle AWAITING MISSING INFO State (Sparse / Bad Resumes)
    if stage == "AWAITING_MISSING_INFO" or category == "Bad":
        st.warning("⚠️ **Analysis Paused: Missing Critical Resume Information**")
        questions = analysis_json.get("follow_up_questions", analysis_json.get("missing_info_questions", []))
        if questions:
            st.markdown("### ❓ Please reply with the following details in the chat below:")
            for q in questions:
                st.markdown(f"• **{q}**")
        render_divider()
        return

    # 4. Render Dynamic AI Review Markdown (Strengths → Weaknesses → What I'd Fix First)
    review_markdown = analysis_json.get(
        "review_markdown",
        analysis_json.get("conversational_review", analysis_json.get("recruiter_opinion", ""))
    )
    if review_markdown:
        st.markdown(review_markdown)

    # 5. Resume-Specific Follow-Up Questions Card
    follow_up_questions = analysis_json.get("follow_up_questions", [])
    if not follow_up_questions:
        legacy = analysis_json.get("closing_proposal", analysis_json.get("closing_question", ""))
        if legacy:
            follow_up_questions = [legacy]

    if follow_up_questions:
        questions_html = '<div class="rr-followup-card rr-animate">'
        questions_html += '<div class="rr-followup-title">Before we continue — a few things I want to ask:</div>'
        for q in follow_up_questions:
            if q and q.strip() and not q.startswith("<"):
                questions_html += f'<div style="margin-bottom:0.4rem; font-size:0.93rem;">• {q}</div>'
        questions_html += '</div>'
        st.markdown(questions_html, unsafe_allow_html=True)

    render_divider()


def render_conversation() -> None:
    """
    Render the follow-up conversation history as clean chat bubbles.
    Initial review is shown in render_analysis_results(), so history skips index 0
    if it matches the initial summary.
    """
    history = st.session_state.get("conversation_history", [])

    # Exclude initial analysis summary if present as first item
    follow_ups = history[1:] if len(history) > 1 else []

    if not follow_ups:
        return

    for msg in follow_ups:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            st.markdown(f"""
            <div class="rr-msg-user rr-animate">
                <div class="rr-msg-user-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="rr-msg-ai rr-animate">
                <div class="rr-msg-ai-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)


def render_chat_interface() -> str | None:
    """
    Render the streamable chat input component at the bottom of the page.

    Returns:
        The text typed by the user, or None if empty.
    """
    return st.chat_input(
        placeholder="Reply to the recruiter or ask anything about your resume...",
        key="main_chat_input",
    )


def render_clear_conversation_button() -> bool:
    """Render a subtle reset button for clearing follow-up chat."""
    return st.button("💬 Clear Follow-up Chat", key="btn_clear_chat", type="secondary")
