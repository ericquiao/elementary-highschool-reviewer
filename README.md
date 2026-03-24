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


## Tracking

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
