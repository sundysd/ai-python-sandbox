# logger.py
import datetime
import logging

logging.basicConfig(filename="data/logs.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def log_info(msg):
    # Write to global file (optional)
    logging.info(msg)
    # Write to session-specific logs if in Streamlit
    import streamlit as st
    if "user_logs" in st.session_state:
        st.session_state.user_logs.append(f"{datetime.datetime.now()} - INFO - {msg}")

def log_error(msg):
    logging.error(msg)
    import streamlit as st
    if "user_logs" in st.session_state:
        st.session_state.user_logs.append(f"{datetime.datetime.now()} - ERROR - {msg}")