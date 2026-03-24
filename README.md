# Elementary & High School Reviewer

Simple study app with a lightweight Python backend API and a plain HTML/CSS/JS frontend.

## Features

- Home page with selectors for grade, subject, and mode.
- Review mode with instant feedback.
- Exam mode with score summary.
- Result page that shows correct answers and explanations.
- Mobile-friendly layout with minimal styling.

## Run locally

```bash
python3 server.py
```

Then open <http://127.0.0.1:8000>.

## API endpoints

- `GET /api/config` returns grade, subject, and mode options.
- `GET /api/questions?grade=...&subject=...&mode=...` returns quiz questions.
- `POST /api/submit` scores answers and returns result details.

## Existing utilities

### Validator

```bash
python3 validator.py < questions.json
```

## Pipeline

To run the full pipeline end-to-end:

```bash
python3 pipeline.py
```

The pipeline will:
1. Load raw JSON from `questions.json`.
2. Validate and clean each question.
3. Process the cleaned questions.
4. Save the final dataset to `clean_questions.json`.

It is safe to run repeatedly because it always rewrites `clean_questions.json` and removes duplicate questions from the final dataset.
### Processor

```bash
python3 processor.py < some-array.json
```
## Review Mode Functions

`review_mode.py` provides reusable review-session helpers for apps or API layers:

- `start_review_session(questions)` initializes a session.
- `get_current_question(session)` returns exactly one question at a time.
- `submit_review_answer(session, selected_index)` returns immediate correct/incorrect feedback, the explanation, and the updated score.
- `review_session_summary(session)` returns simple progress and scoring totals.

## Exam session logic

The repository also includes `exam_session.py`, an in-memory exam-session manager that exposes store methods and thin endpoint-style functions for exam flows. It can:

- start an exam with a random subset of questions
- store and retrieve session state for ongoing exam/review screens
- navigate next/previous through the session
- record answers without revealing correctness until submission
- submit only after all questions are answered
- calculate the final score after submission
- keep review data visible when a submitted session is fetched later

## API

Run the API locally with FastAPI:

```bash
uvicorn app:app --reload
```

### Endpoints

- `GET /questions?grade=&subject=&topic=&difficulty=` returns filtered questions.
- `POST /submit` accepts `{"answers": [{"question_id": "...", "answer": "..."}]}` and returns score, correct answers, and explanations.
- `GET /topics` returns available topics grouped by grade and subject.
