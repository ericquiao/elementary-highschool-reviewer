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
