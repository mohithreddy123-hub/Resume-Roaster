"""
app.py
------
Resume Roaster — Main Streamlit entry point.
This file only wires modules together. No business logic lives here.

Parts being built:
    Part 1 (current) — Foundation & Parsing  ✅
    Part 2           — AI Brain              🔜
    Part 3           — UI & Conversation     🔜
    Part 4           — Integration & Polish  🔜
"""

import streamlit as st
from config import APP_TITLE, APP_ICON

st.set_page_config(
    page_title="Resume Roaster",
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title(APP_TITLE)
st.info("🚧 Part 1 complete. UI will be wired in Part 3.")
