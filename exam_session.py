#!/usr/bin/env python3
import random
import uuid
from copy import deepcopy
from typing import Any, Dict, List, Optional


class ExamSessionError(ValueError):
    """Raised when an exam session action cannot be completed."""


class ExamSessionStore:
    """In-memory store for exam sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, questions: List[Dict[str, Any]], exam_size: Optional[int] = None, *, seed: Optional[int] = None) -> Dict[str, Any]:
        if not questions:
            raise ExamSessionError("Cannot start an exam without questions.")

        normalized_questions = [normalize_question(question, index) for index, question in enumerate(questions)]
        total_available = len(normalized_questions)
        total_questions = total_available if exam_size is None else exam_size

        if total_questions <= 0:
            raise ExamSessionError("Exam size must be greater than zero.")
        if total_questions > total_available:
            raise ExamSessionError("Exam size cannot exceed the number of available questions.")

        rng = random.Random(seed)
        selected_questions = rng.sample(normalized_questions, total_questions)
        session_id = str(uuid.uuid4())
        answers = [None] * total_questions

        session = {
            "session_id": session_id,
            "status": "in_progress",
            "current_index": 0,
            "questions": selected_questions,
            "answers": answers,
            "submitted": False,
            "score": None,
        }
        self._sessions[session_id] = session
        return build_session_payload(session)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        return build_session_payload(session)

    def answer_question(self, session_id: str, question_index: int, selected_index: int) -> Dict[str, Any]:
        session = self._require_open_session(session_id)
        question = self._require_question(session, question_index)

        if not 0 <= selected_index < len(question["choices"]):
            raise ExamSessionError("Selected answer is out of range.")

        session["answers"][question_index] = selected_index
        session["current_index"] = question_index
        return build_session_payload(session)

    def go_next(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        if session["current_index"] >= len(session["questions"]) - 1:
            raise ExamSessionError("Already at the last question.")
        session["current_index"] += 1
        return build_session_payload(session)

    def go_previous(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        if session["current_index"] <= 0:
            raise ExamSessionError("Already at the first question.")
        session["current_index"] -= 1
        return build_session_payload(session)

    def submit_session(self, session_id: str) -> Dict[str, Any]:
        session = self._require_open_session(session_id)
        if any(answer is None for answer in session["answers"]):
            raise ExamSessionError("Cannot submit exam until every question has an answer.")

        correct_count = sum(
            1
            for answer, question in zip(session["answers"], session["questions"])
            if answer == question["correct_answer_index"]
        )
        session["submitted"] = True
        session["status"] = "submitted"
        session["score"] = {
            "correct": correct_count,
            "total": len(session["questions"]),
            "percentage": round((correct_count / len(session["questions"])) * 100, 2),
        }
        return build_session_payload(session, include_answers=True)

    def _require_session(self, session_id: str) -> Dict[str, Any]:
        session = self._sessions.get(session_id)
        if session is None:
            raise ExamSessionError(f"Unknown session: {session_id}")
        return session

    def _require_open_session(self, session_id: str) -> Dict[str, Any]:
        session = self._require_session(session_id)
        if session["submitted"]:
            raise ExamSessionError("Exam session has already been submitted.")
        return session

    @staticmethod
    def _require_question(session: Dict[str, Any], question_index: int) -> Dict[str, Any]:
        if not 0 <= question_index < len(session["questions"]):
            raise ExamSessionError("Question index is out of range.")
        return session["questions"][question_index]


def normalize_question(question: Dict[str, Any], fallback_index: int) -> Dict[str, Any]:
    if not isinstance(question, dict):
        raise ExamSessionError("Each question must be a dictionary.")

    choices = deepcopy(question.get("choices") or [])
    if not choices:
        raise ExamSessionError("Each question must include choices.")

    correct_index = question.get("answer_index")
    if not isinstance(correct_index, int) or not 0 <= correct_index < len(choices):
        raise ExamSessionError("Each question must include a valid answer_index.")

    return {
        "id": question.get("id") or f"question-{fallback_index}",
        "question": str(question.get("question") or question.get("prompt") or ""),
        "choices": [choice["text"] if isinstance(choice, dict) and "text" in choice else str(choice) for choice in choices],
        "correct_answer_index": correct_index,
        "explanation": str(question.get("explanation") or ""),
    }


def build_session_payload(session: Dict[str, Any], *, include_answers: bool = False) -> Dict[str, Any]:
    questions = []
    for index, question in enumerate(session["questions"]):
        payload_question = {
            "index": index,
            "id": question["id"],
            "question": question["question"],
            "choices": deepcopy(question["choices"]),
            "selected_answer_index": session["answers"][index],
        }
        if include_answers:
            payload_question["correct_answer_index"] = question["correct_answer_index"]
            payload_question["explanation"] = question["explanation"]
        questions.append(payload_question)

    answered_count = sum(answer is not None for answer in session["answers"])
    return {
        "session_id": session["session_id"],
        "status": session["status"],
        "current_index": session["current_index"],
        "total_questions": len(session["questions"]),
        "answered_questions": answered_count,
        "complete": answered_count == len(session["questions"]),
        "score": deepcopy(session["score"]),
        "questions": questions,
    }
