import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_pipeline(input_path: Path, output_path: Path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "pipeline.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
        env={**__import__("os").environ},
    )
    assert result.returncode == 0
    return json.loads(output_path.read_text())


def test_pipeline_creates_clean_deduped_output(tmp_path):
    input_path = ROOT / "questions.json"
    output_path = ROOT / "clean_questions.json"
    original_input = input_path.read_text(encoding="utf-8") if input_path.exists() else None
    original_output = output_path.read_text(encoding="utf-8") if output_path.exists() else None

    payload = {
        "grade": "5",
        "subject": "math",
        "questions": [
            {
                "topic": "fractions",
                "question": "Add 1/2 + 1/4",
                "choices": ["3/4", "1/2", "3/4"],
                "answer": "3/4",
            },
            {
                "topic": "fractions",
                "question": "Add 1/2 + 1/4",
                "choices": ["3/4", "1/2"],
                "answer": "3/4",
            },
        ],
    }

    try:
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        first = run_pipeline(input_path, output_path)
        second = run_pipeline(input_path, output_path)
    finally:
        if original_input is None:
            input_path.unlink(missing_ok=True)
        else:
            input_path.write_text(original_input, encoding="utf-8")
        if original_output is None:
            output_path.unlink(missing_ok=True)
        else:
            output_path.write_text(original_output, encoding="utf-8")

    assert len(first) == 1
    assert first == second
    assert first[0]["question"].endswith("?")
    assert first[0]["topic"] == "Fractions - Operations"
    assert first[0]["subject"] == "Math"
    assert first[0]["answer"] == "3/4"
