# Elementary & High School Reviewer

Merged repository for the student reviewer project. It currently contains:

- the original lightweight Python/HTML/CSS/JS reviewer app at the repository root
- the newer `app/`-based Student Reviewer App built with a FastAPI backend, Angular frontend, and curriculum data assets

## Local project summary

The `app/` project is an AI-powered reviewer application for students that can explain lessons, interpret uploaded study images, and generate quizzes.

Framework used for the local build workflow: `rapid-ai-builder`

## Repository structure

- `app/backend/` contains the FastAPI backend for the newer local project
- `app/frontend/` contains the Angular frontend for the newer local project
- `app/data/` contains curriculum, question, topic, and report data assets
- root-level Python files and `frontend/` contain the original GitHub project

## Original root app

The original GitHub repository includes a simple study app with a lightweight Python backend API and a plain HTML/CSS/JS frontend.

### Features

- Home page with selectors for grade, subject, and mode
- Review mode with instant feedback
- Exam mode with score summary
- Result page that shows correct answers and explanations
- Mobile-friendly layout with minimal styling

### Run locally

```bash
python3 server.py
```

Then open <http://127.0.0.1:8000>.

### API endpoints

- `GET /api/config` returns grade, subject, and mode options
- `GET /api/questions?grade=...&subject=...&mode=...` returns quiz questions
- `POST /api/submit` scores answers and returns result details

## Existing utilities

### Validator

```bash
python3 validator.py < questions.json
```

### Tracking

The repository also includes a simple JSON tracking utility in `tracking.py`.

It records:
- questions answered
- correct vs. incorrect results
- weak topics based on missed questions

Example:

```python
from tracking import record_answer, summarize_performance

record_answer(
    user_id="user-1",
    session_id="session-a",
    question_id="q-42",
    topic="Fractions - Operations",
    is_correct=False,
)

summary = summarize_performance(user_id="user-1", session_id="session-a")
print(summary)
```

By default this writes to `tracking_log.json`, but you can pass a custom `path` to both functions.

## API test coverage

The original repository includes pytest coverage for the API and session flows.

Run everything with:

```bash
pytest
```

Or run the API-specific suites:

```bash
pytest tests/test_api.py tests/test_api_modes.py
```

## Question processing pipeline

### Pipeline

```bash
python3 pipeline.py
```

Reads `questions.json`, validates question shape, normalizes topics, writes `clean_questions.json`, and removes duplicate questions from the final dataset.

### Processor

```bash
python3 processor.py < some-array.json
```

## Review mode functions

`review_mode.py` provides reusable review-session helpers for apps or API layers:

- `start_review_session(questions)` initializes a session
- `get_current_question(session)` returns exactly one question at a time
- `submit_review_answer(session, selected_index)` returns immediate correct or incorrect feedback, the explanation, and the updated score
- `review_session_summary(session)` returns simple progress and scoring totals

## Exam session logic

The repository also includes `exam_session.py`, an in-memory exam-session manager that exposes store methods and thin endpoint-style functions for exam flows. It can:

- start an exam with a random subset of questions
- store and retrieve session state for ongoing exam and review screens
- navigate next and previous through the session
- record answers without revealing correctness until submission
- submit only after all questions are answered
- calculate the final score after submission
- keep review data visible when a submitted session is fetched later

## Root API

Run the root API locally with FastAPI:

```bash
uvicorn app:app --reload
```

### Endpoints

- `GET /questions?grade=&subject=&topic=&difficulty=` returns filtered questions
- `POST /submit` accepts `{"answers": [{"question_id": "...", "answer": "..."}]}` and returns score, correct answers, and explanations
- `GET /topics` returns available topics grouped by grade and subject
