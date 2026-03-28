import streamlit as st
from generator import generate_code
from executor import execute_code
from debugger import auto_debug
from validator import is_safe
from memory import add_to_history, load_history, clear_history
from logger import log_info, log_error

st.sidebar.title("Controls")

# OpenAI key helper
st.sidebar.markdown("### API Key Help")
st.sidebar.markdown(
    "[Get OpenAI API key](https://platform.openai.com/account/api-keys)" +
    " (opens in a new tab)", unsafe_allow_html=True
)

if "has_openai_key" not in st.session_state:
    st.session_state.has_openai_key = False

if st.sidebar.checkbox("I already have key", value=True):
    st.session_state.has_openai_key = True
else:
    st.session_state.has_openai_key = False

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

if st.sidebar.button("Clear history"):
    clear_history()
    st.sidebar.success("History cleared")

if st.sidebar.button("View logs"):
    try:
        with open("data/logs.txt", "r", encoding="utf-8") as lf:
            st.sidebar.text_area("Logs", lf.read(), height=260)
    except FileNotFoundError:
        st.sidebar.warning("No logs yet")

history = load_history()
if history:
    import io, csv
    if st.sidebar.button("Export history CSV"):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["user", "assistant"])
        writer.writeheader()
        writer.writerows(history)
        st.sidebar.download_button("Download CSV", output.getvalue().encode("utf-8"), "history.csv", "text/csv")

st.title("AI Code Executor")

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

openai_api_key = ""
if st.session_state.has_openai_key:
    openai_api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
    st.caption("Go to OpenAI console, create key, paste into this box")
    st.caption("API Key only stored in session (not persisted to disk). Refresh page loses key for safety.")

    if st.button("📖 Show OpenAI API Key Setup Guide"):
        st.session_state.show_api_guide = not st.session_state.get("show_api_guide", False)

    if st.session_state.get("show_api_guide", False):
        st.markdown("""
        **OpenAI API Key Setup - 5 Steps:**
        
        1. Open https://platform.openai.com/account/api-keys
        2. Sign up / log in to your OpenAI account
        3. Click `Create new secret key`
        4. Copy the key (shown only once - save it immediately!)
        5. Paste to the input box above and run
        
        📚 Official Guide: https://platform.openai.com/docs/guides/getting-started
        """)
else:
    st.info("Click the link in the sidebar to get your OpenAI API Key, check 'I already have key', then enter it here.")

user_input = st.text_area("Enter instruction:")

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

        st.info("Generating Python code...")
        try:
            code = generate_code(openai_api_key, user_input, model=model, max_tokens=max_tokens, temperature=temperature)
            st.code(code, language="python")
            log_info("Code generation succeeded")
        except Exception as e:
            st.error(f"Code generation failed: {e}")
            log_error(f"Code generation failed: {e}")
            code = None

        if not code:
            st.error("No generated code to execute.")
        else:
            # Validate generated code
            valid, msg = is_safe(code)
            if not valid:
                st.error(f"Generated code is unsafe: {msg}")
                log_error(f"Unsafe generated code: {msg}")
            else:
                # Execute safely
                try:
                    success, output = execute_code(code)
                    if success:
                        st.success("✅ Execution Result:")
                        st.text(output)
                        log_info("Execution succeeded")
                    else:
                        st.error("❌ Execution failed:")
                        st.text(output)
                        log_error(f"Execution failed: {output}")
                        st.info("Attempting auto-debug...")
                        fixed_code = auto_debug(code, output)
                        st.code(fixed_code, language="python")
                        success2, output2 = execute_code(fixed_code)
                        if success2:
                            st.success("✅ Auto-Debug Execution Result:")
                            st.text(output2)
                            log_info("Auto-debug succeeded")
                        else:
                            st.error("❌ Auto-Debug also failed:")
                            st.text(output2)
                            log_error(f"Auto-debug failed: {output2}")

                except Exception as e:
                    st.error(f"Execution failed unexpectedly: {e}")
                    log_error(f"Execution failed unexpectedly: {e}")
                    st.info("Attempting auto-debug...")
                    try:
                        fixed_code = auto_debug(code, str(e))
                        st.code(fixed_code, language="python")
                        success2, output2 = execute_code(fixed_code)
                        if success2:
                            st.success("✅ Auto-Debug Execution Result:")
                            st.text(output2)
                            log_info("Auto-debug succeeded after unexpected failure")
                        else:
                            st.error("❌ Auto-Debug also failed:")
                            st.text(output2)
                            log_error(f"Auto-debug also failed: {output2}")
                    except Exception as e2:
                        st.error(f"Auto-debug failed unexpectedly: {e2}")
                        log_error(f"Auto-debug failed unexpectedly: {e2}")

        # 保存历史，便于复现
        add_to_history(user_input, output if 'output' in locals() else "")
        log_info("Interaction saved to history")

# 展示历史记录（最后 10 条）
if history:
    st.subheader("History")
    st.table([
        {"Instruction": item["user"], "Result": item["assistant"]}
        for item in history[-10:]
    ])