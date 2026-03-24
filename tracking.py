#!/usr/bin/env python3
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_LOG_PATH = Path("tracking_log.json")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_tracking_log(path: Path | str = DEFAULT_LOG_PATH) -> List[Dict[str, Any]]:
    log_path = Path(path)
    if not log_path.exists():
        return []
    with log_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Tracking log must contain a JSON array of events.")
    return data



def save_tracking_log(entries: Iterable[Dict[str, Any]], path: Path | str = DEFAULT_LOG_PATH) -> None:
    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(list(entries), handle, ensure_ascii=False, indent=2)
        handle.write("\n")



def record_answer(
    *,
    user_id: str,
    session_id: str,
    question_id: str,
    topic: str,
    is_correct: bool,
    path: Path | str = DEFAULT_LOG_PATH,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    entries = load_tracking_log(path)
    normalized_topic = (topic or "General").strip() or "General"
    entry: Dict[str, Any] = {
        "timestamp": utc_timestamp(),
        "user_id": user_id,
        "session_id": session_id,
        "question_id": question_id,
        "topic": normalized_topic,
        "result": "correct" if is_correct else "incorrect",
        "is_correct": bool(is_correct),
    }
    if metadata:
        entry["metadata"] = metadata
    entries.append(entry)
    save_tracking_log(entries, path)
    return entry



def _filter_entries(
    entries: Iterable[Dict[str, Any]],
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    filtered = []
    for entry in entries:
        if user_id is not None and entry.get("user_id") != user_id:
            continue
        if session_id is not None and entry.get("session_id") != session_id:
            continue
        filtered.append(entry)
    return filtered



def summarize_performance(
    path: Path | str = DEFAULT_LOG_PATH,
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    entries = _filter_entries(load_tracking_log(path), user_id=user_id, session_id=session_id)
    total_questions = len(entries)
    correct_answers = sum(1 for entry in entries if entry.get("is_correct"))
    incorrect_answers = total_questions - correct_answers

    topic_totals: Counter[str] = Counter()
    topic_incorrect: Counter[str] = Counter()
    for entry in entries:
        topic = str(entry.get("topic") or "General").strip() or "General"
        topic_totals[topic] += 1
        if not entry.get("is_correct"):
            topic_incorrect[topic] += 1

    weak_topics = [
        {
            "topic": topic,
            "incorrect": topic_incorrect[topic],
            "attempted": topic_totals[topic],
            "accuracy": round((topic_totals[topic] - topic_incorrect[topic]) / topic_totals[topic], 2),
        }
        for topic in topic_totals
        if topic_incorrect[topic] > 0
    ]
    weak_topics.sort(key=lambda item: (-item["incorrect"], -item["attempted"], item["accuracy"], item["topic"]))

    return {
        "user_id": user_id,
        "session_id": session_id,
        "questions_answered": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "accuracy": round(correct_answers / total_questions, 2) if total_questions else 0.0,
        "weak_topics": weak_topics,
    }
