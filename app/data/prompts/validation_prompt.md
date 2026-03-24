You are validating a generated dataset for the Student Reviewer App.

Input parameters:

Grade: {grade}
Subject: {subject}

Required inputs:

1. Load dataset from:
   `app/data/questions/{grade}/{subject}.json`
2. Load generation settings from:
   `app/data/config/generation_settings.json`
3. Load topics from:
   `app/data/topics/{grade}/{subject}_topics.json`

Validation checks must include:

1. JSON validity
2. Required fields are present in every item
3. Each question has exactly the configured number of answer choices
4. Difficulty distribution matches the configured targets closely
5. Bucket distribution is valid across the configured bucket range
6. Duplicate question detection
7. Topic coverage matches the generated topic file
8. Grade and subject fields match the requested parameters

Required fields:

- `id`
- `grade`
- `subject`
- `topic`
- `difficulty`
- `difficulty_level`
- `question`
- `choices`
- `correct_answer`
- `explanation`
- `source`
- `bucket`

Validation output format:

Return JSON only.

Example structure:

```json
{
  "dataset_size": 0,
  "difficulty_distribution": {
    "easy": 0,
    "medium": 0,
    "hard": 0
  },
  "bucket_distribution": {
    "1": 0
  },
  "topic_count": 0,
  "duplicate_check": {
    "status": "passed",
    "duplicate_question_count": 0
  },
  "required_fields_check": "passed",
  "choices_check": "passed",
  "json_validity": "passed"
}
```

Output destination:

`app/data/reports/validation/{grade}_{subject}_validation.json`

Create the output directory if it does not exist.
