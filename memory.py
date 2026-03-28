import json
import os

HISTORY_FILE = "data/history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_history(user_input, ai_response):
    history = load_history()
    history.append({
        "user": user_input,
        "assistant": ai_response
    })
    save_history(history)

def clear_history():
    save_history([])
