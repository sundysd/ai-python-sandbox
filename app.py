import streamlit as st
from generator import generate_code
from executor import execute_code
from debugger import auto_debug
from validator import is_safe
from memory import add_to_history, load_history, clear_history
from logger import log_info, log_error
import io, csv

# Ensure session history exists
if "history" not in st.session_state:
    st.session_state.history = []

# Ensure session logs exist
if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

st.sidebar.title("Controls")

# OpenAI key helper
st.sidebar.markdown("### API Key Help")
st.sidebar.markdown(
    "[Get OpenAI API key](https://platform.openai.com/account/api-keys)" +
    " (opens in a new tab)", unsafe_allow_html=True
)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

theme = st.sidebar.selectbox("Theme", ["Light", "Dark"], index=1 if st.session_state.dark_mode else 0)
st.session_state.dark_mode = theme == "Dark"
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .main, .block-container, .stApp {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
            background-color: #1b2430 !important;
            color: #ffffff !important;
        }
        .stButton>button {
            background-color: #1f3a58 !important;
            color: #ffffff !important;
        }
        .stMarkdown, .stHeader, .stText {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("**OpenAI config**")
model = st.sidebar.selectbox("Model", ["gpt-5-mini", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"], index=0)
max_tokens = st.sidebar.slider("Max tokens", 64, 2048, 512, step=64)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, step=0.05)

if "openai_api_key" not in st.session_state or not st.session_state.openai_api_key.strip():
    st.sidebar.info("OpenAI key status: not set")
else:
    st.sidebar.success("OpenAI key status: set")

max_retries = st.sidebar.selectbox(
    "Max Auto-Debug Retries",
    [1, 2, 3, 5, 10],
    index=1,
    help="Number of times the AI will attempt to fix failed code"
)    

if st.sidebar.button("Clear history"):
    st.session_state.history = []
    st.sidebar.success("History cleared")

if st.sidebar.button("Clear session logs"):
    st.session_state.user_logs = []
    st.sidebar.success("Session logs cleared")

if st.sidebar.button("View logs"):
    # Show session logs (user-specific)
    st.sidebar.subheader("Session Logs")
    st.sidebar.text_area("Logs", "\n".join(st.session_state.user_logs), height=260)

st.title("AI Code Executor")

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

# OpenAI API Key input (session-safe)
openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    value=st.session_state.get("openai_api_key", ""),
    help="Go to OpenAI console, create key, paste into this box. Key is only stored in session; refresh loses it."
)

# Store the input in session state
st.session_state.openai_api_key = openai_api_key

# Optional: show setup guide
if st.button("📖 Show OpenAI API Key Setup Guide"):
    st.markdown("""
    **OpenAI API Key Setup - 5 Steps:**
    
    1. Open https://platform.openai.com/account/api-keys
    2. Sign up / log in to your OpenAI account
    3. Click `Create new secret key`
    4. Copy the key (shown only once - save it immediately!)
    5. Paste to the input box above and run
    
    📚 Official Guide: https://platform.openai.com/docs/guides/getting-started
    """)

user_input = st.text_area("Enter instruction:")

st.markdown(
    """
    **Example instructions you can try:**  
    - `print numbers from 1 to 10`  
    - `add 1, 2, 3, 5, 7 together`  
    - `create a list of squares from 1 to 5`  
    - `define a function that returns factorial of a number`
    """,
    unsafe_allow_html=True
)

if openai_api_key:
    st.session_state.openai_api_key = openai_api_key

history = []
try:
    history = load_history()
except Exception:
    history = []


if st.button("Run"):
    if not openai_api_key.strip():
        st.warning("Please enter your OpenAI API key.")
    elif not user_input.strip():
        st.warning("Please enter an instruction.")
    else:
        # Save key in session state (page session only, refresh clears)
        st.session_state.openai_api_key = openai_api_key

        # Initialize code and output
        code = None
        output = ""
        st.info("Generating Python code...")
        try:
            code = generate_code(openai_api_key, user_input, model=model, max_tokens=max_tokens, temperature=temperature)
            st.code(code, language="python")
            log_info("Code generation succeeded")
        except Exception as e:
            st.error(f"Code generation failed: {e}")
            log_error(f"Code generation failed: {e}")

        if not code:
            st.error("No generated code to execute.")
        else:
            # Validate generated code
            valid, msg = is_safe(code)
            if not valid:
                st.error(f"Generated code is unsafe: {msg}")
                log_error(f"Unsafe generated code: {msg}")
            else:
                # Execute with retries
                current_code = code
                for attempt in range(1, max_retries + 1):
                    try:
                        success, output = execute_code(current_code)
                        if success:
                            st.success(f"✅ Execution Result (Attempt {attempt}):")
                            st.text(output)
                            log_info(f"Execution succeeded on attempt {attempt}")
                            break
                        else:
                            st.warning(f"❌ Execution failed on attempt {attempt}: {output}")
                            log_error(f"Execution failed on attempt {attempt}: {output}")
                            if attempt < max_retries:
                                st.info(f"Attempting auto-debug (Attempt {attempt})...")
                                current_code = auto_debug(openai_api_key, current_code, output)
                                st.code(current_code, language="python")
                            else:
                                st.error("❌ Auto-debug retries exhausted")
                    except Exception as e:
                        st.error(f"Execution failed unexpectedly on attempt {attempt}: {e}")
                        log_error(f"Execution failed unexpectedly on attempt {attempt}: {e}")
                        if attempt < max_retries:
                            st.info(f"Attempting auto-debug after exception (Attempt {attempt})...")
                            current_code = auto_debug(openai_api_key, current_code, str(e))
                            st.code(current_code, language="python")
                        else:
                            st.error("❌ Auto-debug retries exhausted due to exceptions")

        # Save the interaction in session history
        st.session_state.history.append({
            "user": user_input,
            "assistant": output
        })
        log_info("Interaction saved to session history")



# show last 10 interactions
if st.session_state.history:
    st.subheader("History")
    st.table([
        {"Instruction": item["user"], "Result": item["assistant"]}
        for item in st.session_state.history[-10:]
    ])