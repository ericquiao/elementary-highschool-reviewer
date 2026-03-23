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
