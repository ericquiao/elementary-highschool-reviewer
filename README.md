# Question Validator

Small CLI utility that cleans a JSON array of multiple-choice questions.

## Behavior

- Ensures there is exactly one correct answer.
- Removes duplicate choices.
- Makes question text minimally clearer when possible.
- Rewrites explanations when they do not match the correct answer.
- Outputs cleaned JSON only.

## Usage

```bash
python3 validator.py < questions.json
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
