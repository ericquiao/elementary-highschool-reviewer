import os
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .gemini_service import GeminiServiceError, generate_review
from .models import ReviewResponse
from .temp_files import delete_temp_file, save_upload_to_temp

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

app = FastAPI(title="Student Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4200",
        "http://localhost:4200",
        "http://127.0.0.1:4210",
        "http://localhost:4210",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/review", response_model=ReviewResponse)
async def review(
    question: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    image_context: Optional[str] = Form(default=None),
    subject: str = Form(default="Science"),
    include_quiz: bool = Form(default=True),
    grade_level: str = Form(default="Grade 5"),
    question_count: int = Form(default=10),
) -> ReviewResponse:
    cleaned_question = question.strip() if question else None
    has_question = bool(cleaned_question)
    has_image = image is not None and bool(image.filename)

    if has_question == has_image:
        raise HTTPException(status_code=422, detail="Provide either a question or one image.")

    if question_count < 1 or question_count > 30:
        raise HTTPException(status_code=422, detail="Question count must be between 1 and 30.")

    temp_path: Optional[str] = None
    try:
        if has_question:
            return await generate_review(
                question=cleaned_question,
                subject=subject,
                include_quiz=include_quiz,
                grade_level=grade_level,
                question_count=question_count,
            )

        temp_path = await save_upload_to_temp(image)
        return await generate_review(
            image_path=temp_path,
            image_context=image_context.strip() if image_context else None,
            subject=subject,
            include_quiz=include_quiz,
            grade_level=grade_level,
            question_count=question_count,
        )
    except GeminiServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        delete_temp_file(temp_path)
