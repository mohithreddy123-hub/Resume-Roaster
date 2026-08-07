# pyrefly: ignore
# type: ignore
"""
app.py
------
Resume Roaster — Main Streamlit application entry point.
Conversation-first layout, multi-layered light theme, step-by-step analysis feedback,
multi-resume session history & AI resume comparison.

Flow:
    1. Page config & CSS loading
    2. Session state initialization
    3. Sidebar conversation history & session switcher
    4. Landing view / Upload screen (if no resumes analyzed)
    5. Results view / Conversation view (after analysis)
"""

import time
import streamlit as st

from config import APP_ICON, APP_TITLE, CATEGORY_BAD

# ── Page Config (Must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="Resume Roaster",
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS Stylesheet ────────────────────────────────
from ui.styles import load_css
load_css()

# ── Module Imports ────────────────────────────────────────────
from parser.parser import parse_resume
from utils.validator import validate_file, validate_extracted_text
from utils.cleaner import clean_text
from utils.helper import find_missing_fields
from parser.section_detector import extract_structured_resume

from analyzer.score import calculate_complete_metrics, get_score_explanation
from analyzer.classifier import classify_resume

from llm.gemini import send_message, GeminiError, GeminiAPIKeyMissingError
from prompts.system_prompt import get_system_prompt
from prompts.roast_prompt import get_roast_prompt
from prompts.json_schema import parse_and_validate_analysis_json
from prompts.conversation_prompt import build_conversation_user_prompt
from prompts.comparison_prompt import get_resume_comparison_prompt

from ui.styles import (
    render_hero,
    render_error,
    render_divider,
    render_analysis_steps,
    render_multi_resume_banner,
)
from ui.upload import render_upload_section, render_clear_button
from ui.dashboard import (
    render_analysis_results,
    render_conversation,
    render_chat_interface,
    render_clear_conversation_button,
)
from ui.sidebar import render_sidebar_history


# ── Session State Initialization ──────────────────────────────
def init_session_state() -> None:
    """Initialize session state defaults."""
    defaults = {
        "analysis_done":        False,
        "resume_history":       [],    # list of all uploaded resume dicts
        "active_resume_index":  0,
        "uploader_key":         0,     # dynamic widget key for file uploader resets
        "comparison_mode":      False,
        "comparison_result":    "",
        "resume_text":          "",
        "resume_score":         0,
        "ats_score":            0,
        "resume_category":      "",
        "strengths":            [],
        "weaknesses":           [],
        "overall_feedback":     "",
        "conversation_history": [],
        "missing_fields":       [],
        "error_message":        None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_resume_from_history(index: int) -> None:
    """Load a specific resume from history into active session state."""
    history = st.session_state.get("resume_history", [])
    if 0 <= index < len(history):
        item = history[index]
        st.session_state.active_resume_index = index
        st.session_state.analysis_done = True
        st.session_state.comparison_mode = False
        st.session_state.resume_text = item.get("resume_text", "")
        st.session_state.structured_resume = item.get("structured_resume", {})
        st.session_state.job_description = item.get("job_description", "")
        st.session_state.resume_score = item.get("resume_score", 0)
        st.session_state.ats_score = item.get("ats_score", 0)
        st.session_state.resume_category = item.get("resume_category", "")
        st.session_state.missing_fields = item.get("missing_fields", [])
        st.session_state.analysis_json = item.get("analysis_json", {})
        st.session_state.conversation_stage = item.get("conversation_stage", "INITIAL_REVIEW")
        st.session_state.conversation_history = item.get("conversation_history", [])


def reset_session() -> None:
    """Reset to clean upload view and increment uploader key."""
    st.session_state.analysis_done = False
    st.session_state.comparison_mode = False
    st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
    st.rerun()


def reset_all_sessions() -> None:
    """Completely wipe all resume history and session state."""
    st.session_state.resume_history = []
    st.session_state.active_resume_index = 0
    st.session_state.conversation_history = []
    reset_session()


# ── Analysis Pipeline with Step-by-Step Experience ─────────────
def run_analysis_pipeline(
    file_bytes: bytes, filename: str, job_description: str = ""
) -> bool:
    """
    Orchestrate deterministic parsing + Gemini recruiter review
    with a step-by-step visual feedback experience.
    """
    progress_placeholder = st.empty()

    # Step 0: Reading resume
    with progress_placeholder.container():
        render_analysis_steps(0)
    time.sleep(0.3)

    file_validation = validate_file(file_bytes, filename)
    if not file_validation.valid:
        st.session_state.error_message = file_validation.error
        progress_placeholder.empty()
        return False

    # Step 1: Extracting content
    with progress_placeholder.container():
        render_analysis_steps(1)
    time.sleep(0.3)

    parse_result = parse_resume(file_bytes, filename)
    if not parse_result.success:
        st.session_state.error_message = parse_result.error
        progress_placeholder.empty()
        return False

    text_validation = validate_extracted_text(parse_result.text)
    if not text_validation.valid:
        st.session_state.error_message = text_validation.error
        progress_placeholder.empty()
        return False

    # Step 2: Calculating Resume Score
    with progress_placeholder.container():
        render_analysis_steps(2)
    time.sleep(0.3)

    clean_resume_text = clean_text(parse_result.text)
    structured_resume = extract_structured_resume(clean_resume_text)
    missing_fields = find_missing_fields(clean_resume_text)

    metrics = calculate_complete_metrics(clean_resume_text, structured_resume.to_dict())
    python_score = metrics["resume_score"]
    ats_score    = metrics["ats_score"]
    category_ratings = metrics["category_ratings"]

    # Step 3: Calculating ATS Score
    with progress_placeholder.container():
        render_analysis_steps(3)
    time.sleep(0.3)

    category = classify_resume(python_score, missing_fields)
    score_explanation = get_score_explanation(
        resume_text=clean_resume_text,
        structured_resume=structured_resume.to_dict(),
        resume_score=python_score,
        ats_score=ats_score,
    )

    # Step 4: Generating Recruiter Feedback
    with progress_placeholder.container():
        render_analysis_steps(4)

    try:
        system_prompt = get_system_prompt()
        if category == CATEGORY_BAD or len(missing_fields) >= 3:
            from prompts.missing_prompt import get_missing_info_prompt
            analysis_query = get_missing_info_prompt(missing_fields, structured_resume.to_dict())
            conversation_stage = "AWAITING_MISSING_INFO"
        else:
            analysis_query = get_roast_prompt(
                structured_resume=structured_resume.to_dict(),
                category=category,
                python_score=python_score,
                ats_score=ats_score,
                missing_fields=missing_fields,
                job_description=job_description,
                score_explanation=score_explanation,
            )
            conversation_stage = "INITIAL_REVIEW"

        ai_raw_response = send_message(
            system_prompt=system_prompt,
            user_message=analysis_query,
            conversation_history=[],
            json_mode=True,
        )
    except GeminiAPIKeyMissingError:
        st.session_state.error_message = (
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY to your .env file and restart the app."
        )
        progress_placeholder.empty()
        return False
    except GeminiError as e:
        st.session_state.error_message = str(e)
        progress_placeholder.empty()
        return False

    # Step 5: Finalizing analysis
    with progress_placeholder.container():
        render_analysis_steps(5)

    analysis_json = parse_and_validate_analysis_json(
        ai_raw_response, category=category, fallback_score=python_score, fallback_ats=ats_score
    )
    analysis_json["category_ratings"] = category_ratings
    time.sleep(0.3)
    progress_placeholder.empty()

    initial_summary = analysis_json.get("opening", "Resume review completed.")
    conv_history = [{"role": "model", "content": initial_summary}]

    resume_entry = {
        "filename": filename,
        "resume_text": clean_resume_text,
        "structured_resume": structured_resume.to_dict(),
        "job_description": job_description,
        "resume_score": python_score,
        "ats_score": ats_score,
        "resume_category": category,
        "missing_fields": missing_fields,
        "analysis_json": analysis_json,
        "conversation_stage": conversation_stage,
        "conversation_history": conv_history,
    }

    # Store in history
    history_list = st.session_state.get("resume_history", [])
    history_list.append(resume_entry)
    st.session_state.resume_history = history_list

    # Load as active resume
    load_resume_from_history(len(history_list) - 1)
    return True


# ── AI Resume Comparison Pipeline ──────────────────────────────
def run_resume_comparison() -> None:
    """Run AI comparison between all uploaded resumes in the session."""
    resumes = st.session_state.get("resume_history", [])
    if len(resumes) < 2:
        return

    with st.spinner("Analyzing and comparing your uploaded resumes..."):
        try:
            prompt = get_resume_comparison_prompt(resumes)
            comparison_text = send_message(
                system_prompt=get_system_prompt(),
                user_message=prompt,
                conversation_history=[],
            )
            st.session_state.comparison_mode = True
            st.session_state.comparison_result = comparison_text
        except GeminiError as e:
            st.session_state.error_message = str(e)


# ── Conversation Handler ──────────────────────────────────────
def handle_user_message(user_message: str) -> None:
    """Process a follow-up user chat message."""
    structured_resume = st.session_state.get("structured_resume", {})
    python_score      = st.session_state.get("resume_score", 70)
    ats_score         = st.session_state.get("ats_score", 70)
    missing_fields    = st.session_state.get("missing_fields", [])
    job_description   = st.session_state.get("job_description", "")
    history           = st.session_state.get("conversation_history", [])

    full_user_message = build_conversation_user_prompt(
        user_message=user_message,
        structured_resume=structured_resume,
        python_score=python_score,
        ats_score=ats_score,
        missing_fields=missing_fields,
        job_description=job_description,
    )

    history.append({"role": "user", "content": user_message})

    try:
        with st.spinner("Thinking..."):
            ai_response = send_message(
                system_prompt=get_system_prompt(),
                user_message=full_user_message,
                conversation_history=history[:-1],
            )
    except GeminiAPIKeyMissingError:
        render_error("Gemini API key is missing. Please check your .env file.")
        return
    except GeminiError as e:
        render_error(str(e))
        return

    history.append({"role": "model", "content": ai_response})
    st.session_state.conversation_history = history

    # Sync history back to active resume_entry in resume_history
    active_idx = st.session_state.get("active_resume_index", 0)
    resumes = st.session_state.get("resume_history", [])
    if 0 <= active_idx < len(resumes):
        resumes[active_idx]["conversation_history"] = history
        st.session_state.resume_history = resumes


# ── Main Application ──────────────────────────────────────────
def main() -> None:
    """Main application entry point."""
    init_session_state()

    # 1. Sidebar Conversation History & Session Switcher
    sidebar_action = render_sidebar_history()
    if sidebar_action:
        act = sidebar_action.get("action")
        if act == "select_resume":
            load_resume_from_history(sidebar_action.get("index", 0))
            st.rerun()
        elif act == "sidebar_file_uploaded":
            file_bytes = sidebar_action.get("file_bytes")
            filename = sidebar_action.get("filename")
            if file_bytes and filename:
                success = run_analysis_pipeline(file_bytes, filename)
                if success:
                    st.rerun()
                else:
                    st.rerun()
        elif act == "compare_resumes":
            run_resume_comparison()
            st.rerun()
        elif act == "new_upload":
            reset_session()
            return
        elif act == "reset_all":
            reset_all_sessions()
            return

    # Always show hero header
    render_hero()

    # ── State 1: Landing / Upload Screen (No active analysis) ──
    if not st.session_state.analysis_done:

        if st.session_state.error_message:
            render_error(st.session_state.error_message)
            st.session_state.error_message = None

        file_bytes, filename, job_description = render_upload_section()

        if file_bytes is not None and filename is not None:
            success = run_analysis_pipeline(file_bytes, filename, job_description)
            if success:
                st.rerun()
            else:
                st.rerun()

        return

    # ── State 2: Active Analysis View ─────────────────────────

    # Button to upload another resume
    if render_clear_button():
        reset_session()
        return

    # Multi-Resume Banner (if 2+ resumes exist)
    resumes = st.session_state.get("resume_history", [])
    if len(resumes) >= 2:
        compare_clicked, review_new_clicked, new_idx = render_multi_resume_banner(resumes)
        if compare_clicked:
            run_resume_comparison()
            st.rerun()
        elif review_new_clicked:
            load_resume_from_history(new_idx)
            st.rerun()

    # ── Comparison View (If user clicked compare) ─────────────
    if st.session_state.comparison_mode:
        st.markdown("### ⚡ AI Resume Comparison")
        st.markdown(st.session_state.comparison_result)
        render_divider()
    else:
        # Standard Conversational Review
        render_analysis_results()

    # Follow-up Chat History
    render_conversation()

    # Handle clearing conversation history
    if render_clear_conversation_button():
        if st.session_state.conversation_history:
            st.session_state.conversation_history = [
                st.session_state.conversation_history[0]
            ]
            active_idx = st.session_state.get("active_resume_index", 0)
            if 0 <= active_idx < len(resumes):
                resumes[active_idx]["conversation_history"] = st.session_state.conversation_history
                st.session_state.resume_history = resumes
        st.rerun()

    # Chat Input for questions
    user_input = render_chat_interface()
    if user_input and user_input.strip():
        handle_user_message(user_input.strip())
        st.rerun()


# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
