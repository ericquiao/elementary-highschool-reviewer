#!/usr/bin/env python3
import json
import re
import sys
from typing import Any, Dict, List

TOPIC_RULES = [
    (re.compile(r"\bfraction[s]?\b"), "Fractions - Operations"),
    (re.compile(r"\bdecimal[s]?\b"), "Decimals - Operations"),
    (re.compile(r"\bpercent(?:age)?s?\b"), "Percents - Applications"),
    (re.compile(r"\bratio[s]?\b|\bproportion(?:al)?s?\b|\bunit rate\b|\brate[s]?\b"), "Ratios and Proportional Relationships"),
    (re.compile(r"\binteger[s]?\b|\bnegative number[s]?\b"), "Integers - Operations"),
    (re.compile(r"\bequation[s]?\b|\bexpression[s]?\b|\balgebra\b|\blinear\b"), "Algebra - Expressions and Equations"),
    (re.compile(r"\bgeometry\b|\bangle[s]?\b|\btriangle[s]?\b|\bcircle[s]?\b|\barea\b|\bperimeter\b|\bvolume\b"), "Geometry - Measurement and Shapes"),
    (re.compile(r"\bdata\b|\bgraph[s]?\b|\bplot[s]?\b|\bstatistics\b|\bprobability\b|\bmean\b|\bmedian\b|\bmode\b"), "Data and Statistics"),
    (re.compile(r"\bplace value\b|\brounding\b"), "Number Sense - Place Value"),
    (re.compile(r"\bmultiply\b|\bmultiplication\b|\bdivide\b|\bdivision\b|\badd\b|\baddition\b|\bsubtract\b|\bsubtraction\b"), "Arithmetic - Operations"),
]

SUBJECT_KEYWORDS = {
    "math": re.compile(
        r"\bfraction[s]?\b|\bdecimal[s]?\b|\bpercent(?:age)?s?\b|\bratio[s]?\b|\bproportion(?:al)?s?\b|\bequation[s]?\b|\balgebra\b|\bgeometry\b|\bangle[s]?\b|\btriangle[s]?\b|\bcircle[s]?\b|\barea\b|\bperimeter\b|\bvolume\b|\bgraph[s]?\b|\bstatistics\b|\bmean\b|\bmedian\b|\bmode\b|\bmultiply\b|\bdivide\b|\baddition\b|\bsubtraction\b|\bplace value\b|\binteger[s]?\b",
        re.I,
    )
}

GRADE_BANDS = [
    (re.compile(r"\bplace value\b|\baddition\b|\bsubtraction\b|\bshape[s]?\b|\bcounting\b", re.I), 2, 4),
    (re.compile(r"\bmultiply\b|\bdivision\b|\bfraction[s]?\b|\barea\b|\bperimeter\b|\bgraph[s]?\b", re.I), 4, 6),
    (re.compile(r"\bdecimal[s]?\b|\bratio[s]?\b|\bpercent(?:age)?s?\b|\binteger[s]?\b|\bequation[s]?\b|\bstatistics\b|\bprobability\b", re.I), 6, 8),
    (re.compile(r"\blinear\b|\balgebra\b|\bgeometry\b|\bvolume\b", re.I), 7, 9),
]


def normalize_topic(topic: str, text: str) -> str:
    source = f"{topic} {text}".lower()
    for pattern, normalized in TOPIC_RULES:
        if pattern.search(source):
            return normalized
    cleaned = re.sub(r"\s+", " ", topic).strip().title()
    return cleaned or "General"



def infer_subject(topic: str, text: str, current: str) -> str:
    source = f"{topic} {text}".lower()
    for subject, pattern in SUBJECT_KEYWORDS.items():
        if pattern.search(source):
            return subject.title()
    return current.title() if current else "Math"



def infer_grade(topic: str, text: str, current: Any) -> int:
    source = f"{topic} {text}".lower()
    candidates: List[int] = []
    for pattern, low, high in GRADE_BANDS:
        if pattern.search(source):
            candidates.append(round((low + high) / 2))
    if candidates:
        inferred = max(1, min(12, round(sum(candidates) / len(candidates))))
    else:
        inferred = None

    try:
        current_num = int(current)
    except (TypeError, ValueError):
        current_num = None

    if current_num is None:
        return inferred or 6

    if inferred is None:
        return max(1, min(12, current_num))

    return inferred



def infer_difficulty(question: Dict[str, Any]) -> str:
    text_parts = [
        str(question.get("question", "")),
        str(question.get("prompt", "")),
        str(question.get("topic", "")),
    ]
    if "choices" in question and isinstance(question["choices"], list):
        text_parts.extend(str(choice) for choice in question["choices"])
    text = " ".join(text_parts).lower()

    hard_signals = [
        "explain", "justify", "multi-step", "analyze", "compare", "probability", "equation", "percent", "ratio", "volume"
    ]
    medium_signals = [
        "fraction", "decimal", "area", "perimeter", "graph", "word problem", "divide", "multiply"
    ]

    if any(signal in text for signal in hard_signals):
        return "hard"
    if any(signal in text for signal in medium_signals):
        return "medium"
    return "easy"



def process_questions(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed = []
    for item in data:
        updated = dict(item)
        text = str(item.get("question") or item.get("prompt") or "")
        topic = str(item.get("topic") or "")
        updated["topic"] = normalize_topic(topic, text)
        updated["subject"] = infer_subject(updated["topic"], text, str(item.get("subject") or ""))
        updated["grade"] = infer_grade(updated["topic"], text, item.get("grade"))
        updated["difficulty"] = infer_difficulty(item)
        processed.append(updated)
    return processed



def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        print("[]")
        return 0
    data = json.loads(raw)
    if not isinstance(data, list):
        raise SystemExit("Input must be a JSON array.")
    print(json.dumps(process_questions(data), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
