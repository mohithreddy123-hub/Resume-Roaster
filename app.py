"""
app.py
------
Resume Roaster — Main Streamlit application entry point.
This file only wires all modules together.
No business logic, no AI logic, no parsing logic lives here.

Flow:
    1. Load CSS
    2. Initialize session state
    3. Show hero
    4. If no resume analyzed yet → show upload section
    5. If resume analyzed → show results + conversation
"""

import streamlit as st

from config import APP_ICON, APP_TITLE

# ── Page Config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="Resume Roaster",
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load CSS ──────────────────────────────────────────────────
from ui.styles import load_css
load_css()

# ── Module Imports ────────────────────────────────────────────
from parser.parser import parse_resume
from utils.validator import validate_file, validate_extracted_text
from utils.cleaner import clean_text
from utils.helper import find_missing_fields

from analyzer.score import calculate_resume_score
from analyzer.classifier import classify_resume
from analyzer.ats import calculate_ats_score
from analyzer.strengths import extract_strengths
from analyzer.weaknesses import extract_weaknesses

from llm.gemini import send_message, build_resume_context, GeminiError, GeminiAPIKeyMissingError
from prompts.system_prompt import get_system_prompt
from prompts.roast_prompt import get_roast_prompt

from ui.styles import render_hero, render_error, render_divider
from ui.upload import render_upload_section, render_clear_button
from ui.dashboard import (
    render_analysis_results,
    render_conversation,
    render_chat_interface,
    render_clear_conversation_button,
)


# ── Session State Initialization ──────────────────────────────
def init_session_state() -> None:
    """Initialize all session state variables on first load."""
    defaults = {
        "analysis_done":        False,
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


def reset_session() -> None:
    """Clear all session state to reset the app for a new resume."""
    keys_to_clear = [
        "analysis_done", "resume_text", "resume_score", "ats_score",
        "resume_category", "strengths", "weaknesses", "overall_feedback",
        "conversation_history", "missing_fields", "error_message",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ── Resume Analysis Pipeline ──────────────────────────────────
def run_analysis_pipeline(
    file_bytes: bytes, filename: str, job_description: str = ""
) -> bool:
    """
    Orchestrate the full analysis flow.

    Steps:
        1. Validate file
        2. Parse resume
        3. Validate extracted text
        4. Clean text
        5. Calculate local scores & classify (for internal tone category)
        6. Extract strengths and weaknesses
        7. Generate AI feedback via Gemini (with optional Job Description)
        8. Extract strict scores from AI response
        9. Store everything in session state

    Args:
        file_bytes:      Raw bytes of the uploaded file.
        filename:        Original filename.
        job_description: Optional target Job Description text.

    Returns:
        True if analysis succeeded, False if any step failed.
    """
    # Step 1: Validate file
    file_validation = validate_file(file_bytes, filename)
    if not file_validation.valid:
        st.session_state.error_message = file_validation.error
        return False

    # Step 2: Parse resume
    with st.spinner("Reading your resume..."):
        parse_result = parse_resume(file_bytes, filename)

    if not parse_result.success:
        st.session_state.error_message = parse_result.error
        return False

    # Step 3: Validate extracted text
    text_validation = validate_extracted_text(parse_result.text)
    if not text_validation.valid:
        st.session_state.error_message = text_validation.error
        return False

    # Step 4: Clean the text
    clean_resume_text = clean_text(parse_result.text)

    # Step 5: Local score estimation & internal classification
    local_resume_score = calculate_resume_score(clean_resume_text)
    local_ats_score    = calculate_ats_score(clean_resume_text)
    category = classify_resume(local_resume_score)

    # Step 6: Extract strengths and weaknesses (local baseline)
    strengths  = extract_strengths(clean_resume_text)
    weaknesses = extract_weaknesses(clean_resume_text)

    # Step 7: Generate AI-powered overall feedback (passing Job Description)
    with st.spinner("Senior recruiter is reviewing your resume... This may take a moment."):
        try:
            system_prompt  = get_system_prompt()
            analysis_query = get_roast_prompt(clean_resume_text, category, job_description)

            ai_response = send_message(
                system_prompt=system_prompt,
                user_message=analysis_query,
                conversation_history=[],
            )
        except GeminiAPIKeyMissingError:
            st.session_state.error_message = (
                "Gemini API key is missing. "
                "Please add GEMINI_API_KEY to your .env file and restart the app."
            )
            return False
        except GeminiError as e:
            st.session_state.error_message = str(e)
            return False

    # Step 8: Parse strict scores from AI response (fallback to local if parse fails)
    ai_resume_score, ai_ats_score = _extract_ai_scores(
        ai_response, fallback_resume=local_resume_score, fallback_ats=local_ats_score
    )

    # Step 9: Parse overall feedback from AI response
    overall_feedback = _extract_overall_feedback(ai_response)

    # Step 10: Store everything in session state
    st.session_state.analysis_done       = True
    st.session_state.resume_text         = clean_resume_text
    st.session_state.job_description     = job_description
    st.session_state.resume_score        = ai_resume_score
    st.session_state.ats_score           = ai_ats_score
    st.session_state.resume_category     = category
    st.session_state.strengths           = strengths
    st.session_state.weaknesses          = weaknesses
    st.session_state.overall_feedback    = overall_feedback
    st.session_state.missing_fields      = find_missing_fields(clean_resume_text)
    st.session_state.error_message       = None

    # Store initial AI response as first entry in conversation history
    st.session_state.conversation_history = [
        {"role": "model", "content": ai_response}
    ]

    return True


import re


def _extract_ai_scores(
    ai_response: str, fallback_resume: int = 70, fallback_ats: int = 70
) -> tuple[int, int]:
    """
    Extract Resume Score and ATS Score from AI markdown response.

    Looks for patterns like:
        **Resume Score: 68/100**
        **ATS Score: 72/100**

    Returns:
        Tuple of (resume_score, ats_score) as integers.
    """
    resume_score = fallback_resume
    ats_score = fallback_ats

    # Pattern for Resume Score: 65/100 or Score: 65
    resume_match = re.search(r"Resume\s+Score:\s*(\d{1,3})\s*/\s*100", ai_response, re.IGNORECASE)
    if resume_match:
        try:
            resume_score = int(resume_match.group(1))
        except ValueError:
            pass

    # Pattern for ATS Score: 70/100
    ats_match = re.search(r"ATS\s+Score:\s*(\d{1,3})\s*/\s*100", ai_response, re.IGNORECASE)
    if ats_match:
        try:
            ats_score = int(ats_match.group(1))
        except ValueError:
            pass

    # Ensure bounds between 0 and 100
    resume_score = max(0, min(100, resume_score))
    ats_score = max(0, min(100, ats_score))

    return resume_score, ats_score


def _extract_overall_feedback(ai_response: str) -> str:
    """
    Extract the Overall Feedback section from the AI response.
    Falls back to the last paragraph if no clear section header found.

    Args:
        ai_response: Full AI response text.

    Returns:
        The overall feedback portion as a string.
    """
    lines = ai_response.split("\n")
    in_feedback = False
    feedback_lines: list[str] = []

    for line in lines:
        lower = line.lower().strip()
        if "overall feedback" in lower or "overall:" in lower:
            in_feedback = True
            continue
        if in_feedback:
            # Stop at next major section header
            if line.startswith("**") and line.endswith("**") and len(line) > 6:
                if "score" in lower or "strength" in lower or "weakness" in lower:
                    break
            if line.strip():
                feedback_lines.append(line.strip())

    if feedback_lines:
        return " ".join(feedback_lines)

    # Fallback: use the last non-empty paragraph
    paragraphs = [p.strip() for p in ai_response.split("\n\n") if p.strip()]
    return paragraphs[-1] if paragraphs else ai_response[:300]


# ── Conversation Handler ──────────────────────────────────────
def handle_user_message(user_message: str) -> None:
    """
    Process a follow-up user message and get AI response.

    Sends:
        - System prompt
        - Resume context
        - Full conversation history
        - User's new message

    Appends both user message and AI response to conversation history.

    Args:
        user_message: The user's input from the chat box.
    """
    resume_text = st.session_state.get("resume_text", "")
    history     = st.session_state.get("conversation_history", [])

    # Build context-aware user message
    full_user_message = build_resume_context(resume_text, user_message)

    # Append user message to history
    history.append({"role": "user", "content": user_message})

    try:
        with st.spinner("Thinking..."):
            ai_response = send_message(
                system_prompt=get_system_prompt(),
                user_message=full_user_message,
                conversation_history=history[:-1],  # exclude the just-added user msg
            )
    except GeminiAPIKeyMissingError:
        render_error("Gemini API key is missing. Please check your .env file.")
        return
    except GeminiError as e:
        render_error(str(e))
        return

    # Append AI response to history
    history.append({"role": "model", "content": ai_response})
    st.session_state.conversation_history = history


# ── Main App ──────────────────────────────────────────────────
def main() -> None:
    """Main application entry point."""
    init_session_state()

    # Always show the hero header
    render_hero()

    # ── State: No analysis done yet ──────────────────────────
    if not st.session_state.analysis_done:

        # Show any previous error
        if st.session_state.error_message:
            render_error(st.session_state.error_message)
            st.session_state.error_message = None

        # Show upload section
        file_bytes, filename, job_description = render_upload_section()

        # If user clicked Analyze
        if file_bytes is not None and filename is not None:
            success = run_analysis_pipeline(file_bytes, filename, job_description)
            if success:
                st.rerun()  # Rerun to show results in clean state
            else:
                # Error already stored in session — rerun to display it
                st.rerun()

        return

    # ── State: Analysis complete ──────────────────────────────

    # Option to upload a new resume
    if render_clear_button():
        reset_session()
        return

    render_divider()

    # Show analysis results (scores, strengths, weaknesses, feedback)
    render_analysis_results()

    # Show conversation history (follow-up messages)
    render_conversation()

    # Handle clearing conversation
    if render_clear_conversation_button():
        # Keep only the first message (initial analysis)
        if st.session_state.conversation_history:
            st.session_state.conversation_history = [
                st.session_state.conversation_history[0]
            ]
        st.rerun()

    # Chat input for follow-up questions
    user_input = render_chat_interface()

    if user_input and user_input.strip():
        handle_user_message(user_input.strip())
        st.rerun()


# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
