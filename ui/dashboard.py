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
    Render category-driven conversational resume review results.
    Progressively discloses information based on internal category classification.
    """
    resume_score   = st.session_state.get("resume_score", 0)
    ats_score      = st.session_state.get("ats_score", 0)
    category       = st.session_state.get("resume_category", "Average")
    missing_fields = st.session_state.get("missing_fields", [])
    analysis_json  = st.session_state.get("analysis_json", {})
    stage          = st.session_state.get("conversation_stage", "INITIAL_REVIEW")

    # 1. Deterministic Score Cards
    render_score_cards(resume_score, ats_score)

    render_section_header("🔥 Senior Recruiter Resume Review")

    # 2. Handle AWAITING MISSING INFO State (Bad / Sparse Resumes)
    if stage == "AWAITING_MISSING_INFO" or category == "Bad":
        st.warning("⚠️ **Analysis Paused: Missing Critical Resume Information**")
        first_imp = analysis_json.get("first_impression", "")
        if first_imp:
            st.info(f"**First Impression**: {first_imp}")

        questions = analysis_json.get("missing_info_questions", [])
        if questions:
            st.markdown("### ❓ Please reply with the following details in the chat below:")
            for q in questions:
                st.markdown(f"• **{q}**")

        closing_p = analysis_json.get("closing_prompt", "Reply in the chat below so I can analyze your resume accurately!")
        st.caption(f"👉 *{closing_p}*")
        render_divider()
        return

    # 3. Category Breakdown Metrics (Mathematical source of truth)
    ratings = analysis_json.get("category_ratings", {})
    if ratings:
        st.markdown("### 📊 Category Breakdown")
        cols = st.columns(3)
        with cols[0]:
            st.metric("ATS Friendliness", f"{ratings.get('ats_friendliness', 7)}/10")
            st.metric("Technical Skills", f"{ratings.get('technical_skills', 7)}/10")
        with cols[1]:
            st.metric("Project Quality", f"{ratings.get('project_quality', 7)}/10")
            st.metric("Professional Summary", f"{ratings.get('professional_summary', 6)}/10")
        with cols[2]:
            st.metric("Placement Readiness", f"{ratings.get('placement_readiness', 7)}/10")
            st.metric("FAANG Readiness", f"{ratings.get('faang_readiness', 6)}/10")

    # 4. First Impression
    first_imp = analysis_json.get("first_impression", "")
    if first_imp:
        st.info(f"**First Impression**: {first_imp}")

    # 5. Render Output Specifically Based on Quality Category
    if category == "Excellent":
        strengths = analysis_json.get("strengths", [])
        if strengths:
            st.markdown("### ⭐ Key Strengths")
            for item in strengths:
                if isinstance(item, dict):
                    st.markdown(f"• **{item.get('title', 'Strength')}**: {item.get('explanation', '')}")
                else:
                    st.markdown(f"• {item}")

        weaknesses = analysis_json.get("weaknesses", [])
        if weaknesses:
            st.markdown("### 🔍 Executive Polish Points")
            for item in weaknesses:
                if isinstance(item, dict):
                    st.markdown(f"• **{item.get('issue', 'Polish')}**: {item.get('fix', '')}")
                else:
                    st.markdown(f"• {item}")

    elif category == "Good":
        strengths = analysis_json.get("strengths", [])
        if strengths:
            st.markdown("### ⭐ Key Strengths")
            for item in strengths:
                if isinstance(item, dict):
                    st.markdown(f"• **{item.get('title', 'Strength')}**: {item.get('explanation', '')}")
                else:
                    st.markdown(f"• {item}")

        weaknesses = analysis_json.get("weaknesses", [])
        if weaknesses:
            st.markdown("### 🔥 Light Roasts & Weaknesses")
            for item in weaknesses:
                if isinstance(item, dict):
                    st.markdown(
                        f"• **{item.get('issue', 'Issue')}**: {item.get('why', '')}\n"
                        f"  👉 *Fix*: {item.get('fix', '')}"
                    )
                else:
                    st.markdown(f"• {item}")

        improvements = analysis_json.get("key_improvements", [])
        if improvements:
            st.markdown("### ✍️ Specific Recommended Improvements")
            for imp in improvements:
                st.markdown(f"• {imp}")

    elif category == "Average":
        roasts = analysis_json.get("roasts_and_solutions", [])
        if roasts:
            st.markdown("### 🔥 Direct Recruiter Roasts & Solutions")
            for item in roasts:
                if isinstance(item, dict):
                    st.markdown(
                        f"• **{item.get('issue', 'Roast')}**: {item.get('why', '')}\n"
                        f"  👉 *Immediate Fix*: **{item.get('solution', '')}**"
                    )

    # 6. Overall Feedback & Closing Question
    overall = analysis_json.get("overall_feedback", "")
    if overall:
        st.success(f"**Recruiter Verdict**: {overall}")

    closing_q = analysis_json.get("closing_question", "Ask me to rewrite any section, suggest skills, or improve bullet points!")
    st.markdown(f"💡 **{closing_q}**")

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
