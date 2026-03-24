import base64
import mimetypes
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from .models import ReviewResponse


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def build_prompt(include_quiz: bool, grade_level: str, question_count: int, subject: str) -> str:
    quiz_requirements = ""
    quiz_format = ""
    quiz_mode_instruction = "The user wants both an explanation and a quiz."

    if include_quiz:
        quiz_requirements = """
- Generate exactly {question_count} multiple choice questions.
- Each question must have exactly 4 answer choices.
- Include the correct answer after each question.
- Include a short explanation after each answer explaining why it is correct.
- Most questions should be basic difficulty, with a few medium ones.
""".format(question_count=question_count)
        quiz_format = """
Quiz:
1. ...
A. ...
B. ...
C. ...
D. ...
Answer: ...
Explanation: ...
"""
    else:
        quiz_mode_instruction = "The user wants explanation only. Do not include a Quiz section. Do not include any quiz questions. Do not include any answers."

    return f"""You are an AI study reviewer for students.

Analyze the student's input and return a student-friendly reviewer response as plain text.

Requirements:
- The student selected this subject for the request: {subject}.
- Treat {subject} as the intended school subject and keep the explanation and quiz aligned to it unless the input clearly conflicts.
- Target the explanation and examples for a student at {grade_level}.
- Adjust vocabulary, sentence length, and difficulty to match {grade_level}.
- {quiz_mode_instruction}
- Detect the most likely school subject and topic.
- Write 3 to 5 short explanation bullets using simple language for Grades 3 to 10.
- Include one short example when possible.
{quiz_requirements}- Keep the content focused on review and practice.

Use this format:
Detected Subject: <subject>
Detected Topic: <topic>

Explanation:
- ...
- ...

Example:
...
{quiz_format}
"""


class GeminiServiceError(Exception):
    pass


def _extract_text_response(payload: Dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        raise GeminiServiceError("Gemini returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_chunks = [part.get("text", "") for part in parts if part.get("text")]
    if not text_chunks:
        raise GeminiServiceError("Gemini returned no text content.")
    return "".join(text_chunks).strip()


def _build_text_parts(
    question: str,
    include_quiz: bool,
    grade_level: str,
    question_count: int,
    subject: str,
) -> list[dict[str, Any]]:
    return [
        {"text": build_prompt(include_quiz, grade_level, question_count, subject)},
        {"text": f"Student input:\n{question.strip()}"},
    ]


def _build_image_parts(
    image_path: str,
    include_quiz: bool,
    grade_level: str,
    question_count: int,
    subject: str,
    image_context: Optional[str],
) -> list[dict[str, Any]]:
    mime_type, _ = mimetypes.guess_type(image_path)
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    context_instruction = (
        f"Student context for this image:\n{image_context.strip()}"
        if image_context and image_context.strip()
        else "No extra student context was provided for this image."
    )

    return [
        {"text": build_prompt(include_quiz, grade_level, question_count, subject)},
        {
            "inline_data": {
                "mime_type": mime_type or "image/jpeg",
                "data": encoded_image,
            }
        },
        {"text": "Student input is an uploaded study image. Analyze the image content directly."},
        {"text": context_instruction},
    ]


async def generate_review(
    question: Optional[str] = None,
    image_path: Optional[str] = None,
    image_context: Optional[str] = None,
    subject: str = "Science",
    include_quiz: bool = True,
    grade_level: str = "Grade 5",
    question_count: int = 10,
) -> ReviewResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiServiceError("GEMINI_API_KEY is not set.")

    if bool(question) == bool(image_path):
        raise GeminiServiceError("Exactly one input type is required.")

    contents = (
        _build_text_parts(question, include_quiz, grade_level, question_count, subject)
        if question
        else _build_image_parts(image_path or "", include_quiz, grade_level, question_count, subject, image_context)
    )

    request_body = {
        "contents": [{"parts": contents}],
    }

    url = GEMINI_API_URL.format(model=DEFAULT_MODEL)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, headers=headers, json=request_body)

    if response.status_code >= 400:
        raise GeminiServiceError(f"Gemini request failed with status {response.status_code}: {response.text}")

    raw_text = _extract_text_response(response.json())
    return ReviewResponse(result=raw_text)
