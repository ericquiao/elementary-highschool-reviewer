import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validator.py"
PROCESSOR = ROOT / "processor.py"


def run_cli(script: Path, payload, *, raw_input=None, check=True):
    if raw_input is None:
        raw_input = json.dumps(payload)
    result = subprocess.run(
        [sys.executable, str(script)],
        input=raw_input,
        text=True,
        capture_output=True,
        check=check,
    )
    return result


@pytest.mark.parametrize(
    ("script", "payload", "expected"),
    [
        (
            VALIDATOR,
            [
                {
                    "question": "2 + 3",
                    "choices": ["4", "5", "6", "5"],
                    "answer": "B",
                    "explanation": "It totals 5.",
                }
            ],
            [
                {
                    "question": "2 + 3?",
                    "choices": [
                        {"text": "4", "is_correct": False},
                        {"text": "5", "is_correct": True},
                        {"text": "6", "is_correct": False},
                    ],
                    "answer": "5",
                    "answer_index": 1,
                    "correct_answer": "5",
                    "explanation": "It totals 5.",
                }
            ],
        ),
        (
            PROCESSOR,
            [
                {
                    "question": "What percent of 50 is 10?",
                    "topic": "percent word problems",
                    "grade": None,
                    "subject": "",
                }
            ],
            [
                {
                    "question": "What percent of 50 is 10?",
                    "topic": "Percents - Applications",
                    "grade": 7,
                    "subject": "Math",
                    "difficulty": "hard",
                }
            ],
        ),
    ],
)
def test_api_samples_return_expected_outputs(script, payload, expected):
    """API-style sample requests produce the expected JSON shape and values."""
    result = run_cli(script, payload)
    output = json.loads(result.stdout)

    for expected_item, output_item in zip(expected, output):
        for key, value in expected_item.items():
            assert output_item[key] == value


@pytest.mark.parametrize("script", [VALIDATOR, PROCESSOR])
def test_api_empty_request_returns_empty_list_without_crashing(script):
    result = run_cli(script, payload=None, raw_input="")
    assert result.returncode == 0
    assert json.loads(result.stdout) == []
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("sample_request", "expected_answer", "expected_index", "expected_score"),
    [
        (
            {
                "question": "Which fraction is equivalent to 1/2",
                "choices": ["1/4", "2/4", "3/4", "2/4"],
                "answer": "2/4",
                "explanation": "2/4 equals 1/2.",
            },
            "2/4",
            1,
            1,
        ),
        (
            {
                "question": "Pick the prime number",
                "choices": [
                    {"text": "4", "correct": "false"},
                    {"text": "5", "correct": "true"},
                    {"text": "6", "correct": "false"},
                ],
                "explanation": "5 is prime.",
            },
            "5",
            1,
            1,
        ),
    ],
)
def test_exam_mode_samples_keep_single_correct_answer_and_score(sample_request, expected_answer, expected_index, expected_score):
    """Exam mode sample requests should always normalize to one scorable correct answer."""
    result = run_cli(VALIDATOR, [sample_request])
    item = json.loads(result.stdout)[0]

    actual_score = sum(choice["is_correct"] for choice in item["choices"])

    assert item["answer"] == expected_answer
    assert item["answer_index"] == expected_index
    assert item["correct_answer"] == expected_answer
    assert actual_score == expected_score



def test_exam_mode_handles_sparse_question_without_crashing():
    result = run_cli(VALIDATOR, [{"choices": [], "explanation": None}])
    item = json.loads(result.stdout)[0]

    assert result.returncode == 0
    assert item["choices"] == []
    assert item["answer"] == ""
    assert item["answer_index"] is None
    assert item["correct_answer"] == ""
    assert item["explanation"] == ""


@pytest.mark.parametrize(
    ("sample_request", "expected_output"),
    [
        (
            {
                "question": "Solve the equation 4x = 20.",
                "topic": "intro algebra",
                "grade": 5,
                "subject": "science",
            },
            {
                "topic": "Algebra - Expressions and Equations",
                "subject": "Math",
                "grade": 8,
                "difficulty": "hard",
            },
        ),
        (
            {
                "prompt": "Read the bar graph and compare the values.",
                "topic": "graphs",
                "grade": None,
                "subject": "",
                "choices": ["A", "B", "C", "D"],
            },
            {
                "topic": "Data and Statistics",
                "subject": "Math",
                "grade": 6,
                "difficulty": "hard",
            },
        ),
    ],
)
def test_review_mode_samples_infer_expected_metadata(sample_request, expected_output):
    """Review mode sample requests should enrich content with stable review metadata."""
    result = run_cli(PROCESSOR, [sample_request])
    item = json.loads(result.stdout)[0]

    assert item["topic"] == expected_output["topic"]
    assert item["subject"] == expected_output["subject"]
    assert item["grade"] == expected_output["grade"]
    assert item["difficulty"] == expected_output["difficulty"]



def test_review_mode_handles_minimal_payload_without_crashing():
    result = run_cli(PROCESSOR, [{"question": "", "topic": "", "grade": "bad"}])
    item = json.loads(result.stdout)[0]

    assert result.returncode == 0
    assert item["topic"] == "General"
    assert item["subject"] == "Math"
    assert item["grade"] == 6
    assert item["difficulty"] == "easy"
