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

The repository also includes `exam_session.py`, an in-memory exam-session manager that can:

- start an exam with a random subset of questions
- store session state
- navigate next/previous through the session
- record answers without revealing correctness until submission
- submit only after all questions are answered
- calculate the final score after submission
