import pytest

from exam_session import ExamSessionError, ExamSessionStore


QUESTIONS = [
    {
        "id": "q1",
        "question": "2 + 2 = ?",
        "choices": ["3", "4", "5"],
        "answer_index": 1,
        "explanation": "2 + 2 equals 4.",
    },
    {
        "id": "q2",
        "question": "Capital of France?",
        "choices": ["Paris", "Rome", "Berlin"],
        "answer_index": 0,
        "explanation": "Paris is the capital of France.",
    },
    {
        "id": "q3",
        "question": "Water freezes at?",
        "choices": ["0°C", "50°C", "100°C"],
        "answer_index": 0,
        "explanation": "Water freezes at 0°C.",
    },
]


def test_start_exam_randomizes_questions_and_hides_answers_until_submission():
    store = ExamSessionStore()

    session = store.create_session(QUESTIONS, exam_size=2, seed=7)

    assert session["status"] == "in_progress"
    assert session["total_questions"] == 2
    assert session["answered_questions"] == 0
    assert session["score"] is None
    assert all("correct_answer_index" not in question for question in session["questions"])
    assert [question["id"] for question in session["questions"]] == ["q2", "q1"]


def test_navigation_and_answering_updates_session_state():
    store = ExamSessionStore()
    session = store.create_session(QUESTIONS, exam_size=3, seed=1)
    session_id = session["session_id"]

    answered = store.answer_question(session_id, 0, 2)
    assert answered["answered_questions"] == 1
    assert answered["questions"][0]["selected_answer_index"] == 2

    moved_next = store.go_next(session_id)
    assert moved_next["current_index"] == 1

    moved_previous = store.go_previous(session_id)
    assert moved_previous["current_index"] == 0


def test_submit_requires_all_questions_answered_and_returns_score_with_answers():
    store = ExamSessionStore()
    session_id = store.create_session(QUESTIONS, exam_size=2, seed=7)["session_id"]

    store.answer_question(session_id, 0, 0)

    with pytest.raises(ExamSessionError, match="every question"):
        store.submit_session(session_id)

    store.answer_question(session_id, 1, 1)
    submitted = store.submit_session(session_id)

    assert submitted["status"] == "submitted"
    assert submitted["complete"] is True
    assert submitted["score"] == {"correct": 2, "total": 2, "percentage": 100.0}
    assert all("correct_answer_index" in question for question in submitted["questions"])
    assert submitted["questions"][0]["explanation"] == "Paris is the capital of France."


@pytest.mark.parametrize(
    ("operation", "message"),
    [
        (lambda store, session_id: store.go_previous(session_id), "first question"),
        (lambda store, session_id: store.answer_question(session_id, 99, 0), "out of range"),
    ],
)
def test_invalid_operations_raise_errors(operation, message):
    store = ExamSessionStore()
    session_id = store.create_session(QUESTIONS, exam_size=2, seed=7)["session_id"]

    with pytest.raises(ExamSessionError, match=message):
        operation(store, session_id)
