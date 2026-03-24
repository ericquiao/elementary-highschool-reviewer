from review_mode import (
    get_current_question,
    review_session_summary,
    start_review_session,
    submit_review_answer,
)


def sample_questions():
    return [
        {
            "question": "What is 2 + 2?",
            "choices": ["3", "4", "5"],
            "answer_index": 1,
            "explanation": "2 + 2 equals 4.",
        },
        {
            "question": "What is 3 x 3?",
            "choices": [
                {"text": "6", "is_correct": False},
                {"text": "9", "is_correct": True},
                {"text": "12", "is_correct": False},
            ],
            "explanation": "3 times 3 equals 9.",
        },
    ]



def test_review_mode_shows_one_question_at_a_time_and_tracks_score():
    session = start_review_session(sample_questions())

    first_question = get_current_question(session)
    assert first_question["question_number"] == 1
    assert first_question["total_questions"] == 2
    assert first_question["question"] == "What is 2 + 2?"
    assert [choice["text"] for choice in first_question["choices"]] == ["3", "4", "5"]

    feedback = submit_review_answer(session, 1)
    assert feedback["correct"] is True
    assert feedback["indicator"] == "correct"
    assert feedback["explanation"] == "2 + 2 equals 4."
    assert feedback["score"] == {
        "correct_answers": 1,
        "answered_questions": 1,
        "total_questions": 2,
    }
    assert feedback["next_question"]["question_number"] == 2
    assert feedback["completed"] is False



def test_review_mode_returns_incorrect_feedback_and_completion_summary():
    session = start_review_session(sample_questions())

    submit_review_answer(session, 0)
    second_feedback = submit_review_answer(session, 0)

    assert second_feedback["correct"] is False
    assert second_feedback["indicator"] == "incorrect"
    assert second_feedback["correct_choice"] == {"index": 1, "text": "9"}
    assert second_feedback["selected_choice"] == {"index": 0, "text": "6"}
    assert second_feedback["explanation"] == "3 times 3 equals 9."
    assert second_feedback["next_question"] is None
    assert second_feedback["completed"] is True

    assert review_session_summary(session) == {
        "completed": True,
        "score": 0,
        "answered_questions": 2,
        "total_questions": 2,
        "remaining_questions": 0,
    }
