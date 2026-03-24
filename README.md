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
