#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from processor import process_questions
from validator import clean_question, normalize_text

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "questions.json"
DEFAULT_OUTPUT = ROOT / "clean_questions.json"


def load_raw_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_questions(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        questions = payload.get("questions")
        if isinstance(questions, list):
            base: Dict[str, Any] = {
                key: value
                for key, value in payload.items()
                if key not in {"questions", "topics"}
            }
            topic_list = payload.get("topics") if isinstance(payload.get("topics"), list) else None
            extracted = []
            for item in questions:
                if not isinstance(item, dict):
                    continue
                merged = dict(base)
                merged.update(item)
                if not merged.get("topic") and topic_list:
                    question_id = merged.get("id")
                    if isinstance(question_id, int) and 1 <= question_id <= len(topic_list):
                        merged["topic"] = topic_list[question_id - 1]
                extracted.append(merged)
            return extracted
    raise ValueError("Input JSON must be a list of questions or an object with a 'questions' list.")


def dedupe_questions(questions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[Tuple[str, str, str]] = set()
    unique: List[Dict[str, Any]] = []
    for item in questions:
        key = (
            normalize_text(item.get("question", "")).casefold(),
            normalize_text(item.get("topic", "")).casefold(),
            normalize_text(item.get("answer", item.get("correct_answer", ""))).casefold(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def run_pipeline(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> List[Dict[str, Any]]:
    raw_payload = load_raw_json(input_path)
    raw_questions = extract_questions(raw_payload)
    validated = [clean_question(question) for question in raw_questions]
    processed = process_questions(validated)
    final_questions = dedupe_questions(processed)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(final_questions, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return final_questions


if __name__ == "__main__":
    run_pipeline()
