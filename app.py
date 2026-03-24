from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from processor import process_questions
from validator import clean_question

BASE_DIR = Path(__file__).resolve().parent
DATA_FILES = [
    BASE_DIR / 'questions.json',
    BASE_DIR / 'grade5_6_math_mcq.json',
]


class AnswerSubmission(BaseModel):
    question_id: str = Field(..., description='Unique question identifier')
    answer: str = Field(..., description='User-selected answer text')


class SubmitRequest(BaseModel):
    answers: List[AnswerSubmission]


class QuestionRepository:
    def __init__(self, data_files: List[Path]) -> None:
        self._data_files = data_files
        self._questions = self._load_questions()
        self._questions_by_id = {item['id']: item for item in self._questions}
        self._topics = self._build_topics_index(self._questions)

    def _load_questions(self) -> List[Dict[str, Any]]:
        combined: List[Dict[str, Any]] = []
        for data_file in self._data_files:
            payload = json.loads(data_file.read_text())
            base_grade = payload.get('grade') or payload.get('grade_band')
            base_subject = payload.get('subject')
            for raw_question in payload.get('questions', []):
                normalized = self._normalize_question(raw_question, data_file.stem, base_grade, base_subject)
                combined.append(normalized)

        processed = process_questions(combined)
        return sorted(processed, key=lambda item: item['id'])

    def _normalize_question(
        self,
        question: Dict[str, Any],
        source_name: str,
        base_grade: Any,
        base_subject: Optional[str],
    ) -> Dict[str, Any]:
        normalized = {
            'id': f"{source_name}-{question.get('id')}",
            'topic': question.get('topic', ''),
            'question': question.get('question', ''),
            'choices': question.get('choices') or question.get('options') or [],
            'answer': question.get('answer', ''),
            'explanation': question.get('explanation', ''),
            'subject': question.get('subject') or base_subject or '',
            'grade': question.get('grade') or base_grade,
            'difficulty': question.get('difficulty'),
            'type': question.get('type', 'multiple_choice'),
            'source': source_name,
        }
        cleaned = clean_question(normalized)
        if question.get('difficulty'):
            cleaned['difficulty'] = str(question['difficulty']).strip().lower()
        return cleaned

    def _build_topics_index(self, questions: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[str]]]:
        index: Dict[str, Dict[str, set[str]]] = {}
        for question in questions:
            grade_key = str(question['grade'])
            subject_key = str(question['subject'])
            index.setdefault(grade_key, {}).setdefault(subject_key, set()).add(question['topic'])

        return {
            grade: {subject: sorted(topics) for subject, topics in subjects.items()}
            for grade, subjects in sorted(index.items(), key=lambda item: int(item[0]))
        }

    def get_questions(
        self,
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = self._questions
        if grade is not None:
            results = [item for item in results if item['grade'] == grade]
        if subject:
            expected = subject.strip().casefold()
            results = [item for item in results if str(item['subject']).casefold() == expected]
        if topic:
            expected = topic.strip().casefold()
            results = [item for item in results if str(item['topic']).casefold() == expected]
        if difficulty:
            expected = difficulty.strip().casefold()
            results = [item for item in results if str(item['difficulty']).casefold() == expected]
        return results

    def get_topics(self) -> Dict[str, Dict[str, List[str]]]:
        return self._topics

    def score_submission(self, submission: SubmitRequest) -> Dict[str, Any]:
        results = []
        score = 0
        for item in submission.answers:
            question = self._questions_by_id.get(item.question_id)
            if question is None:
                raise HTTPException(status_code=404, detail=f'Question not found: {item.question_id}')

            user_answer = item.answer.strip()
            correct_answer = question['answer']
            is_correct = user_answer.casefold() == str(correct_answer).casefold()
            score += int(is_correct)
            results.append({
                'question_id': item.question_id,
                'question': question['question'],
                'submitted_answer': user_answer,
                'is_correct': is_correct,
                'correct_answer': correct_answer,
                'explanation': question['explanation'],
            })

        return {
            'score': score,
            'total': len(submission.answers),
            'results': results,
        }


repository = QuestionRepository(DATA_FILES)
app = FastAPI(title='Elementary & High School Reviewer API')


@app.get('/questions')
def get_questions(
    grade: Optional[int] = Query(default=None),
    subject: Optional[str] = Query(default=None),
    topic: Optional[str] = Query(default=None),
    difficulty: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    questions = repository.get_questions(grade=grade, subject=subject, topic=topic, difficulty=difficulty)
    return {'count': len(questions), 'questions': questions}


@app.post('/submit')
def submit_answers(payload: SubmitRequest) -> Dict[str, Any]:
    return repository.score_submission(payload)


@app.get('/topics')
def get_topics() -> Dict[str, Dict[str, List[str]]]:
    return repository.get_topics()
