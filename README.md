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


## API

Run the API locally with FastAPI:

```bash
uvicorn app:app --reload
```

### Endpoints

- `GET /questions?grade=&subject=&topic=&difficulty=` returns filtered questions.
- `POST /submit` accepts `{"answers": [{"question_id": "...", "answer": "..."}]}` and returns score, correct answers, and explanations.
- `GET /topics` returns available topics grouped by grade and subject.
