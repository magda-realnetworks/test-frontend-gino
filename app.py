import base64
import html
import json
import os
import time
import uuid
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
import streamlit as st
import streamlit.components.v1 as components
import urllib3

API_URL = "http://localhost:5002/question"
NEW_API_URL = "http://localhost:5002/question/v2"
CHAT_STORE = "chats.json"
CHAT_DIR = "chats"
CHAT_INDEX_STORE = os.path.join(CHAT_DIR, "index.json")
SETTINGS_STORE = "app_settings.json"
# Where "save as test case" writes its jsonl files. Defaults to the sibling
# chatbot repo's tests/ dir; override with the TEST_CASES_DIR env var.
TEST_CASES_DIR = os.environ.get(
    "TEST_CASES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chatbot", "tests"),
)
TEST_CASE_DIFFICULTIES = ("easy", "medium", "hard")
DEFAULT_HISTORY_LENGTH = 3
DEFAULT_MODEL = "OpenAI GPT4.1"
DEFAULT_QUERY_ENGINE_VERSION = "old"
QUERY_ENGINE_VERSION_OPTIONS = ("old", "new")
CHAT_LIST_LIMIT = 50
CHAT_SEARCH_LIMIT = 100
MODEL_OPTIONS = [
    "OpenAI GPT4.1",
    "OpenAI GPT5.5",
    "OpenAI GPT5.3 Codex Low",
    "OpenAI GPT5.4",
    "OpenAI GPT5.4 Low",
    "OpenAI GPT5.4 Mini",
    "OpenAI GPT5.4 Mini Low",
    "Google Gemini 2.5 Pro",
    "Google Gemini 2.5 Flash",
    "Google Gemini 3.5 Flash Low",
    "Google Gemini 3.1 Flash Lite Low",
    "AWS Claude 4.8 Opus",
    "AWS DeepSeek-R1",
    "AWS gpt-oss-120b",
]
CVOS_BASE = "cvos.dev.real.com"
CVOS_USER = "gino2"
CVOS_PASS = "Z2V0R2lubzEyMyE="
CVOS_DIRECTORY = "main"
CVOS_BASE_URL = (
    CVOS_BASE if CVOS_BASE.startswith(("http://", "https://")) else f"https://{CVOS_BASE}"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Superior SAFR")
st.title("GINO AI chat local version")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"],
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] [data-testid="stElementContainer"],
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] [data-testid="stMarkdown"],
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-chat_row_"] [data-testid="stHorizontalBlock"] {
        margin: 0 !important;
        padding: 0 !important;
        gap: 0.22rem !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-chat_list"] [data-testid="stVerticalBlock"] {
        gap: 0.08rem !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-chat_list"] [data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] .chat-row {
        position: relative;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] .chat-link {
        display: block;
        position: relative;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: transparent;
        color: #1e314f;
        text-decoration: none;
        font-weight: 500;
        line-height: 1.25;
        min-height: 2.2rem;
        padding: 0.44rem 3.95rem 0.44rem 0.65rem;
        margin: 0 !important;
        transition: all 0.12s ease;
    }
    [data-testid="stSidebar"] .chat-link:hover {
        border-color: rgba(203, 213, 225, 0.65);
        background: rgba(148, 163, 184, 0.16);
        color: #1e314f;
    }
    [data-testid="stSidebar"] .chat-row.active .chat-link {
        border-color: #ff4b4b;
        background: #ff4b4b;
        color: #ffffff;
    }
    [data-testid="stSidebar"] .chat-label {
        display: block;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    [data-testid="stSidebar"] .chat-actions {
        position: absolute;
        right: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        gap: 0.1rem;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.12s ease;
    }
    [data-testid="stSidebar"] .chat-row:hover .chat-actions,
    [data-testid="stSidebar"] .chat-row:focus-within .chat-actions {
        opacity: 1;
        pointer-events: auto;
    }
    [data-testid="stSidebar"] .chat-icon {
        width: 1.6rem;
        height: 1.6rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        color: inherit;
        text-decoration: none;
        background: transparent;
        line-height: 1;
    }
    [data-testid="stSidebar"] .chat-icon:hover {
        background: rgba(148, 163, 184, 0.2);
    }
    [data-testid="stSidebar"] div[class*="st-key-save_rename_"] button,
    [data-testid="stSidebar"] div[class*="st-key-cancel_rename_"] button {
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        min-height: 2.35rem;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-rename_input_"] input {
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-save_rename_"] button p,
    [data-testid="stSidebar"] div[class*="st-key-cancel_rename_"] button p {
        width: 100%;
        text-align: center !important;
        margin: 0;
    }
    [data-testid="stSidebar"] div[class*="st-key-open_chat_"] button {
        justify-content: flex-start;
        border-radius: 10px;
        min-height: 2.35rem;
        padding: 0 0.65rem !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-open_chat_"],
    [data-testid="stSidebar"] div[class*="st-key-edit_chat_"],
    [data-testid="stSidebar"] div[class*="st-key-delete_chat_"],
    [data-testid="stSidebar"] div[class*="st-key-rename_input_"],
    [data-testid="stSidebar"] div[class*="st-key-save_rename_"],
    [data-testid="stSidebar"] div[class*="st-key-cancel_rename_"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-open_chat_"] button p {
        width: 100%;
        text-align: left !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    [data-testid="stSidebar"] div[class*="st-key-edit_chat_"] button,
    [data-testid="stSidebar"] div[class*="st-key-delete_chat_"] button {
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        min-height: 2.35rem;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-edit_chat_"] button p,
    [data-testid="stSidebar"] div[class*="st-key-delete_chat_"] button p {
        width: 100%;
        text-align: center !important;
        margin: 0;
    }
    [data-testid="stSidebar"] div[class*="st-key-start_new_chat"] button {
        background: #d9f5e1 !important;
        color: #234a31 !important;
        border: 1px solid #9fd5af !important;
    }
    [data-testid="stSidebar"] div[class*="st-key-start_new_chat"] button:hover {
        background: #c8edd2 !important;
        color: #1f422b !important;
        border-color: #8bc89e !important;
    }
    /* Compact action row: keep the turn buttons inline and right-aligned. */
    [data-testid="stAppViewContainer"] div[class*="st-key-turn_actions_"] [data-testid="stHorizontalBlock"],
    [data-testid="stMain"] div[class*="st-key-turn_actions_"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        align-items: center !important;
        flex-wrap: nowrap !important;
        gap: 0.4rem !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-turn_actions_"] [data-testid="stColumn"],
    [data-testid="stMain"] div[class*="st-key-turn_actions_"] [data-testid="stColumn"] {
        width: auto !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button,
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button {
        width: auto !important;
        min-height: 0 !important;
        border-radius: 999px !important;
        background: transparent !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 0.28rem 0.85rem !important;
        box-shadow: none !important;
        transition: all 0.12s ease !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button p,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button p,
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button p,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button p {
        white-space: nowrap !important;
        margin: 0 !important;
    }
    /* Delete = subtle rose ghost pill */
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button {
        border: 1px solid rgba(239, 68, 68, 0.45) !important;
        color: #e11d48 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button:hover,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button:hover {
        border-color: rgba(239, 68, 68, 0.6) !important;
        background: rgba(239, 68, 68, 0.08) !important;
        color: #be123c !important;
    }
    /* Retry = subtle emerald ghost pill */
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button {
        border: 1px solid rgba(16, 185, 129, 0.5) !important;
        color: #059669 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button:hover,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button:hover {
        border-color: rgba(16, 185, 129, 0.65) !important;
        background: rgba(16, 185, 129, 0.08) !important;
        color: #047857 !important;
    }
    /* Disabled state for both */
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button:disabled,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button:disabled,
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button:disabled,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button:disabled,
    [data-testid="stAppViewContainer"] div[class*="st-key-save_test_case_btn_"] button:disabled,
    [data-testid="stMain"] div[class*="st-key-save_test_case_btn_"] button:disabled {
        border-color: rgba(148, 163, 184, 0.35) !important;
        color: #94a3b8 !important;
        background: transparent !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-save_test_case_btn_"],
    [data-testid="stMain"] div[class*="st-key-save_test_case_btn_"] {
        display: flex;
        justify-content: flex-end;
    }
    /* Save = subtle indigo ghost pill */
    [data-testid="stAppViewContainer"] div[class*="st-key-save_test_case_btn_"] button,
    [data-testid="stMain"] div[class*="st-key-save_test_case_btn_"] button {
        width: auto !important;
        min-height: 0 !important;
        border-radius: 999px !important;
        border: 1px solid rgba(99, 102, 241, 0.45) !important;
        background: transparent !important;
        color: #4f46e5 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 0.28rem 0.85rem !important;
        box-shadow: none !important;
        transition: all 0.12s ease !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-save_test_case_btn_"] button:hover,
    [data-testid="stMain"] div[class*="st-key-save_test_case_btn_"] button:hover {
        border-color: rgba(99, 102, 241, 0.65) !important;
        background: rgba(99, 102, 241, 0.08) !important;
        color: #4338ca !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-save_test_case_btn_"] button p,
    [data-testid="stMain"] div[class*="st-key-save_test_case_btn_"] button p {
        white-space: nowrap !important;
        margin: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_json_atomic(path: str, data):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp_path, path)


def load_json(path: str, fallback):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def now_ms() -> int:
    return int(time.time() * 1000)


def chat_file_path(chat_id: str) -> str:
    return os.path.join(CHAT_DIR, f"{chat_id}.json")


def chat_summary(chat: dict) -> dict:
    turns = chat.get("turns") or []
    return {
        "id": chat.get("id") or generate_chat_id(),
        "title": normalize_chat_title(chat.get("title") or "New chat"),
        "turn_count": len(turns),
        "updated_at": chat.get("updated_at") or now_ms(),
    }


def normalize_chat_summary(summary: dict) -> dict:
    normalized = dict(summary or {})
    normalized["id"] = normalized.get("id") or generate_chat_id()
    normalized["title"] = normalize_chat_title(normalized.get("title") or "New chat")
    normalized["turn_count"] = max(0, int(normalized.get("turn_count") or 0))
    normalized["updated_at"] = int(normalized.get("updated_at") or now_ms())
    return normalized


def load_legacy_chats():
    data = load_json(CHAT_STORE, [])
    return data if isinstance(data, list) else []


def load_chats():
    index = load_json(CHAT_INDEX_STORE, None)
    if isinstance(index, list):
        return [normalize_chat_summary(chat) for chat in index]

    legacy_chats = load_legacy_chats()
    if not legacy_chats:
        return []

    summaries = []
    for chat in legacy_chats:
        if not isinstance(chat, dict):
            continue
        if not chat.get("id"):
            chat["id"] = generate_chat_id()
        summary = chat_summary(chat)
        chat["title"] = summary["title"]
        chat["updated_at"] = summary["updated_at"]
        save_json_atomic(chat_file_path(summary["id"]), chat)
        summaries.append(summary)
    save_chats(summaries)
    return summaries


def save_chats(chats):
    save_json_atomic(CHAT_INDEX_STORE, [normalize_chat_summary(chat) for chat in chats])


def load_chat(chat_id: str) -> dict:
    chat = load_json(chat_file_path(chat_id), None)
    if isinstance(chat, dict):
        chat.setdefault("id", chat_id)
        chat.setdefault("title", "New chat")
        chat.setdefault("turns", [])
        return chat
    return {"id": chat_id, "title": "New chat", "turns": []}


def get_active_chat() -> dict:
    chat_id = st.session_state.chats[st.session_state.active_chat].get("id")
    cached = st.session_state.get("active_chat_data")
    if isinstance(cached, dict) and cached.get("id") == chat_id:
        return cached
    st.session_state.active_chat_data = load_chat(chat_id)
    return st.session_state.active_chat_data


def save_active_chat(chat: dict):
    chat["updated_at"] = now_ms()
    save_json_atomic(chat_file_path(chat["id"]), chat)
    idx = find_chat_index_by_id(st.session_state.chats, chat["id"])
    if idx is not None:
        st.session_state.chats[idx].update(chat_summary(chat))
    save_chats(st.session_state.chats)


def load_settings():
    if not os.path.exists(SETTINGS_STORE):
        return {}
    try:
        with open(SETTINGS_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_settings(settings):
    save_json_atomic(SETTINGS_STORE, settings)


def normalize_history_length(value) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return DEFAULT_HISTORY_LENGTH


def normalize_model(value) -> str:
    if isinstance(value, str) and value in MODEL_OPTIONS:
        return value
    return DEFAULT_MODEL


def normalize_query_engine_version(value) -> str:
    if value in QUERY_ENGINE_VERSION_OPTIONS:
        return value
    return DEFAULT_QUERY_ENGINE_VERSION


def query_engine_url() -> str:
    """Return the endpoint for the selected query engine."""
    if st.session_state.get("query_engine_version") == "new":
        return NEW_API_URL
    return API_URL


def generate_chat_id() -> str:
    return uuid.uuid4().hex


def ensure_chat_ids(chats) -> bool:
    changed = False
    seen = set()
    for chat in chats:
        chat_id = chat.get("id")
        if not isinstance(chat_id, str) or not chat_id or chat_id in seen:
            chat_id = generate_chat_id()
            chat["id"] = chat_id
            changed = True
        seen.add(chat_id)
    return changed


def new_chat():
    return {"id": generate_chat_id(), "title": "New chat", "turns": [], "updated_at": now_ms()}


def normalize_chat_title(value: str) -> str:
    cleaned = (value or "").strip()
    return cleaned[:60] or "New chat"


SKIP_SELECTION_QUERY_KEY = "_skip_chat_selection_chat_id"
RETRY_STATE_KEY = "_retry_state"
RETRY_QUESTION_KEY = "_retry_question"
RETRY_CHAT_ID_KEY = "_retry_chat_id"
RETRY_BACKUP_TURN_KEY = "_retry_backup_turn"
SEND_STATE_KEY = "_send_state"
SEND_QUESTION_KEY = "_send_question"
SEND_CHAT_ID_KEY = "_send_chat_id"


def rename_input_key(index: int) -> str:
    return f"rename_input_{index}"


def start_rename(index: int, title: str):
    st.session_state.rename_target = index
    st.session_state[rename_input_key(index)] = title


def clear_rename_state():
    target = st.session_state.get("rename_target")
    if target is not None:
        st.session_state.pop(rename_input_key(target), None)
    st.session_state.rename_target = None


def commit_rename(index: int):
    if index < 0 or index >= len(st.session_state.chats):
        clear_rename_state()
        return
    input_key = rename_input_key(index)
    title = normalize_chat_title(st.session_state.get(input_key, ""))
    st.session_state.chats[index]["title"] = title
    chat_id = st.session_state.chats[index].get("id")
    if chat_id:
        chat = load_chat(chat_id)
        chat["title"] = title
        if index == st.session_state.active_chat:
            st.session_state.active_chat_data = chat
        save_json_atomic(chat_file_path(chat_id), chat)
    save_chats(st.session_state.chats)
    clear_rename_state()


def delete_chat_at_index(index: int):
    rename_target = st.session_state.rename_target
    removed = st.session_state.chats.pop(index)
    removed_chat_id = removed.get("id")
    if removed_chat_id:
        try:
            os.remove(chat_file_path(removed_chat_id))
        except FileNotFoundError:
            pass
    if not st.session_state.chats:
        chat = new_chat()
        save_json_atomic(chat_file_path(chat["id"]), chat)
        st.session_state.chats = [chat_summary(chat)]
        st.session_state.active_chat = 0
    elif index < st.session_state.active_chat:
        st.session_state.active_chat -= 1
    elif index == st.session_state.active_chat:
        st.session_state.active_chat = min(index, len(st.session_state.chats) - 1)
    st.session_state.pop("active_chat_data", None)
    if rename_target is not None:
        if index == rename_target:
            clear_rename_state()
        elif index < rename_target:
            renamed_text = st.session_state.pop(rename_input_key(rename_target), "")
            st.session_state.rename_target -= 1
            st.session_state[rename_input_key(st.session_state.rename_target)] = renamed_text


def move_chat_to_end(index: int):
    if index < 0 or index >= len(st.session_state.chats):
        return
    last_index = len(st.session_state.chats) - 1
    if index == last_index:
        return
    moved_chat = st.session_state.chats.pop(index)
    st.session_state.chats.append(moved_chat)

    active_index = st.session_state.active_chat
    if active_index == index:
        st.session_state.active_chat = last_index
    elif active_index > index:
        st.session_state.active_chat = active_index - 1

    rename_target = st.session_state.rename_target
    if rename_target is None:
        return
    if rename_target == index:
        renamed_text = st.session_state.pop(rename_input_key(rename_target), "")
        st.session_state.rename_target = last_index
        st.session_state[rename_input_key(last_index)] = renamed_text
    elif rename_target > index:
        renamed_text = st.session_state.pop(rename_input_key(rename_target), "")
        st.session_state.rename_target = rename_target - 1
        st.session_state[rename_input_key(st.session_state.rename_target)] = renamed_text


def parse_chat_query_param():
    chat_value = st.query_params.get("chat")
    if isinstance(chat_value, list):
        chat_value = chat_value[0] if chat_value else None
    try:
        return int(chat_value)
    except (TypeError, ValueError):
        return None


def parse_chat_id_query_param():
    chat_id = st.query_params.get("chat_id")
    if isinstance(chat_id, list):
        chat_id = chat_id[0] if chat_id else None
    if isinstance(chat_id, str) and chat_id:
        return chat_id
    return None


def parse_chat_action_query_param():
    action = st.query_params.get("chat_action")
    if isinstance(action, list):
        action = action[0] if action else None
    if action in {"edit", "delete"}:
        return action
    return None


def clear_chat_action_query_param():
    if "chat_action" in st.query_params:
        del st.query_params["chat_action"]


def find_chat_index_by_id(chats, chat_id: str):
    for idx, chat in enumerate(chats):
        if chat.get("id") == chat_id:
            return idx
    return None


def apply_chat_action_from_query():
    action = parse_chat_action_query_param()
    if action is None:
        return
    target_chat_id = parse_chat_id_query_param()
    clear_chat_action_query_param()
    if target_chat_id is None:
        return
    target_idx = find_chat_index_by_id(st.session_state.chats, target_chat_id)
    if target_idx is None:
        return
    if action == "edit":
        start_rename(target_idx, st.session_state.chats[target_idx].get("title") or "New chat")
        st.session_state[SKIP_SELECTION_QUERY_KEY] = target_chat_id
        st.rerun()
    if action == "delete":
        delete_chat_at_index(target_idx)
        save_chats(st.session_state.chats)
        st.rerun()


def apply_chat_selection_from_query():
    requested_chat_id = parse_chat_id_query_param()
    skip_chat_id = st.session_state.pop(SKIP_SELECTION_QUERY_KEY, None)
    if requested_chat_id is None:
        return
    if requested_chat_id == skip_chat_id:
        return
    resolved_index = find_chat_index_by_id(st.session_state.chats, requested_chat_id)
    if resolved_index is not None:
        if resolved_index != st.session_state.active_chat:
            clear_rename_state()
            st.session_state.pop("active_chat_data", None)
        st.session_state.active_chat = resolved_index


def sync_chat_query_param():
    current_chat = st.session_state.chats[st.session_state.active_chat]
    current_chat_id = current_chat.get("id")
    query_chat_id = st.query_params.get("chat_id")
    if isinstance(query_chat_id, list):
        query_chat_id = query_chat_id[0] if query_chat_id else None
    if query_chat_id != current_chat_id:
        st.query_params["chat_id"] = current_chat_id
    if "chat" in st.query_params:
        del st.query_params["chat"]


def visible_chat_indices():
    query = (st.session_state.get("chat_search") or "").strip().lower()
    if query:
        matches = [
            idx
            for idx in range(len(st.session_state.chats) - 1, -1, -1)
            if query in (st.session_state.chats[idx].get("title") or "").lower()
        ]
        active = st.session_state.active_chat
        if active not in matches:
            matches.append(active)
        return matches[:CHAT_SEARCH_LIMIT]

    total = len(st.session_state.chats)
    start = max(0, total - CHAT_LIST_LIMIT)
    indices = list(range(total - 1, start - 1, -1))
    active = st.session_state.active_chat
    if active not in indices:
        indices.append(active)
    return indices


@st.cache_resource(show_spinner=False)
def get_http_session():
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=8, pool_maxsize=16)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if not st.session_state.chats:
    chat = new_chat()
    save_json_atomic(chat_file_path(chat["id"]), chat)
    st.session_state.chats = [chat_summary(chat)]
if ensure_chat_ids(st.session_state.chats):
    save_chats(st.session_state.chats)
if "active_chat" not in st.session_state:
    requested_chat_id = parse_chat_id_query_param()
    requested_chat_index = parse_chat_query_param()
    if requested_chat_id is not None:
        resolved_index = find_chat_index_by_id(st.session_state.chats, requested_chat_id)
        if resolved_index is None:
            st.session_state.active_chat = len(st.session_state.chats) - 1
        else:
            st.session_state.active_chat = resolved_index
    elif requested_chat_index is None:
        st.session_state.active_chat = len(st.session_state.chats) - 1
    else:
        st.session_state.active_chat = requested_chat_index
if "rename_target" not in st.session_state:
    st.session_state.rename_target = None
if RETRY_STATE_KEY not in st.session_state:
    st.session_state[RETRY_STATE_KEY] = None
if SEND_STATE_KEY not in st.session_state:
    st.session_state[SEND_STATE_KEY] = None
if "history_length" not in st.session_state:
    st.session_state.history_length = normalize_history_length(
        st.session_state.settings.get("history_length")
    )
if "model" not in st.session_state:
    st.session_state.model = normalize_model(st.session_state.settings.get("model"))
if "query_engine_version" not in st.session_state:
    st.session_state.query_engine_version = normalize_query_engine_version(
        st.session_state.settings.get("query_engine_version")
    )
apply_chat_action_from_query()
apply_chat_selection_from_query()
if st.session_state.active_chat >= len(st.session_state.chats):
    st.session_state.active_chat = len(st.session_state.chats) - 1
if st.session_state.active_chat < 0:
    st.session_state.active_chat = 0
sync_chat_query_param()
if st.session_state.rename_target is not None:
    if (
        st.session_state.rename_target >= len(st.session_state.chats)
        or st.session_state.rename_target < 0
    ):
        clear_rename_state()


def _history_item(prev: dict) -> dict:
    """Build one request ``history`` entry from a stored chat turn.

    Args:
        prev: A prior chat turn dict.

    Returns:
        A dict holding the turn's non-empty question/response/attachments and
        agent/identity context, matching the shape the backend expects.
    """
    hist_item = {}
    if prev.get("question"):
        hist_item["question"] = prev["question"]
    if prev.get("response"):
        hist_item["response"] = prev["response"]
    if prev.get("attachments"):
        hist_item["attachments"] = prev["attachments"]
    if "agentContext" in prev and prev["agentContext"] is not None:
        hist_item["agentContext"] = prev["agentContext"]
    if "identityResolutions" in prev and prev["identityResolutions"] is not None:
        hist_item["identityResolutions"] = prev["identityResolutions"]
    return hist_item


def build_payload(question: str) -> dict:
    payload = {
        "role": "user",
        "question": question,
        "model": normalize_model(st.session_state.get("model")),
    }

    current = get_active_chat()
    history_length = normalize_history_length(
        st.session_state.get("history_length", DEFAULT_HISTORY_LENGTH)
    )
    if history_length > 0 and current["turns"]:
        history_items = [
            item for prev in current["turns"][-history_length:] if (item := _history_item(prev))
        ]
        if history_items:
            payload["history"] = history_items

    return payload


def build_request_body(turn_index: int) -> dict:
    """Reconstruct the ``/question`` request body that produced a given turn.

    Mirrors :func:`build_payload`, but anchors on a stored turn: the question and
    model come from that turn, and ``history`` is rebuilt from the turns that
    preceded it (honouring the current history-length setting).

    Args:
        turn_index: Index of the turn within the active chat's ``turns`` list.

    Returns:
        A request-body dict (``role``/``question``/``model`` and optional
        ``history``), the same shape sent to the backend.
    """
    turns = get_active_chat()["turns"]
    turn = turns[turn_index]
    payload = {
        "role": "user",
        "question": turn.get("question", ""),
        "model": turn.get("model") or normalize_model(st.session_state.get("model")),
    }

    history_length = normalize_history_length(
        st.session_state.get("history_length", DEFAULT_HISTORY_LENGTH)
    )
    if history_length > 0 and turn_index > 0:
        preceding = turns[max(0, turn_index - history_length):turn_index]
        history_items = [item for prev in preceding if (item := _history_item(prev))]
        if history_items:
            payload["history"] = history_items

    return payload


def request_answer(question: str):
    payload = build_payload(question)
    headers = {
        "X-RPC-AUTHORIZATION": f"{CVOS_USER}:{CVOS_PASS}",
        "X-RPC-DIRECTORY": CVOS_DIRECTORY,
    }
    request_started = time.perf_counter()
    resp = get_http_session().post(
        query_engine_url(), json=payload, headers=headers, timeout=(60, 600)
    )
    response_time_seconds = time.perf_counter() - request_started
    resp.raise_for_status()
    data = resp.json()
    return (
        data.get("response", ""),
        data.get("attachments") or [],
        data.get("agentContext"),
        data.get("identityResolutions"),
        data.get("n_steps"),
        response_time_seconds,
    )


def append_turn(
    question: str,
    response_text: str,
    attachments,
    agent_context=None,
    identity_resolutions=None,
    model_name=None,
    query_engine_version=None,
    history_length=None,
    response_time_seconds=None,
    n_steps=None,
):
    current_chat = get_active_chat()
    turn = {
        "question": question,
        "response": response_text,
        "attachments": attachments,
    }
    model_name = normalize_model(model_name or st.session_state.get("model"))
    turn["model"] = model_name
    turn["query_engine_version"] = normalize_query_engine_version(
        query_engine_version or st.session_state.get("query_engine_version")
    )
    turn["history_length"] = normalize_history_length(
        history_length if history_length is not None else st.session_state.get("history_length")
    )
    if response_time_seconds is not None:
        turn["response_time_seconds"] = response_time_seconds
    if agent_context is not None:
        turn["agentContext"] = agent_context
    if identity_resolutions is not None:
        turn["identityResolutions"] = identity_resolutions
    # Recorded only for "save as test case"; never sent back as history.
    if n_steps is not None:
        turn["nSteps"] = n_steps
    current_chat["turns"].append(turn)
    if current_chat.get("title") == "New chat" and len(current_chat["turns"]) == 1:
        current_chat["title"] = normalize_chat_title(question)
    save_active_chat(current_chat)
    move_chat_to_end(st.session_state.active_chat)
    save_chats(st.session_state.chats)


def clear_retry_state():
    st.session_state[RETRY_STATE_KEY] = None
    st.session_state.pop(RETRY_QUESTION_KEY, None)
    st.session_state.pop(RETRY_CHAT_ID_KEY, None)
    st.session_state.pop(RETRY_BACKUP_TURN_KEY, None)


def start_retry_last_turn():
    current_chat = get_active_chat()
    if not current_chat["turns"]:
        return False, "No previous turn to retry."
    last_turn = current_chat["turns"].pop()
    retry_question = (last_turn.get("question") or "").strip()
    if not retry_question:
        current_chat["turns"].append(last_turn)
        return False, "No previous user message to retry."
    st.session_state[RETRY_STATE_KEY] = "pending"
    st.session_state[RETRY_QUESTION_KEY] = retry_question
    st.session_state[RETRY_CHAT_ID_KEY] = current_chat.get("id")
    st.session_state[RETRY_BACKUP_TURN_KEY] = last_turn
    save_active_chat(current_chat)
    return True, ""


def clear_send_state():
    st.session_state[SEND_STATE_KEY] = None
    st.session_state.pop(SEND_QUESTION_KEY, None)
    st.session_state.pop(SEND_CHAT_ID_KEY, None)


def save_history_length_setting():
    history_length = normalize_history_length(st.session_state.get("history_length"))
    st.session_state.history_length = history_length
    settings = dict(st.session_state.get("settings") or {})
    settings["history_length"] = history_length
    st.session_state.settings = settings
    save_settings(settings)


def save_model_setting():
    model = normalize_model(st.session_state.get("model"))
    st.session_state.model = model
    settings = dict(st.session_state.get("settings") or {})
    settings["model"] = model
    st.session_state.settings = settings
    save_settings(settings)


def save_query_engine_version_setting():
    version = normalize_query_engine_version(st.session_state.get("query_engine_version"))
    st.session_state.query_engine_version = version
    settings = dict(st.session_state.get("settings") or {})
    settings["query_engine_version"] = version
    st.session_state.settings = settings
    save_settings(settings)


def start_send_message(question: str):
    raw_question = question or ""
    if not raw_question.strip():
        return False
    current_chat = get_active_chat()
    st.session_state[SEND_STATE_KEY] = "running"
    st.session_state[SEND_QUESTION_KEY] = raw_question
    st.session_state[SEND_CHAT_ID_KEY] = current_chat.get("id")
    return True


@st.cache_data(show_spinner=False, max_entries=1000)
def get_event_scene_image(event_id: str) -> bytes:
    event_id_b64 = base64.b64encode(event_id.encode("utf-8")).decode("ascii")
    url = f"{CVOS_BASE_URL}/obj/{event_id_b64}/sceneThumb"
    headers = {
        "X-RPC-AUTHORIZATION": f"{CVOS_USER}:{CVOS_PASS}",
        "Authorization": CVOS_DIRECTORY,
    }
    resp = get_http_session().get(url, headers=headers, verify=False, timeout=30)
    resp.raise_for_status()
    return resp.content


def render_attachments(attachments):
    if not attachments:
        return

    st.subheader("Attachments")
    event_face_in_scene_ids = []
    for idx, att in enumerate(attachments, start=1):
        if not isinstance(att, dict):
            st.write(f"Attachment {idx}: {att}")
            continue
        filtered = {k: v for k, v in att.items() if v is not None}
        if filtered.get("type") == "eventFaceInScene":
            if filtered.get("id"):
                event_face_in_scene_ids.append(str(filtered["id"]))
            continue
        st.write(f"Attachment {idx}:")
        st.json(filtered)

    if not event_face_in_scene_ids:
        return

    st.markdown("**Event Face In Scene Images**")
    for i in range(0, len(event_face_in_scene_ids), 2):
        row_ids = event_face_in_scene_ids[i : i + 2]
        row = st.columns(2, gap="small")
        for j, event_id in enumerate(row_ids):
            with row[j]:
                try:
                    image_bytes = get_event_scene_image(event_id)
                    st.image(
                        image_bytes,
                        caption=f"eventFaceInScene id: {event_id}",
                        width="stretch",
                    )
                except Exception:
                    st.warning(f"Could not load image for event id: {event_id}")


def render_copy_icon(text: str, key: str):
    payload = json.dumps(text or "")
    button_id = f"copy_{key}"
    components.html(
        f"""
        <style>
          html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
          }}
          .copy-slot {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.12s ease;
          }}
          .copy-slot:hover {{
            background: rgba(148, 163, 184, 0.22);
          }}
          .copy-slot.copied {{
            background: rgba(34, 197, 94, 0.2);
          }}
          .copy-slot.error {{
            background: rgba(239, 68, 68, 0.2);
          }}
          .copy-slot.copied .copy-btn {{
            color: #166534;
          }}
          .copy-slot.error .copy-btn {{
            color: #991b1b;
          }}
          .copy-btn {{
            width: 100%;
            height: 100%;
            border: none;
            background: transparent;
            color: #0f172a;
            font-size: 21px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            line-height: 1;
          }}
          .copy-btn:focus-visible {{
            outline: 2px solid rgba(30, 64, 175, 0.45);
            outline-offset: 2px;
            border-radius: 10px;
          }}
        </style>
        <div style="display:flex;justify-content:flex-end;align-items:flex-start;height:40px;">
          <div class="copy-slot" id="{button_id}_slot">
            <button id="{button_id}" class="copy-btn" title="Copy" aria-label="Copy message">⧉</button>
          </div>
        </div>
        <script>
          const btn = document.getElementById("{button_id}");
          const slot = document.getElementById("{button_id}_slot");
          const textToCopy = {payload};
          function flashState(kind) {{
            slot.classList.remove("copied", "error");
            if (!kind) return;
            slot.classList.add(kind);
            setTimeout(() => {{
              slot.classList.remove("copied", "error");
            }}, 700);
          }}
          async function copyText(value) {{
            try {{
              await navigator.clipboard.writeText(value);
              return true;
            }} catch (e) {{
              try {{
                const ta = document.createElement("textarea");
                ta.value = value;
                ta.style.position = "fixed";
                ta.style.left = "-9999px";
                document.body.appendChild(ta);
                ta.focus();
                ta.select();
                const ok = document.execCommand("copy");
                document.body.removeChild(ta);
                return ok;
              }} catch (_) {{
                return false;
              }}
            }}
          }}
          btn.addEventListener("click", async () => {{
            const ok = await copyText(textToCopy);
            flashState(ok ? "copied" : "error");
          }});
        </script>
        """,
        height=40,
        width=44,
    )


def render_user_message(text: str, key: str):
    row = st.columns([19, 1], gap="small")
    with row[0]:
        st.write(text)
    with row[1]:
        render_copy_icon(text, key)


def render_answer_model(
    model_name: str, query_engine_version=None, history_length=None, response_time_seconds=None
):
    if not model_name:
        return
    answered_by = f"Answered by {html.escape(model_name)}"
    if isinstance(response_time_seconds, (int, float)):
        answered_by += f" after {response_time_seconds:.1f} s"
    request_settings = [answered_by]
    if query_engine_version in QUERY_ENGINE_VERSION_OPTIONS:
        request_settings.append(f"Query engine: {html.escape(query_engine_version)}")
    if history_length is not None:
        request_settings.append(f"History: {normalize_history_length(history_length)}")
    st.markdown(
        f"""
        <div style="margin: 0.1rem 0 0.45rem 0;">
          <span style="
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(148, 163, 184, 0.45);
            border-radius: 999px;
            background: rgba(248, 250, 252, 0.85);
            color: #475569;
            font-size: 0.76rem;
            font-weight: 600;
            line-height: 1;
            padding: 0.28rem 0.55rem;
          ">{" &middot; ".join(request_settings)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_test_case(request_body: dict, turn: dict) -> dict:
    """Build a jsonl test-case entry pairing the full request with its response.

    Args:
        request_body: The exact ``/question`` request body that produced the
            turn (``role``/``question``/``model`` and optional ``history``),
            as returned by :func:`build_request_body`.
        turn: The chat turn holding the response and any output context
            (``response``, ``attachments``, ``agentContext``,
            ``identityResolutions``).

    Returns:
        A dict with the full ``request`` body, the ``response`` plus any present
        output fields, and a ``savedAt`` ISO-8601 UTC timestamp, ready to be
        written as one jsonl line.
    """
    entry = {
        "request": request_body,
        "response": turn.get("response", ""),
    }
    # nSteps captures how many agent steps the response took, so test cases can
    # track what's optimal. It is intentionally response-only — never sent back
    # as part of request history.
    if turn.get("nSteps") is not None:
        entry["nSteps"] = turn["nSteps"]
    if turn.get("attachments"):
        entry["attachments"] = turn["attachments"]
    if turn.get("agentContext") is not None:
        entry["agentContext"] = turn["agentContext"]
    if turn.get("identityResolutions") is not None:
        entry["identityResolutions"] = turn["identityResolutions"]
    entry["savedAt"] = datetime.now(timezone.utc).isoformat()
    return entry


def save_test_case(request_body: dict, turn: dict, difficulty: str) -> str:
    """Append a request/response pair as a test case to the difficulty file.

    Args:
        request_body: The full request body to persist (see
            :func:`build_test_case`).
        turn: The chat turn supplying the response/output context.
        difficulty: One of ``TEST_CASE_DIFFICULTIES`` ("easy"/"medium"/"hard");
            selects the target file ``test_cases_<difficulty>.jsonl``.

    Returns:
        The absolute path of the jsonl file that was appended to.

    Raises:
        ValueError: If ``difficulty`` is not a recognised difficulty level.
    """
    if difficulty not in TEST_CASE_DIFFICULTIES:
        raise ValueError(f"Unknown test-case difficulty: {difficulty!r}")
    os.makedirs(TEST_CASES_DIR, exist_ok=True)
    path = os.path.join(TEST_CASES_DIR, f"test_cases_{difficulty}.jsonl")
    entry = build_test_case(request_body, turn)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


@st.dialog("Save as test case")
def save_test_case_dialog(request_body: dict, turn: dict):
    """Modal asking which difficulty to file the test case under, then saving.

    Args:
        request_body: The full request body to persist when a difficulty is
            chosen.
        turn: The chat turn supplying the response/output context.
    """
    st.write("How hard is this question? It will be saved to the matching file.")
    question_preview = (request_body.get("question") or "").strip()
    if question_preview:
        st.caption(f"“{question_preview[:140]}{'…' if len(question_preview) > 140 else ''}”")
    cols = st.columns(len(TEST_CASE_DIFFICULTIES), gap="small")
    for col, difficulty in zip(cols, TEST_CASE_DIFFICULTIES):
        if col.button(
            difficulty.capitalize(),
            key=f"save_test_case_{difficulty}",
            width="stretch",
            type="primary",
        ):
            try:
                path = save_test_case(request_body, turn, difficulty)
            except Exception as exc:
                st.error(f"Could not save test case: {exc}")
            else:
                st.session_state["test_case_save_msg"] = (
                    f"Saved {difficulty} test case to {os.path.basename(path)}"
                )
                st.rerun()


# Sidebar: chat list + actions
with st.sidebar:
    st.header("Chats")
    st.subheader("Request settings")
    st.selectbox(
        "Model",
        MODEL_OPTIONS,
        key="model",
        help="Which model label to send to the /question backend.",
        on_change=save_model_setting,
    )
    st.caption(f"Current model: {st.session_state.model}")
    st.selectbox(
        "Query engine version",
        QUERY_ENGINE_VERSION_OPTIONS,
        key="query_engine_version",
        help="Old calls /question; new calls /question/v2 on the same backend.",
        on_change=save_query_engine_version_setting,
    )
    st.caption(f"Current query engine version: {st.session_state.query_engine_version}")
    st.caption(f"Request destination: {query_engine_url()}")
    st.number_input(
        "History length",
        min_value=0,
        step=1,
        key="history_length",
        help="Maximum number of prior question/answer pairs to send in the request history.",
        on_change=save_history_length_setting,
    )
    st.caption(f"Current history length: {st.session_state.history_length}")
    st.divider()

    if st.button("Start new chat", key="start_new_chat", width="stretch"):
        chat = new_chat()
        save_json_atomic(chat_file_path(chat["id"]), chat)
        st.session_state.chats.append(chat_summary(chat))
        st.session_state.active_chat = len(st.session_state.chats) - 1
        st.session_state.active_chat_data = chat
        clear_rename_state()
        save_chats(st.session_state.chats)
        sync_chat_query_param()
        st.rerun()

    st.text_input(
        "Search chats",
        key="chat_search",
        placeholder="Search chats",
        label_visibility="collapsed",
    )

    with st.container(key="chat_list"):
        visible_indices = visible_chat_indices()
        hidden_count = len(st.session_state.chats) - len(set(visible_indices))
        if hidden_count > 0:
            st.caption(
                f"Showing {len(set(visible_indices))} of {len(st.session_state.chats)} chats."
            )
        for idx in visible_indices:
            chat = st.session_state.chats[idx]
            with st.container(key=f"chat_row_{idx}"):
                title = chat.get("title") or "New chat"

                if st.session_state.rename_target == idx:
                    row = st.columns([8.2, 0.9, 0.9], gap="small")
                    input_key = rename_input_key(idx)
                    row[0].text_input(
                        "Rename chat",
                        key=input_key,
                        label_visibility="collapsed",
                        placeholder="Rename chat",
                        on_change=commit_rename,
                        args=(idx,),
                    )
                    if row[1].button(
                        "✓",
                        key=f"save_rename_{idx}",
                        help="Save name",
                        width="stretch",
                        type="tertiary",
                    ):
                        commit_rename(idx)
                        st.rerun()
                    if row[2].button(
                        "✕",
                        key=f"cancel_rename_{idx}",
                        help="Cancel rename",
                        width="stretch",
                        type="tertiary",
                    ):
                        clear_rename_state()
                        st.rerun()
                    continue
                row = st.columns([8.2, 0.9, 0.9], gap="small")
                is_active = idx == st.session_state.active_chat
                if row[0].button(
                    title,
                    key=f"open_chat_{idx}",
                    help=title,
                    width="stretch",
                    type="primary" if is_active else "secondary",
                ):
                    if idx != st.session_state.active_chat:
                        clear_rename_state()
                        st.session_state.pop("active_chat_data", None)
                        st.session_state.active_chat = idx
                        sync_chat_query_param()
                        st.rerun()
                if row[1].button(
                    "✎",
                    key=f"edit_chat_{idx}",
                    help="Rename chat",
                    width="stretch",
                    type="tertiary",
                ):
                    start_rename(idx, title)
                    st.rerun()
                if row[2].button(
                    "🗑",
                    key=f"delete_chat_{idx}",
                    help="Delete chat",
                    width="stretch",
                    type="tertiary",
                ):
                    delete_chat_at_index(idx)
                    save_chats(st.session_state.chats)
                    st.rerun()


current_chat = get_active_chat()
retry_state = st.session_state.get(RETRY_STATE_KEY)
retry_locked = retry_state in {"pending", "running"}
pending_retry_question = (st.session_state.get(RETRY_QUESTION_KEY) or "").strip()
send_state = st.session_state.get(SEND_STATE_KEY)
pending_send_chat_id = st.session_state.get(SEND_CHAT_ID_KEY)
send_locked = send_state == "running" and pending_send_chat_id == current_chat.get("id")
pending_send_question = st.session_state.get(SEND_QUESTION_KEY) or ""

if send_state == "running" and pending_send_chat_id and pending_send_chat_id != current_chat.get("id"):
    clear_send_state()
    send_locked = False
    pending_send_question = ""

if send_locked:
    st.markdown(
        """
        <style>
        [data-testid="stChatInput"] button {
            pointer-events: none !important;
            background: #d1d5db !important;
            color: #9ca3af !important;
            border-color: #d1d5db !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

test_case_save_msg = st.session_state.pop("test_case_save_msg", None)
if test_case_save_msg:
    st.toast(test_case_save_msg, icon="✅")

# Render chat history
for turn_idx, turn in enumerate(current_chat["turns"]):
    with st.chat_message("user"):
        render_user_message(
            turn.get("question", ""),
            key=f"user_hist_{current_chat.get('id', st.session_state.active_chat)}_{turn_idx}",
        )
    with st.chat_message("assistant"):
        render_answer_model(
            turn.get("model"),
            turn.get("query_engine_version"),
            turn.get("history_length"),
            turn.get("response_time_seconds"),
        )
        st.write(turn.get("response", ""))
        render_attachments(turn.get("attachments"))
        # The last turn's "save" lives in the combined action row below, next to
        # delete/retry; earlier turns get their own inline save pill here.
        is_last_turn = turn_idx == len(current_chat["turns"]) - 1
        if turn.get("response") and not is_last_turn:
            if st.button(
                "Save as test case",
                key=f"save_test_case_btn_{current_chat.get('id', st.session_state.active_chat)}_{turn_idx}",
                help="Save this question and answer as a test case",
            ):
                save_test_case_dialog(build_request_body(turn_idx), turn)

if retry_locked and pending_retry_question:
    with st.chat_message("user"):
        render_user_message(
            pending_retry_question,
            key=f"user_retry_pending_{current_chat.get('id', st.session_state.active_chat)}",
        )
if send_locked and pending_send_question:
    with st.chat_message("user"):
        render_user_message(
            pending_send_question,
            key=f"user_send_pending_{current_chat.get('id', st.session_state.active_chat)}",
        )

action_row_slot = st.empty()
if not retry_locked:
    has_turns = bool(current_chat["turns"])
    last_turn = current_chat["turns"][-1] if has_turns else None
    can_save_last = bool(last_turn and last_turn.get("response"))
    with action_row_slot.container():
        with st.container(key=f"turn_actions_{st.session_state.active_chat}"):
            undo_cols = st.columns(3, gap="small")
            if undo_cols[0].button(
                "Save as test case",
                key=f"save_test_case_btn_action_{st.session_state.active_chat}",
                help="Save this question and answer as a test case",
                disabled=send_locked or not can_save_last,
            ):
                save_test_case_dialog(build_request_body(len(current_chat["turns"]) - 1), last_turn)
            if undo_cols[1].button(
                "Delete previous turn",
                key=f"undo_turn_{st.session_state.active_chat}",
                disabled=send_locked or not has_turns,
            ):
                current_chat["turns"].pop()
                save_active_chat(current_chat)
                st.rerun()
            if undo_cols[2].button(
                "Retry last message",
                key=f"retry_last_{st.session_state.active_chat}",
                disabled=send_locked or not has_turns,
            ):
                started, warning_message = start_retry_last_turn()
                if started:
                    action_row_slot.empty()
                    st.rerun()
                st.warning(warning_message)

if st.session_state.get(RETRY_STATE_KEY) == "pending":
    st.session_state[RETRY_STATE_KEY] = "running"
    st.rerun()

if st.session_state.get(RETRY_STATE_KEY) == "running":
    pending_chat_id = st.session_state.get(RETRY_CHAT_ID_KEY)
    if pending_chat_id and pending_chat_id != current_chat.get("id"):
        clear_retry_state()
    else:
        retry_question = (st.session_state.get(RETRY_QUESTION_KEY) or "").strip()
        with st.spinner("Retrying last message..."):
            with st.container(key=f"turn_actions_{st.session_state.active_chat}"):
                locked_cols = st.columns(3, gap="small")
                locked_cols[0].button(
                    "Save as test case",
                    key=f"save_test_case_btn_action_{st.session_state.active_chat}",
                    disabled=True,
                )
                locked_cols[1].button(
                    "Delete previous turn",
                    key=f"undo_turn_{st.session_state.active_chat}",
                    disabled=True,
                )
                locked_cols[2].button(
                    "Retry last message",
                    key=f"retry_last_{st.session_state.active_chat}",
                    disabled=True,
                )
            try:
                response_text, attachments, agent_context, identity_resolutions, n_steps, response_time_seconds = request_answer(retry_question)
            except Exception as exc:
                backup_turn = st.session_state.get(RETRY_BACKUP_TURN_KEY)
                if backup_turn is not None:
                    current_chat["turns"].append(backup_turn)
                    save_active_chat(current_chat)
                clear_retry_state()
                st.error(f"Retry failed: {exc}")
            else:
                append_turn(
                    retry_question,
                    response_text,
                    attachments,
                    agent_context,
                    identity_resolutions,
                    normalize_model(st.session_state.get("model")),
                    response_time_seconds=response_time_seconds,
                    n_steps=n_steps,
                )
                clear_retry_state()
                st.rerun()

user_input = st.chat_input("Type your message", disabled=retry_locked)

if user_input:
    if send_locked:
        st.warning("Please wait for the current answer before sending another message.")
    else:
        if start_send_message(user_input):
            with st.chat_message("user"):
                render_user_message(
                    user_input,
                    key=f"user_send_pending_{current_chat.get('id', st.session_state.active_chat)}",
                )

if st.session_state.get(SEND_STATE_KEY) == "running":
    pending_chat_id = st.session_state.get(SEND_CHAT_ID_KEY)
    if pending_chat_id and pending_chat_id != current_chat.get("id"):
        clear_send_state()
    else:
        send_question = st.session_state.get(SEND_QUESTION_KEY) or ""
        with st.spinner("Waiting for answer..."):
            try:
                response_text, attachments, agent_context, identity_resolutions, n_steps, response_time_seconds = request_answer(send_question)
            except Exception as exc:
                clear_send_state()
                with st.chat_message("assistant"):
                    st.error(f"Request failed: {exc}")
                st.stop()
            else:
                append_turn(
                    send_question,
                    response_text,
                    attachments,
                    agent_context,
                    identity_resolutions,
                    normalize_model(st.session_state.get("model")),
                    response_time_seconds=response_time_seconds,
                    n_steps=n_steps,
                )
                clear_send_state()
                st.rerun()
