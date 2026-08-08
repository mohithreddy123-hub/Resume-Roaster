# pyrefly: ignore
# type: ignore
"""
ui/upload.py
------------
Upload component — single primary upload box UI.
Renders Streamlit file_uploader directly as the hero dropzone card.
"""

import streamlit as st
from config import MAX_FILE_SIZE_MB


def render_upload_section() -> tuple[bytes | None, str | None, str]:
    """
    Render the single primary file uploader section.

    Displays:
        - Streamlit drag & drop file uploader (styled directly as the hero card)
        - Selected File feedback tag
        - Optional Job Description input
        - Primary "🔥 Analyze Resume" button

    Returns:
        Tuple of (file_bytes, filename, job_description) if user clicked Analyze,
        else (None, None, "").
    """
    uploader_key_id = st.session_state.get("uploader_key", 0)

    uploaded_file = st.file_uploader(
        label="📄 Drop your resume here (PDF or DOCX, up to 10MB)",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help=f"Supported: PDF, DOCX · Maximum size: {MAX_FILE_SIZE_MB}MB",
        key=f"file_uploader_widget_{uploader_key_id}",
    )

    if uploaded_file is None:
        return None, None, ""

    # CRITICAL FIX: Use .getvalue() instead of .read()
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name
    file_size_kb = round(len(file_bytes) / 1024, 1)
    file_size_display = (
        f"{round(file_size_kb / 1024, 1)} MB"
        if file_size_kb > 1024
        else f"{file_size_kb} KB"
    )

    st.markdown(f"""
    <div class="rr-info rr-animate" style="margin-top: 1rem; text-align: center;">
        📄 <strong>{filename}</strong> &nbsp;·&nbsp; {file_size_display} &nbsp;✓ Ready to analyze
    </div>
    """, unsafe_allow_html=True)

    # Optional Job Description input
    with st.expander("🎯 Target Job Description (Optional)", expanded=False):
        job_description = st.text_area(
            label="Target Job Description",
            placeholder="Paste job description or target role details here for a tailored roast and ATS match...",
            height=110,
            key=f"job_description_input_{uploader_key_id}",
            label_visibility="collapsed",
        )

    # Primary Analyze Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_clicked = st.button(
            "🔥 Analyze Resume",
            key=f"btn_analyze_{uploader_key_id}",
            use_container_width=True,
        )

    if analyze_clicked:
        return file_bytes, filename, job_description.strip() if 'job_description' in locals() else ""

    return None, None, ""


def render_clear_button() -> bool:
    """
    Render the 'Upload Another Resume' button in conversation mode.

    Returns:
        True if the button was clicked, False otherwise.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(
            "➕ Upload Another Resume",
            key="btn_clear_another",
            use_container_width=True,
        )
