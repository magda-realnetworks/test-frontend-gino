import base64
import json
import os
import uuid

import requests
import streamlit as st
import streamlit.components.v1 as components
import urllib3

API_URL = "http://localhost:5002/question"
CHAT_STORE = "chats.json"
SETTINGS_STORE = "app_settings.json"
DEFAULT_HISTORY_LENGTH = 3
DEFAULT_MODEL = "OpenAI GPT4.1"
MODEL_OPTIONS = [
    "OpenAI GPT4.1",
    "OpenAI GPT5.4",
    "OpenAI GPT5.4 Mini",
    "OpenAI GPT5.4 Nano",
    "AWS DeepSeek-R1",
    "Groq GPT OSS 120B",
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
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button {
        background: #e8d8c3 !important;
        color: #4a3525 !important;
        border: 1px solid #c7ad91 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button p,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button p {
        white-space: nowrap !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button p,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button p {
        white-space: nowrap !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button {
        background: #d9f5e1 !important;
        color: #234a31 !important;
        border: 1px solid #9fd5af !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button:hover,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button:hover {
        background: #c8edd2 !important;
        color: #1f422b !important;
        border-color: #8bc89e !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-retry_last_"] button:disabled,
    [data-testid="stMain"] div[class*="st-key-retry_last_"] button:disabled {
        background: #eef8f1 !important;
        color: #7b9483 !important;
        border-color: #d9e9df !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button:hover,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button:hover {
        background: #dcc6ab !important;
        color: #3f2d20 !important;
        border-color: #b79778 !important;
    }
    [data-testid="stAppViewContainer"] div[class*="st-key-undo_turn_"] button:disabled,
    [data-testid="stMain"] div[class*="st-key-undo_turn_"] button:disabled {
        background: #f3e9dc !important;
        color: #8a735d !important;
        border-color: #ead8c4 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_chats():
    if not os.path.exists(CHAT_STORE):
        return []
    try:
        with open(CHAT_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_chats(chats):
    with open(CHAT_STORE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)


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
    with open(SETTINGS_STORE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def normalize_history_length(value) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return DEFAULT_HISTORY_LENGTH


def normalize_model(value) -> str:
    if isinstance(value, str) and value in MODEL_OPTIONS:
        return value
    return DEFAULT_MODEL


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
    return {"id": generate_chat_id(), "title": "New chat", "turns": []}


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
    st.session_state.chats[index]["title"] = normalize_chat_title(
        st.session_state.get(input_key, "")
    )
    save_chats(st.session_state.chats)
    clear_rename_state()


def delete_chat_at_index(index: int):
    rename_target = st.session_state.rename_target
    st.session_state.chats.pop(index)
    if not st.session_state.chats:
        st.session_state.chats = [new_chat()]
        st.session_state.active_chat = 0
    elif index < st.session_state.active_chat:
        st.session_state.active_chat -= 1
    elif index == st.session_state.active_chat:
        st.session_state.active_chat = min(index, len(st.session_state.chats) - 1)
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


if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if not st.session_state.chats:
    st.session_state.chats = [new_chat()]
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


def build_payload(question: str) -> dict:
    payload = {
        "role": "user",
        "question": question,
        "model": normalize_model(st.session_state.get("model")),
    }

    current = st.session_state.chats[st.session_state.active_chat]
    history_length = normalize_history_length(
        st.session_state.get("history_length", DEFAULT_HISTORY_LENGTH)
    )
    if history_length > 0 and current["turns"]:
        history_items = []
        for prev in current["turns"][-history_length:]:
            hist_item = {}
            if prev.get("question"):
                hist_item["question"] = prev["question"]
            if prev.get("response"):
                hist_item["response"] = prev["response"]
            if prev.get("attachments"):
                hist_item["attachments"] = prev["attachments"]
            if "agentContext" in prev and prev["agentContext"] is not None:
                hist_item["agentContext"] = prev["agentContext"]
            if hist_item:
                history_items.append(hist_item)
        if history_items:
            payload["history"] = history_items

    return payload


def request_answer(question: str):
    payload = build_payload(question)
    headers = {
        "X-RPC-AUTHORIZATION": f"{CVOS_USER}:{CVOS_PASS}",
        "X-RPC-DIRECTORY": CVOS_DIRECTORY,
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=(60, 600))
    resp.raise_for_status()
    data = resp.json()
    return (
        data.get("response", ""),
        data.get("attachments") or [],
        data.get("agentContext"),
    )


def append_turn(question: str, response_text: str, attachments, agent_context=None):
    current_chat = st.session_state.chats[st.session_state.active_chat]
    turn = {
        "question": question,
        "response": response_text,
        "attachments": attachments,
    }
    if agent_context is not None:
        turn["agentContext"] = agent_context
    current_chat["turns"].append(turn)
    if current_chat.get("title") == "New chat" and len(current_chat["turns"]) == 1:
        current_chat["title"] = normalize_chat_title(question)
    move_chat_to_end(st.session_state.active_chat)


def clear_retry_state():
    st.session_state[RETRY_STATE_KEY] = None
    st.session_state.pop(RETRY_QUESTION_KEY, None)
    st.session_state.pop(RETRY_CHAT_ID_KEY, None)
    st.session_state.pop(RETRY_BACKUP_TURN_KEY, None)


def start_retry_last_turn():
    current_chat = st.session_state.chats[st.session_state.active_chat]
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
    save_chats(st.session_state.chats)
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


def start_send_message(question: str):
    raw_question = question or ""
    if not raw_question.strip():
        return False
    current_chat = st.session_state.chats[st.session_state.active_chat]
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
    resp = requests.get(url, headers=headers, verify=False, timeout=30)
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
                        use_container_width=True,
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

    if st.button("Start new chat", key="start_new_chat", use_container_width=True):
        st.session_state.chats.append(new_chat())
        st.session_state.active_chat = len(st.session_state.chats) - 1
        clear_rename_state()
        save_chats(st.session_state.chats)
        sync_chat_query_param()
        st.rerun()

    with st.container(key="chat_list"):
        for idx in range(len(st.session_state.chats) - 1, -1, -1):
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
                        use_container_width=True,
                        type="tertiary",
                    ):
                        commit_rename(idx)
                        st.rerun()
                    if row[2].button(
                        "✕",
                        key=f"cancel_rename_{idx}",
                        help="Cancel rename",
                        use_container_width=True,
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
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    if idx != st.session_state.active_chat:
                        clear_rename_state()
                        st.session_state.active_chat = idx
                        sync_chat_query_param()
                        st.rerun()
                if row[1].button(
                    "✎",
                    key=f"edit_chat_{idx}",
                    help="Rename chat",
                    use_container_width=True,
                    type="tertiary",
                ):
                    start_rename(idx, title)
                    st.rerun()
                if row[2].button(
                    "🗑",
                    key=f"delete_chat_{idx}",
                    help="Delete chat",
                    use_container_width=True,
                    type="tertiary",
                ):
                    delete_chat_at_index(idx)
                    save_chats(st.session_state.chats)
                    st.rerun()


current_chat = st.session_state.chats[st.session_state.active_chat]
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

# Render chat history
for turn_idx, turn in enumerate(current_chat["turns"]):
    with st.chat_message("user"):
        render_user_message(
            turn.get("question", ""),
            key=f"user_hist_{current_chat.get('id', st.session_state.active_chat)}_{turn_idx}",
        )
    with st.chat_message("assistant"):
        st.write(turn.get("response", ""))
        render_attachments(turn.get("attachments"))

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
    with action_row_slot.container():
        undo_cols = st.columns([4, 3, 3], gap="small")
        if undo_cols[1].button(
            "Delete previous turn ❌",
            key=f"undo_turn_{st.session_state.active_chat}",
            use_container_width=True,
            disabled=send_locked or not current_chat["turns"],
        ):
            current_chat["turns"].pop()
            save_chats(st.session_state.chats)
            st.rerun()
        if undo_cols[2].button(
            "Retry last message 🔁",
            key=f"retry_last_{st.session_state.active_chat}",
            use_container_width=True,
            disabled=send_locked or not current_chat["turns"],
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
            locked_cols = st.columns([4, 3, 3], gap="small")
            locked_cols[1].button(
                "Delete previous turn ❌",
                key=f"undo_turn_{st.session_state.active_chat}",
                use_container_width=True,
                disabled=True,
            )
            locked_cols[2].button(
                "Retry last message 🔁",
                key=f"retry_last_{st.session_state.active_chat}",
                use_container_width=True,
                disabled=True,
            )
            try:
                response_text, attachments, agent_context = request_answer(retry_question)
            except Exception as exc:
                backup_turn = st.session_state.get(RETRY_BACKUP_TURN_KEY)
                if backup_turn is not None:
                    current_chat["turns"].append(backup_turn)
                    save_chats(st.session_state.chats)
                clear_retry_state()
                st.error(f"Retry failed: {exc}")
            else:
                append_turn(retry_question, response_text, attachments, agent_context)
                save_chats(st.session_state.chats)
                clear_retry_state()
                st.rerun()

user_input = st.chat_input("Type your message", disabled=retry_locked)

if user_input:
    if send_locked:
        st.warning("Please wait for the current answer before sending another message.")
    else:
        start_send_message(user_input)

if st.session_state.get(SEND_STATE_KEY) == "running":
    pending_chat_id = st.session_state.get(SEND_CHAT_ID_KEY)
    if pending_chat_id and pending_chat_id != current_chat.get("id"):
        clear_send_state()
    else:
        send_question = st.session_state.get(SEND_QUESTION_KEY) or ""
        with st.spinner("Waiting for answer..."):
            try:
                response_text, attachments, agent_context = request_answer(send_question)
            except Exception as exc:
                clear_send_state()
                with st.chat_message("assistant"):
                    st.error(f"Request failed: {exc}")
                st.stop()
            else:
                append_turn(send_question, response_text, attachments, agent_context)
                save_chats(st.session_state.chats)
                clear_send_state()
                st.rerun()
