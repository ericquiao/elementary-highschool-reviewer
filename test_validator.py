import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def run_validator(payload):
    result = subprocess.run(
        [sys.executable, str(ROOT / "validator.py")],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_deduplicates_and_keeps_single_correct_answer():
    output = run_validator([
        {
            "question": "Capital of France",
            "choices": ["Paris", "Lyon", "Paris"],
            "answer": "Paris",
            "explanation": "Paris is the capital of France.",
        }
    ])
    item = output[0]
    assert item["question"].endswith("?")
    assert len(item["choices"]) == 2
    assert sum(choice["is_correct"] for choice in item["choices"]) == 1
    assert item["answer"] == "Paris"


def test_rewrites_explanation_when_it_does_not_match():
    output = run_validator([
        {
            "question": "2 + 2 = ?",
            "choices": [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
            ],
            "explanation": "Because math.",
        }
    ])
    item = output[0]
    assert item["explanation"] == "The correct answer is 4."
    assert item["answer_index"] == 1
