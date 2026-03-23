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

