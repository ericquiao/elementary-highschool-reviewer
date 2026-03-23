from __future__ import annotations

from typing import Any, Dict, List, Optional


ReviewSession = Dict[str, Any]
Question = Dict[str, Any]


def _get_question_text(question: Question) -> str:
    return str(question.get("question") or question.get("prompt") or "")



def _serialize_choice(choice: Any, index: int) -> Dict[str, Any]:
    if isinstance(choice, dict):
        text = str(choice.get("text") or choice.get("label") or choice.get("value") or choice.get("choice") or "")
        is_correct = bool(choice.get("is_correct", False))
    else:
        text = str(choice)
        is_correct = False
    return {
        "index": index,
        "text": text,
        "is_correct": is_correct,
    }



def _normalize_questions(questions: List[Question]) -> List[Question]:
    normalized: List[Question] = []
    for raw in questions:
        choices = [_serialize_choice(choice, idx) for idx, choice in enumerate(raw.get("choices", []))]

        correct_index = raw.get("answer_index")
        if not isinstance(correct_index, int):
            correct_index = next((choice["index"] for choice in choices if choice["is_correct"]), 0 if choices else None)

        if correct_index is not None:
            for choice in choices:
                choice["is_correct"] = choice["index"] == correct_index

        normalized.append(
            {
                "question": _get_question_text(raw),
                "choices": choices,
                "answer_index": correct_index,
                "answer": str(raw.get("answer") or raw.get("correct_answer") or ""),
                "explanation": str(raw.get("explanation") or ""),
                "topic": str(raw.get("topic") or ""),
                "subject": str(raw.get("subject") or ""),
                "grade": raw.get("grade"),
                "difficulty": str(raw.get("difficulty") or ""),
            }
        )
    return normalized



def _public_question(question: Question, number: int, total: int) -> Dict[str, Any]:
    return {
        "question_number": number,
        "total_questions": total,
        "question": question["question"],
        "choices": [
            {
                "index": choice["index"],
                "text": choice["text"],
            }
            for choice in question["choices"]
        ],
        "topic": question.get("topic", ""),
        "subject": question.get("subject", ""),
        "grade": question.get("grade"),
        "difficulty": question.get("difficulty", ""),
    }



def start_review_session(questions: List[Question]) -> ReviewSession:
    normalized = _normalize_questions(questions)
    return {
        "questions": normalized,
        "current_index": 0,
        "score": 0,
        "answers": [],
        "completed": len(normalized) == 0,
    }



def get_current_question(session: ReviewSession) -> Optional[Dict[str, Any]]:
    if session["completed"] or session["current_index"] >= len(session["questions"]):
        return None
    question = session["questions"][session["current_index"]]
    return _public_question(question, session["current_index"] + 1, len(session["questions"]))



def submit_review_answer(session: ReviewSession, selected_index: int) -> Dict[str, Any]:
    current = get_current_question(session)
    if current is None:
        raise IndexError("Review session is already complete.")

    question = session["questions"][session["current_index"]]
    correct_index = question["answer_index"]
    is_correct = selected_index == correct_index
    if is_correct:
        session["score"] += 1

    correct_choice = next(
        ({"index": choice["index"], "text": choice["text"]} for choice in question["choices"] if choice["index"] == correct_index),
        None,
    )
    selected_choice = next(
        ({"index": choice["index"], "text": choice["text"]} for choice in question["choices"] if choice["index"] == selected_index),
        {"index": selected_index, "text": ""},
    )

    session["answers"].append(
        {
            "question_index": session["current_index"],
            "selected_index": selected_index,
            "correct_index": correct_index,
            "is_correct": is_correct,
        }
    )
    session["current_index"] += 1
    session["completed"] = session["current_index"] >= len(session["questions"])

    return {
        "question_number": current["question_number"],
        "correct": is_correct,
        "indicator": "correct" if is_correct else "incorrect",
        "selected_choice": selected_choice,
        "correct_choice": correct_choice,
        "explanation": question["explanation"],
        "score": {
            "correct_answers": session["score"],
            "answered_questions": len(session["answers"]),
            "total_questions": len(session["questions"]),
        },
        "next_question": get_current_question(session),
        "completed": session["completed"],
    }



def review_session_summary(session: ReviewSession) -> Dict[str, Any]:
    total = len(session["questions"])
    answered = len(session["answers"])
    return {
        "completed": session["completed"],
        "score": session["score"],
        "answered_questions": answered,
        "total_questions": total,
        "remaining_questions": max(total - answered, 0),
    }
