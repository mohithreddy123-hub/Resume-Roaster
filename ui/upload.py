# pyrefly: ignore
# type: ignore
"""
ui/upload.py
------------
Upload component — handles custom hero file upload box UI, validation display,
optional job description input, and primary trigger button.
No parsing logic here — only UI rendering.
"""

import streamlit as st
from config import MAX_FILE_SIZE_MB


def render_upload_section() -> tuple[bytes | None, str | None, str]:
    """
    Render the custom file upload hero section of the landing page.

    Displays:
        - Standout hero upload card with icon badge and clear hierarchy
        - Streamlit drag & drop file uploader
        - Optional Job Description toggle / input
        - Primary "🔥 Analyze Resume" button

    Returns:
        Tuple of (file_bytes, filename, job_description) if user clicked Analyze,
        else (None, None, "").
    """
    st.markdown("""
    <div class="rr-upload-card rr-animate">
        <div class="rr-upload-header">
            <div class="rr-upload-icon-badge">📄</div>
            <div class="rr-upload-title">Drop your resume here</div>
            <div class="rr-upload-subtitle">PDF or DOCX &nbsp;·&nbsp; up to 10MB</div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="Select a file from your computer",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help=f"Supported: PDF, DOCX · Maximum size: {MAX_FILE_SIZE_MB}MB",
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is None:
        return None, None, ""

    # File uploaded — read bytes & details
    file_bytes = uploaded_file.read()
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

    # Optional Job Description input (collapsible expander for clean UI)
    with st.expander("🎯 Target Job Description (Optional)", expanded=False):
        job_description = st.text_area(
            label="Target Job Description",
            placeholder="Paste job description or target role details here for a tailored roast and ATS match...",
            height=110,
            key="job_description_input",
            label_visibility="collapsed",
        )

    # Primary Analyze Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_clicked = st.button(
            "🔥 Analyze Resume",
            key="btn_analyze",
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
            key="btn_clear",
            use_container_width=True,
        )
