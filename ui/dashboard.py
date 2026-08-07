"""
ui/dashboard.py
---------------
Dashboard component — renders the full analysis results.
Displays: scores, strengths, weaknesses, overall feedback, and conversation.
All data comes from Streamlit session state — no analysis happens here.
"""

import streamlit as st
from ui.styles import (
    render_score_cards,
    render_strengths,
    render_weaknesses,
    render_overall_feedback,
    render_divider,
    render_chat_message,
    render_chat_prompt_hint,
    render_section_header,
)


def render_analysis_results() -> None:
    """
    Render presentation-only conversational resume review results.

    Visual flow: Opening paragraph → Score cards → Review markdown → Follow-up questions.
    The opening renders first so the recruiter's words land before the numbers.
    """
    resume_score   = st.session_state.get("resume_score", 0)
    ats_score      = st.session_state.get("ats_score", 0)
    category       = st.session_state.get("resume_category", "Average")
    missing_fields = st.session_state.get("missing_fields", [])
    analysis_json  = st.session_state.get("analysis_json", {})
    stage          = st.session_state.get("conversation_stage", "INITIAL_REVIEW")



    # 1. Natural Recruiter Opening — rendered FIRST, before scores
    # Supports both new ("opening") and legacy ("first_reaction") field names
    opening = analysis_json.get("opening", analysis_json.get("first_reaction", ""))
    if opening:
        st.markdown(
            f'<div class="rr-feedback-card rr-animate" style="'
            f'border-left: 4px solid #f39c12; background: rgba(243,156,18,0.07); '
            f'padding: 18px 22px; margin-bottom: 24px; border-radius: 8px; line-height: 1.75;">'
            f'<span style="font-size: 1.05rem;">{opening}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # 2. Deterministic Score Cards — rendered AFTER opening (visual flow: opening → scores → review)
    render_score_cards(resume_score, ats_score)

    # 3. Handle AWAITING MISSING INFO State (Bad / Sparse Resumes)
    if stage == "AWAITING_MISSING_INFO" or category == "Bad":
        st.warning("⚠️ **Analysis Paused: Missing Critical Resume Information**")
        questions = analysis_json.get("follow_up_questions", analysis_json.get("missing_info_questions", []))
        if questions:
            st.markdown("### ❓ Please reply with the following details in the chat below:")
            for q in questions:
                st.markdown(f"• **{q}**")

        closing_p = analysis_json.get("closing_prompt", "Reply in the chat below so I can analyze your resume accurately!")
        st.caption(f"👉 *{closing_p}*")
        render_divider()
        return

    # 4. Render Dynamic AI Review Markdown (Presentation-Only — AI controls structure)
    review_markdown = analysis_json.get(
        "review_markdown",
        analysis_json.get("conversational_review", analysis_json.get("recruiter_opinion", ""))
    )
    if review_markdown:
        st.markdown(review_markdown)

    # 5. Resume-Specific Follow-Up Questions
    follow_up_questions = analysis_json.get("follow_up_questions", [])
    # Legacy fallback: if field absent, try closing_proposal as a single item
    if not follow_up_questions:
        legacy = analysis_json.get("closing_proposal", analysis_json.get("closing_question", ""))
        if legacy:
            follow_up_questions = [legacy]

    if follow_up_questions:
        st.markdown(
            '<div style="margin-top: 28px; padding: 18px 22px; '
            'background: rgba(99,102,241,0.07); border-radius: 8px; '
            'border-left: 3px solid #6366f1;">',
            unsafe_allow_html=True,
        )
        st.markdown("**Before we continue — a few things I want to ask:**")
        for q in follow_up_questions:
            if q and q.strip():
                st.markdown(f"• {q}")
        st.markdown("</div>", unsafe_allow_html=True)

    render_divider()




def render_conversation() -> None:
    """
    Render the full conversation history as chat bubbles.

    Reads from:
        st.session_state.conversation_history
        (list of {role: "user"|"model", content: str})
    Skips the first message (the initial AI analysis) which is shown above.
    """
    history = st.session_state.get("conversation_history", [])

    # Skip the first AI message (initial analysis already shown above)
    # Show all subsequent messages as chat bubbles
    follow_up = history[1:] if len(history) > 1 else []

    if follow_up:
        render_section_header("Conversation")
        for entry in follow_up:
            role    = entry.get("role", "user")
            content = entry.get("content", "")
            if content:
                render_chat_message(role, content)


def render_chat_interface() -> str | None:
    """
    Render the chat input box at the bottom of the results.

    Returns:
        The user's message string if submitted, else None.
    """
    render_chat_prompt_hint()

    user_input = st.chat_input(
        placeholder="Ask me anything — improve a project, suggest skills, rewrite summary...",
        key="chat_input",
    )
    return user_input


def render_clear_conversation_button() -> bool:
    """
    Render a small 'Clear Conversation' button.
    Clears only chat history — keeps resume and analysis intact.

    Returns:
        True if clicked, False otherwise.
    """
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        return st.button(
            "Clear Chat",
            key="btn_clear_chat",
            use_container_width=True,
        )
