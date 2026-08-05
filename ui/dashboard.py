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
    Render the full resume analysis results from session state.

    Reads from:
        st.session_state.resume_score
        st.session_state.ats_score
        st.session_state.strengths
        st.session_state.weaknesses
        st.session_state.overall_feedback
    """
    resume_score = st.session_state.get("resume_score", 0)
    ats_score    = st.session_state.get("ats_score", 0)
    strengths    = st.session_state.get("strengths", [])
    weaknesses   = st.session_state.get("weaknesses", [])
    feedback     = st.session_state.get("overall_feedback", "")

    # Score Cards
    render_score_cards(resume_score, ats_score)

    # Strengths
    render_strengths(strengths)

    # Weaknesses
    render_weaknesses(weaknesses)

    # Overall Feedback
    if feedback:
        render_overall_feedback(feedback)

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
