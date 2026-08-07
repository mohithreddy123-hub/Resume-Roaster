# pyrefly: ignore
# type: ignore
"""
ui/sidebar.py
-------------
Sidebar Conversation History component for Resume Roaster.
Displays uploaded resumes in current session, allows switching active resume,
and triggering resume comparisons.
"""

import streamlit as st


def render_sidebar_history() -> dict | None:
    """
    Render the modern sidebar conversation history.

    Displays:
        - Uploaded resumes history list
        - Active resume indicator
        - Button to trigger resume comparison (if 2+ resumes)
        - Button to start a fresh upload

    Returns:
        Dict with action details if user clicked something in sidebar:
        {"action": "select_resume", "index": i} or
        {"action": "compare_resumes"} or
        {"action": "new_upload"} or None
    """
    resumes = st.session_state.get("resume_history", [])
    active_index = st.session_state.get("active_resume_index", 0)

    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 1rem 0;">
            <span style="font-size: 1.4rem;">🔥</span>
            <strong style="font-size: 1.1rem; margin-left: 0.4rem; color: #1F1F1F;">Resume Roaster</strong>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Upload New Resume", key="sidebar_btn_new", use_container_width=True):
            return {"action": "new_upload"}

        st.markdown('<div class="rr-sidebar-header">Today</div>', unsafe_allow_html=True)

        if not resumes:
            st.caption("No resumes uploaded yet.")
            return None

        # List uploaded resumes
        selected_index = None
        for idx, item in enumerate(resumes):
            filename = item.get("filename", f"Resume #{idx + 1}")
            score = item.get("resume_score", 0)
            is_active = (idx == active_index)

            # Icon & label formatting
            active_badge = " • active" if is_active else ""
            btn_label = f"📄 {filename} ({score}/100){active_badge}"

            if st.button(
                btn_label,
                key=f"sidebar_resume_{idx}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected_index = idx

        if selected_index is not None:
            return {"action": "select_resume", "index": selected_index}

        # Multi-Resume Comparison option
        if len(resumes) >= 2:
            st.markdown('<div class="rr-sidebar-header">Analysis</div>', unsafe_allow_html=True)
            if st.button("⚡ Compare Uploaded Resumes", key="sidebar_btn_compare", use_container_width=True):
                return {"action": "compare_resumes"}

    return None
