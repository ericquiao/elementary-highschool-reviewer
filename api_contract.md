# Reviewer App Standard API Contract

This contract defines the canonical payloads that every thread and service should use after data passes through the existing dataset pipeline:

1. `validator.py` cleans question text, choices, answer fields, and explanation text.
2. `processor.py` normalizes `topic`, `subject`, `grade`, and `difficulty`.

The final API contract below is based on the fields these scripts already produce.

---

## 1) Question Object (final form)

### Canonical rules

- Each API question **must** represent one multiple-choice item.
- `choices` is the canonical answer list; upstream aliases such as `options` must be converted before serving.
- Exactly one choice must have `is_correct: true`.
- `answer`, `correct_answer`, and `answer_index` must agree with the correct choice.
- `question` must be a normalized display string.
- `topic`, `subject`, `grade`, and `difficulty` must already reflect processor output.

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewer-app.local/schema/question.schema.json",
  "title": "ReviewerQuestion",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id",
    "type",
    "subject",
    "topic",
    "grade",
    "difficulty",
    "question",
    "choices",
    "answer",
    "answer_index",
    "correct_answer",
    "explanation"
  ],
  "properties": {
    "id": {
      "description": "Stable question identifier unique within the dataset or API response.",
      "oneOf": [
        { "type": "string", "minLength": 1 },
        { "type": "integer", "minimum": 1 }
      ]
    },
    "type": {
      "type": "string",
      "const": "multiple_choice"
    },
    "subject": {
      "type": "string",
      "minLength": 1,
      "examples": ["Math", "English", "Science"]
    },
    "topic": {
      "type": "string",
      "minLength": 1
    },
    "grade": {
      "type": "integer",
      "minimum": 1,
      "maximum": 12
    },
    "difficulty": {
      "type": "string",
      "enum": ["easy", "medium", "hard"]
    },
    "question": {
      "type": "string",
      "minLength": 8
    },
    "choices": {
      "type": "array",
      "minItems": 2,
      "maxItems": 8,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["text", "is_correct"],
        "properties": {
          "text": {
            "type": "string",
            "minLength": 1
          },
          "is_correct": {
            "type": "boolean"
          }
        }
      },
      "allOf": [
        {
          "contains": {
            "type": "object",
            "properties": {
              "is_correct": { "const": true }
            },
            "required": ["is_correct"]
          },
          "minContains": 1,
          "maxContains": 1
        }
      ]
    },
    "answer": {
      "type": "string",
      "minLength": 1,
      "description": "Canonical answer text; must match the correct choice text exactly."
    },
    "answer_index": {
      "type": "integer",
      "minimum": 0
    },
    "correct_answer": {
      "type": "string",
      "minLength": 1,
      "description": "Duplicate of answer for explicitness and backward compatibility."
    },
    "explanation": {
      "type": "string",
      "minLength": 1
    },
    "source": {
      "type": "string",
      "description": "Optional dataset or ingestion source identifier."
    },
    "metadata": {
      "type": "object",
      "description": "Optional non-authoritative extra data for internal use.",
      "additionalProperties": true
    }
  }
}
```

### Example Question Object

```json
{
  "id": "math-5-6-0001",
  "type": "multiple_choice",
  "subject": "Math",
  "topic": "Fractions - Operations",
  "grade": 6,
  "difficulty": "medium",
  "question": "What is 1/4 + 2/4?",
  "choices": [
    { "text": "3/4", "is_correct": true },
    { "text": "3/8", "is_correct": false },
    { "text": "1/2", "is_correct": false },
    { "text": "2/8", "is_correct": false }
  ],
  "answer": "3/4",
  "answer_index": 0,
  "correct_answer": "3/4",
  "explanation": "The correct answer is 3/4.",
  "source": "grade5_6_math_mcq.json"
}
```

---

## 2) API response format

### Standard response envelope

All API endpoints that return questions should use a consistent top-level envelope.

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewer-app.local/schema/question-response.schema.json",
  "title": "QuestionApiResponse",
  "type": "object",
  "additionalProperties": false,
  "required": ["success", "data", "error", "meta"],
  "properties": {
    "success": {
      "type": "boolean"
    },
    "data": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["questions"],
          "properties": {
            "questions": {
              "type": "array",
              "items": {
                "$ref": "https://reviewer-app.local/schema/question.schema.json"
              }
            }
          }
        },
        {
          "type": "null"
        }
      ]
    },
    "error": {
      "oneOf": [
        {
          "$ref": "https://reviewer-app.local/schema/error.schema.json"
        },
        {
          "type": "null"
        }
      ]
    },
    "meta": {
      "type": "object",
      "additionalProperties": false,
      "required": ["request_id", "timestamp"],
      "properties": {
        "request_id": {
          "type": "string",
          "minLength": 1
        },
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "count": {
          "type": "integer",
          "minimum": 0
        },
        "filters": {
          "type": "object",
          "additionalProperties": true
        },
        "version": {
          "type": "string"
        }
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "success": { "const": true } },
        "required": ["success"]
      },
      "then": {
        "properties": {
          "error": { "type": "null" }
        }
      }
    },
    {
      "if": {
        "properties": { "success": { "const": false } },
        "required": ["success"]
      },
      "then": {
        "properties": {
          "data": { "type": "null" }
        }
      }
    }
  ]
}
```

### Example request

```http
POST /api/v1/questions/search
Content-Type: application/json
```

```json
{
  "subject": "Math",
  "grade": 6,
  "topic": "Fractions - Operations",
  "difficulty": "medium",
  "limit": 2
}
```

### Example success response

```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": "math-5-6-0001",
        "type": "multiple_choice",
        "subject": "Math",
        "topic": "Fractions - Operations",
        "grade": 6,
        "difficulty": "medium",
        "question": "What is 1/4 + 2/4?",
        "choices": [
          { "text": "3/4", "is_correct": true },
          { "text": "3/8", "is_correct": false },
          { "text": "1/2", "is_correct": false },
          { "text": "2/8", "is_correct": false }
        ],
        "answer": "3/4",
        "answer_index": 0,
        "correct_answer": "3/4",
        "explanation": "The correct answer is 3/4.",
        "source": "grade5_6_math_mcq.json"
      },
      {
        "id": "math-5-6-0002",
        "type": "multiple_choice",
        "subject": "Math",
        "topic": "Fractions - Operations",
        "grade": 6,
        "difficulty": "medium",
        "question": "What is 3/5 - 1/5?",
        "choices": [
          { "text": "2/5", "is_correct": true },
          { "text": "1/5", "is_correct": false },
          { "text": "3/10", "is_correct": false },
          { "text": "4/5", "is_correct": false }
        ],
        "answer": "2/5",
        "answer_index": 0,
        "correct_answer": "2/5",
        "explanation": "The correct answer is 2/5.",
        "source": "normalized-dataset"
      }
    ]
  },
  "error": null,
  "meta": {
    "request_id": "req_01HQ7ZJ8N7AP4M3Y4M8R1Q2ABC",
    "timestamp": "2026-03-23T00:00:00Z",
    "count": 2,
    "filters": {
      "subject": "Math",
      "grade": 6,
      "topic": "Fractions - Operations",
      "difficulty": "medium",
      "limit": 2
    },
    "version": "v1"
  }
}
```

---

## 3) Error handling format

### Standard rules

- Every non-success response must set `success` to `false`.
- Every non-success response must set `data` to `null`.
- Every non-success response must include a structured `error` object.
- `code` must be stable and machine-readable.
- `message` must be short and safe to show to clients.
- `details` may include validation errors, unsupported filters, or internal tracing data that is safe to expose.

### JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://reviewer-app.local/schema/error.schema.json",
  "title": "ApiError",
  "type": "object",
  "additionalProperties": false,
  "required": ["code", "message"],
  "properties": {
    "code": {
      "type": "string",
      "enum": [
        "BAD_REQUEST",
        "VALIDATION_ERROR",
        "NOT_FOUND",
        "UNSUPPORTED_FILTER",
        "DATASET_EMPTY",
        "INTERNAL_ERROR"
      ]
    },
    "message": {
      "type": "string",
      "minLength": 1
    },
    "details": {
      "type": "object",
      "additionalProperties": true
    },
    "field_errors": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "message"],
        "properties": {
          "field": {
            "type": "string",
            "minLength": 1
          },
          "message": {
            "type": "string",
            "minLength": 1
          },
          "value": {}
        }
      }
    }
  }
}
```

### Example error response

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request payload is invalid.",
    "details": {
      "hint": "grade must be an integer from 1 to 12"
    },
    "field_errors": [
      {
        "field": "grade",
        "message": "Expected integer between 1 and 12.",
        "value": "6-7"
      }
    ]
  },
  "meta": {
    "request_id": "req_01HQ7ZJ8N7AP4M3Y4M8R1Q2XYZ",
    "timestamp": "2026-03-23T00:00:00Z",
    "version": "v1"
  }
}
```

---

## Implementation notes for all threads

- Treat this contract as the **post-pipeline** shape, not the raw dataset ingestion shape.
- If a dataset arrives with `options`, convert it to `choices` before serving.
- If a dataset arrives with string grade bands like `"5-6"` or `"6-7"`, normalize to a single integer grade before API output.
- Preserve `answer` and `correct_answer` for compatibility, even though they carry the same canonical value.
- Use the response envelope for both single-question and multi-question endpoints; single-question endpoints can still return `questions: [ ... ]` for consistency.
