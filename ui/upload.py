"""
ui/upload.py
------------
Upload component — handles file upload UI, validation display,
and the "Analyze Resume" button trigger.
Returns the uploaded file bytes and filename, or None if nothing uploaded.
No parsing logic here — only UI.
"""

import streamlit as st
from config import MAX_FILE_SIZE_MB, SUPPORTED_FORMATS


def render_upload_section() -> tuple[bytes | None, str | None, str]:
    """
    Render the file upload section of the landing page.

    Displays:
        - File uploader (PDF and DOCX only)
        - File info after upload
        - Optional Job Description text area
        - "Analyze Resume" button
        - Inline validation feedback

    Returns:
        Tuple of (file_bytes, filename, job_description) if user clicked Analyze, else (None, None, "").
    """
    st.markdown("""
    <div class="rr-upload-card rr-animate">
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="Drop your resume here or click to browse",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help=f"Supported: PDF, DOCX · Maximum size: {MAX_FILE_SIZE_MB}MB",
        label_visibility="visible",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is None:
        # Show supported format hint
        st.markdown("""
        <div class="rr-info" style="text-align:center; margin-top:0.5rem;">
            Supported formats: PDF · DOCX &nbsp;|&nbsp; Maximum size: 10MB
        </div>
        """, unsafe_allow_html=True)
        return None, None

    # File uploaded — show file info
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    file_size_kb = round(len(file_bytes) / 1024, 1)
    file_size_display = (
        f"{round(file_size_kb / 1024, 1)} MB"
        if file_size_kb > 1024
        else f"{file_size_kb} KB"
    )

    st.markdown(f"""
    <div class="rr-info" style="margin-top: 0.5rem;">
        📄 &nbsp;<strong>{filename}</strong> &nbsp;·&nbsp; {file_size_display}
    </div>
    """, unsafe_allow_html=True)

    # Optional Job Description input
    job_description = st.text_area(
        label="🎯 Target Job Description (Optional)",
        placeholder="Paste the job description or role details here for a targeted roast & skill match...",
        height=120,
        key="job_description_input",
    )

    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_clicked = st.button(
            "🔥 Analyze Resume",
            key="btn_analyze",
            use_container_width=True,
        )

    if analyze_clicked:
        return file_bytes, filename, job_description.strip()

    return None, None, ""


def render_clear_button() -> bool:
    """
    Render the 'Clear & Upload New Resume' button.

    Returns:
        True if the button was clicked, False otherwise.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.button(
            "↩ Upload New Resume",
            key="btn_clear",
            use_container_width=True,
        )
