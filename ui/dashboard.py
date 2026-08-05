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
    Render the full structured resume analysis results from session state.
    """
    resume_score   = st.session_state.get("resume_score", 0)
    ats_score      = st.session_state.get("ats_score", 0)
    missing_fields = st.session_state.get("missing_fields", [])
    analysis_json  = st.session_state.get("analysis_json", {})

    # 1. Deterministic Score Cards
    render_score_cards(resume_score, ats_score)

    # 2. Missing Fields Warning Box (if any detected)
    if missing_fields:
        st.warning(f"⚠️ **Missing Critical Resume Information**: {', '.join(missing_fields)}")

    render_section_header("🔥 Senior Recruiter Resume Review")

    if analysis_json:
        # First Impression
        first_imp = analysis_json.get("first_impression", "")
        if first_imp:
            st.info(f"**First Impression**: {first_imp}")

        # Category Ratings Table / Breakdown
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

        # Strengths Section
        strengths = analysis_json.get("strengths", [])
        if strengths:
            st.markdown("### ⭐ Key Strengths")
            for item in strengths:
                if isinstance(item, dict):
                    st.markdown(f"• **{item.get('title', 'Strength')}**: {item.get('explanation', '')}")
                else:
                    st.markdown(f"• {item}")

        # Weaknesses & Roasts Section
        weaknesses = analysis_json.get("weaknesses", [])
        if weaknesses:
            st.markdown("### 🔥 Critical Weaknesses & Immediate Fixes")
            for item in weaknesses:
                if isinstance(item, dict):
                    st.markdown(
                        f"• **{item.get('issue', 'Issue')}**: {item.get('why', '')}\n"
                        f"  👉 *Fix*: {item.get('fix', '')}"
                    )
                else:
                    st.markdown(f"• {item}")

        # Line by Line Audit
        audits = analysis_json.get("line_by_line_audit", [])
        if audits:
            st.markdown("### ✍️ Line-by-Line Bullet Audit")
            for audit in audits:
                if isinstance(audit, dict):
                    st.markdown(
                        f"• **Original**: *\"{audit.get('original', '')}\"*\n"
                        f"  - **Problem**: {audit.get('problem', '')}\n"
                        f"  - **Suggested Rewrite**: **\"{audit.get('improved', '')}\"**"
                    )

        # Skill Analysis
        skills_info = analysis_json.get("skill_analysis", {})
        if skills_info and isinstance(skills_info, dict):
            st.markdown("### 🛠️ Skill Depth & Market Alignment")
            keep = skills_info.get("skills_to_keep", [])
            missing_sk = skills_info.get("missing_recommended_skills", [])
            align = skills_info.get("alignment_feedback", "")
            if keep:
                st.markdown(f"• **Strong Skills to Highlight**: {', '.join(keep)}")
            if missing_sk:
                st.markdown(f"• **Recommended Market Skills**: {', '.join(missing_sk)}")
            if align:
                st.markdown(f"• **Alignment**: {align}")

        # Recruiter Highlights (15s Scan)
        highlights = analysis_json.get("recruiter_scan_highlights", [])
        if highlights:
            st.markdown("### ⚡ What Recruiters Notice in 15 Seconds")
            for h in highlights:
                st.markdown(f"• {h}")

        # Overall Strategy
        overall = analysis_json.get("overall_feedback", "")
        if overall:
            st.markdown("### 🎯 Overall Turnaround Strategy")
            st.success(overall)

        # Suggested Follow-up Questions
        questions = analysis_json.get("suggested_followup_questions", [])
        if questions:
            st.markdown("💡 **Suggested Follow-up Questions**:")
            for q in questions:
                st.caption(f"👉 *\"{q}\"*")

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
