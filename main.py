"""Reusable processing pipeline for the AI Video Assistant."""

from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import generate_title, summarize
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain

load_dotenv()

ProgressCallback = Callable[[str, str], None]


def _report(callback: ProgressCallback | None, step: str, state: str) -> None:
    """Notify an optional UI/CLI observer without coupling the pipeline to Streamlit."""
    if callback:
        callback(step, state)


def run_pipeline(
    source: str,
    language: str = "english",
    on_progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Analyse a video source and return the meeting artefacts plus its RAG chain."""
    if not source.strip():
        raise ValueError("Provide a YouTube URL or a local audio/video file path.")

    _report(on_progress, "audio", "active")
    chunks = process_input(source)
    _report(on_progress, "audio", "done")

    _report(on_progress, "transcript", "active")
    transcript = transcribe_all(chunks, language)
    _report(on_progress, "transcript", "done")

    _report(on_progress, "title", "active")
    title = generate_title(transcript)
    _report(on_progress, "title", "done")

    _report(on_progress, "summary", "active")
    summary = summarize(transcript)
    _report(on_progress, "summary", "done")

    _report(on_progress, "extract", "active")
    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    _report(on_progress, "extract", "done")

    _report(on_progress, "rag", "active")
    rag_chain = build_rag_chain(transcript)
    _report(on_progress, "rag", "done")

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":
    source = input("Enter a YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"

    def print_progress(step: str, state: str) -> None:
        if state == "active":
            print(f"Processing {step}...")

    result = run_pipeline(source, language, print_progress)
    print(f"\nTitle: {result['title']}\n\nSummary:\n{result['summary']}")
    print(f"\nAction items:\n{result['action_items']}")
    print(f"\nKey decisions:\n{result['key_decisions']}")
    print(f"\nOpen questions:\n{result['open_questions']}")

    print("\nChat with your meeting (type 'exit' to quit).")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            break
        if question:
            print(f"\nAssistant: {ask_question(result['rag_chain'], question)}\n")
