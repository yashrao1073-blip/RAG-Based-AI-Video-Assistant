"""Streamlit interface for the AI Video Assistant."""

from datetime import datetime
from pathlib import Path

import streamlit as st

from main import run_pipeline
from core.rag_engine import ask_question

st.set_page_config(page_title="AI Video Assistant", page_icon="🎬", layout="wide")

STEPS = [
    ("audio", "Prepare audio"),
    ("transcript", "Create transcript"),
    ("title", "Generate title"),
    ("summary", "Write summary"),
    ("extract", "Extract insights"),
    ("rag", "Prepare meeting chat"),
]

st.markdown(
    """
    <style>
    :root { --ink: #18212f; --muted: #64748b; --brand: #4f46e5; --soft: #eef2ff; }
    .stApp { background: #f8fafc; color: var(--ink); }
    [data-testid="stSidebar"] { background: #111827; }
    [data-testid="stSidebar"] * { color: #f8fafc; }
    .app-kicker { color: #6366f1; font-weight: 700; letter-spacing: .12em; font-size: .75rem; text-transform: uppercase; }
    .app-title { font-size: clamp(2rem, 4vw, 3.4rem); font-weight: 750; letter-spacing: -.04em; margin: .2rem 0; }
    .app-lede { color: var(--muted); font-size: 1.05rem; max-width: 44rem; }
    .source-card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.25rem; box-shadow: 0 8px 25px rgba(15, 23, 42, .05); }
    .metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; min-height: 104px; }
    .step { padding: .65rem .25rem; border-bottom: 1px solid rgba(255,255,255,.12); font-size: .9rem; }
    .step:last-child { border-bottom: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

for key, default in {
    "result": None,
    "messages": [],
    "pipeline_steps": {},
    "source_label": None,
}.items():
    st.session_state.setdefault(key, default)


def save_upload(uploaded_file) -> str:
    """Persist an uploaded video locally because the audio pipeline accepts a file path."""
    upload_dir = Path("downloades") / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(uploaded_file.name).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = upload_dir / f"{timestamp}_{safe_name}"
    destination.write_bytes(uploaded_file.getbuffer())
    return str(destination)


def render_value(value) -> None:
    """Display model output without injecting it into raw HTML."""
    if isinstance(value, (list, tuple)):
        for item in value:
            st.markdown(f"- {item}")
    else:
        st.markdown(str(value) or "_No items identified._")


def reset_analysis() -> None:
    st.session_state.result = None
    st.session_state.messages = []
    st.session_state.pipeline_steps = {}


with st.sidebar:
    st.markdown("### 🎬 AI Video Assistant")
    st.caption("Meeting intelligence, without the busywork.")
    st.divider()
    st.markdown("**Pipeline status**")
    for step_key, label in STEPS:
        state = st.session_state.pipeline_steps.get(step_key, "waiting")
        marker = {"waiting": "○", "active": "◌", "done": "●"}[state]
        st.markdown(f'<div class="step">{marker}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)
    if st.session_state.result and st.button("Start a new analysis", use_container_width=True, type="primary"):
        reset_analysis()
        st.rerun()

st.markdown('<div class="app-kicker">Meeting intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">Turn video into clear next steps.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-lede">Upload a recording or paste a YouTube link. Get a searchable transcript, concise summary, decisions, and action items.</div>',
    unsafe_allow_html=True,
)
st.write("")

with st.container(border=True):
    source_mode = st.radio("Source type", ["YouTube link", "Upload a file"], horizontal=True)
    with st.form("analysis_form", clear_on_submit=False):
        if source_mode == "YouTube link":
            url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
            uploaded_file = None
        else:
            uploaded_file = st.file_uploader("Video or audio file", type=["mp4", "mov", "mkv", "mp3", "wav", "m4a"])
            url = ""
        language = st.selectbox("Spoken language", ["english", "hinglish"], format_func=str.title)
        analyse = st.form_submit_button("Analyse recording", type="primary", use_container_width=True)

if analyse:
    if source_mode == "YouTube link" and not url.strip():
        st.error("Paste a YouTube URL to continue.")
    elif source_mode == "Upload a file" and uploaded_file is None:
        st.error("Upload an audio or video file to continue.")
    else:
        reset_analysis()
        source = url.strip() if source_mode == "YouTube link" else save_upload(uploaded_file)
        st.session_state.source_label = url.strip() if source_mode == "YouTube link" else uploaded_file.name
        progress = st.progress(0, text="Preparing your analysis…")
        status = st.empty()

        def report_progress(step: str, state: str) -> None:
            st.session_state.pipeline_steps[step] = state
            position = next(index for index, item in enumerate(STEPS) if item[0] == step)
            percent = int(((position + (1 if state == "done" else 0.35)) / len(STEPS)) * 100)
            progress.progress(percent, text=f"{dict(STEPS)[step]}…")
            status.caption(f"{dict(STEPS)[step]} is in progress.")

        try:
            st.session_state.result = run_pipeline(source, language, report_progress)
            progress.progress(100, text="Analysis complete")
            status.success("Your meeting is ready to explore.")
        except Exception as exc:
            status.empty()
            st.error(f"Analysis could not be completed: {exc}")

if not st.session_state.result:
    st.info("Start by adding a YouTube link or uploading a recording. Your results will appear here.")
else:
    result = st.session_state.result
    st.divider()
    st.caption(f"ANALYSED SOURCE · {st.session_state.source_label}")
    st.header(str(result["title"]))

    overview_tab, insights_tab, transcript_tab, chat_tab = st.tabs(
        ["Overview", "Tasks & decisions", "Transcript", "Ask the meeting"]
    )

    with overview_tab:
        st.subheader("Executive summary")
        render_value(result["summary"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Action items", len(result["action_items"]) if isinstance(result["action_items"], list) else "Ready")
        m2.metric("Key decisions", len(result["key_decisions"]) if isinstance(result["key_decisions"], list) else "Ready")
        m3.metric("Open questions", len(result["open_questions"]) if isinstance(result["open_questions"], list) else "Ready")

    with insights_tab:
        left, right = st.columns(2)
        with left:
            st.subheader("Action items")
            render_value(result["action_items"])
            st.subheader("Open questions")
            render_value(result["open_questions"])
        with right:
            st.subheader("Key decisions")
            render_value(result["key_decisions"])

    with transcript_tab:
        st.subheader("Full transcript")
        st.download_button("Download transcript", result["transcript"], file_name="meeting-transcript.txt", mime="text/plain")
        st.text_area("Transcript", result["transcript"], height=420, disabled=True, label_visibility="collapsed")

    with chat_tab:
        st.caption("Ask focused questions about this recording. Answers are grounded in its transcript.")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        question = st.chat_input("Ask about decisions, owners, dates, or any discussion point…")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Searching the meeting…"):
                    answer = ask_question(result["rag_chain"], question)
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        if st.session_state.messages and st.button("Clear conversation"):
            st.session_state.messages = []
            st.rerun()
