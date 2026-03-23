import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_processor(payload):
    result = subprocess.run(
        [sys.executable, str(ROOT / "processor.py")],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_fraction_topic_subject_grade_and_difficulty():
    payload = [
        {
            "question": "Add 1/4 + 3/8.",
            "topic": "fractions addition",
            "grade": 3,
            "subject": "math",
        }
    ]
    output = run_processor(payload)[0]
    assert output["topic"] == "Fractions - Operations"
    assert output["subject"] == "Math"
    assert output["grade"] == 5
    assert output["difficulty"] == "medium"



def test_algebra_question_normalizes_fields():
    payload = [
        {
            "question": "Solve the equation 3x + 5 = 20.",
            "topic": "basic algebra",
            "grade": 4,
            "subject": "reading",
        }
    ]
    output = run_processor(payload)[0]
    assert output["topic"] == "Algebra - Expressions and Equations"
    assert output["subject"] == "Math"
    assert output["grade"] == 8
    assert output["difficulty"] == "hard"
