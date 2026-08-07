# pyrefly: ignore
# type: ignore
"""
ui/sidebar.py
-------------
Sidebar Conversation History component for Resume Roaster.
Displays uploaded resumes in current session, session analytics, active resume switcher,
multi-resume comparison triggers, and uploader reset buttons.
"""

import streamlit as st


def render_sidebar_history() -> dict | None:
    """
    Render the modern sidebar conversation history & session switcher.

    Displays:
        - App Branding header
        - "➕ Upload New Resume" button (resets uploader widget key)
        - Session Resumes list with active indicator & scores
        - Session Summary stats (Total, Avg Score, Avg ATS)
        - AI Resume Comparison trigger (if 2+ resumes)
        - Clear All Sessions reset trigger

    Returns:
        Dict with action details if user clicked something in sidebar, else None.
    """
    resumes = st.session_state.get("resume_history", [])
    active_index = st.session_state.get("active_resume_index", 0)

    with st.sidebar:
        # App Branding Header
        st.markdown("""
        <div style="padding: 0.25rem 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <div style="font-size: 1.6rem; line-height: 1;">🔥</div>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #1E293B; line-height: 1.1;">Resume Roaster</div>
                <div style="font-size: 0.75rem; color: #64748B;">AI Recruiter & Reviewer</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Primary Upload New Resume Button
        if st.button("➕ Upload New Resume", key="sidebar_btn_new", use_container_width=True):
            return {"action": "new_upload"}

        st.markdown('<div class="rr-sidebar-header">Uploaded Resumes</div>', unsafe_allow_html=True)

        if not resumes:
            st.caption("No resumes in session history yet. Upload your first resume to get started.")
            return None

        # List uploaded resumes with active badge & score
        selected_index = None
        for idx, item in enumerate(resumes):
            filename = item.get("filename", f"Resume #{idx + 1}")
            score = item.get("resume_score", 0)
            is_active = (idx == active_index and st.session_state.get("analysis_done", False))

            # Truncate long filenames cleanly
            short_name = filename if len(filename) <= 22 else filename[:19] + "..."
            active_badge = " ✓" if is_active else ""
            btn_label = f"📄 {short_name} ({score}){active_badge}"

            if st.button(
                btn_label,
                key=f"sidebar_resume_{idx}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=f"View analysis for {filename}",
            ):
                selected_index = idx

        if selected_index is not None:
            return {"action": "select_resume", "index": selected_index}

        # Multi-Resume Comparison option
        if len(resumes) >= 2:
            st.markdown('<div class="rr-sidebar-header">Compare & Analyze</div>', unsafe_allow_html=True)
            if st.button("⚡ Compare All Resumes", key="sidebar_btn_compare", use_container_width=True):
                return {"action": "compare_resumes"}

        # Session Stats Summary Box
        avg_score = round(sum(r.get("resume_score", 0) for r in resumes) / len(resumes))
        avg_ats = round(sum(r.get("ats_score", 0) for r in resumes) / len(resumes))

        st.markdown(f"""
        <div style="margin-top: 1.5rem; padding: 0.9rem; background: #F1F5F9; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 0.82rem;">
            <div style="font-weight: 700; color: #1E293B; margin-bottom: 0.4rem;">📊 Session Overview</div>
            <div style="color: #475569;">Resumes Uploaded: <strong>{len(resumes)}</strong></div>
            <div style="color: #475569;">Avg Resume Score: <strong>{avg_score}/100</strong></div>
            <div style="color: #475569;">Avg ATS Score: <strong>{avg_ats}/100</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Reset All Sessions", key="sidebar_btn_reset_all", use_container_width=True, type="secondary"):
            return {"action": "reset_all"}

    return None
