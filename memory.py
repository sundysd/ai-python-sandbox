# memory.py
import streamlit as st

def load_history():
    """Return current user's session history"""
    return st.session_state.get("history", [])

def add_to_history(user_input, ai_response):
    """Add an interaction to current user's session history"""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "user": user_input,
        "assistant": ai_response
    })

def clear_history():
    """Clear current user's session history"""
    st.session_state.history = []