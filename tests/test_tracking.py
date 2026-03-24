import json
from pathlib import Path

from tracking import load_tracking_log, record_answer, summarize_performance


def test_record_answer_writes_json_log(tmp_path):
    log_path = tmp_path / "tracking.json"

    entry = record_answer(
        user_id="user-1",
        session_id="session-a",
        question_id="q-101",
        topic="Fractions - Operations",
        is_correct=False,
        path=log_path,
    )

    assert entry["result"] == "incorrect"
    saved = load_tracking_log(log_path)
    assert len(saved) == 1
    assert saved[0]["user_id"] == "user-1"
    assert saved[0]["topic"] == "Fractions - Operations"


def test_summarize_performance_for_user_and_session(tmp_path):
    log_path = tmp_path / "tracking.json"

    record_answer(
        user_id="user-1",
        session_id="session-a",
        question_id="q-1",
        topic="Fractions - Operations",
        is_correct=False,
        path=log_path,
    )
    record_answer(
        user_id="user-1",
        session_id="session-a",
        question_id="q-2",
        topic="Fractions - Operations",
        is_correct=True,
        path=log_path,
    )
    record_answer(
        user_id="user-1",
        session_id="session-a",
        question_id="q-3",
        topic="Geometry - Measurement and Shapes",
        is_correct=False,
        path=log_path,
    )
    record_answer(
        user_id="user-2",
        session_id="session-b",
        question_id="q-4",
        topic="Data and Statistics",
        is_correct=True,
        path=log_path,
    )

    summary = summarize_performance(log_path, user_id="user-1", session_id="session-a")

    assert summary["questions_answered"] == 3
    assert summary["correct_answers"] == 1
    assert summary["incorrect_answers"] == 2
    assert summary["accuracy"] == 0.33
    assert [topic["topic"] for topic in summary["weak_topics"]] == [
        "Fractions - Operations",
        "Geometry - Measurement and Shapes",
    ]
    assert summary["weak_topics"][0]["incorrect"] == 1
