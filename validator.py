#!/usr/bin/env python3
import json
import re
import sys
from copy import deepcopy

LETTER_RE = re.compile(r"^[A-Z]$")
TRUTHY = {"true", "yes", "correct", "1"}
FALSY = {"false", "no", "incorrect", "0"}


def normalize_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def is_clear_question(text):
    text = normalize_text(text)
    if len(text) < 8:
        return False
    return any(ch in text for ch in "?.:") or text.lower().startswith(
        ("which", "what", "who", "when", "where", "why", "how", "select", "choose")
    )


def canonical_choice(choice):
    if isinstance(choice, str):
        return {"text": choice}
    if isinstance(choice, dict):
        result = deepcopy(choice)
        if "text" not in result:
            for key in ("label", "choice", "option", "value"):
                if key in result:
                    result["text"] = result[key]
                    break
        return result
    return {"text": str(choice)}


def choice_text(choice):
    return normalize_text(choice.get("text", ""))


def choice_is_marked_correct(choice):
    if "is_correct" in choice:
        value = str(choice["is_correct"]).strip().lower()
        if value in TRUTHY:
            return True
        if value in FALSY:
            return False
    if "correct" in choice:
        value = str(choice["correct"]).strip().lower()
        if value in TRUTHY:
            return True
        if value in FALSY:
            return False
    return False


def infer_correct_index(question, choices):
    answer = question.get("answer")
    answer_index = question.get("answer_index")
    correct_answer = question.get("correct_answer")

    if isinstance(answer_index, int) and 0 <= answer_index < len(choices):
        return answer_index

    if isinstance(answer, str):
        answer_norm = normalize_text(answer)
        if LETTER_RE.match(answer_norm) and len(choices) <= 26:
            idx = ord(answer_norm) - ord("A")
            if 0 <= idx < len(choices):
                return idx
        for idx, choice in enumerate(choices):
            if choice_text(choice).casefold() == answer_norm.casefold():
                return idx

    if isinstance(correct_answer, str):
        correct_norm = normalize_text(correct_answer)
        for idx, choice in enumerate(choices):
            if choice_text(choice).casefold() == correct_norm.casefold():
                return idx

    marked = [idx for idx, choice in enumerate(choices) if choice_is_marked_correct(choice)]
    if len(marked) == 1:
        return marked[0]
    if len(marked) > 1:
        return marked[0]

    return 0 if choices else None


def explanation_matches(explanation, answer_text):
    exp = normalize_text(explanation).casefold()
    ans = normalize_text(answer_text).casefold()
    if not exp or not ans:
        return False
    if ans in exp:
        return True
    ans_tokens = [token for token in re.split(r"\W+", ans) if len(token) > 3]
    return bool(ans_tokens) and any(token in exp for token in ans_tokens)


def clean_question(question):
    q = deepcopy(question) if isinstance(question, dict) else {"question": str(question)}
    choices = [canonical_choice(choice) for choice in q.get("choices", [])]

    seen = set()
    deduped = []
    for choice in choices:
        key = choice_text(choice).casefold()
        if key and key not in seen:
            seen.add(key)
            deduped.append(choice)
    choices = deduped

    correct_index = infer_correct_index(q, choices)
    for idx, choice in enumerate(choices):
        choice["is_correct"] = idx == correct_index
        choice.pop("correct", None)
    q["choices"] = choices

    if choices and correct_index is not None:
        q["answer"] = choice_text(choices[correct_index])
        q["answer_index"] = correct_index
        q["correct_answer"] = choice_text(choices[correct_index])
    else:
        q["answer"] = ""
        q["answer_index"] = None
        q["correct_answer"] = ""

    question_text = normalize_text(q.get("question", ""))
    if question_text and not is_clear_question(question_text):
        question_text = f"{question_text.rstrip('.')}?"
    q["question"] = question_text

    explanation = normalize_text(q.get("explanation", ""))
    if choices and correct_index is not None:
        answer_text = choice_text(choices[correct_index])
        if not explanation_matches(explanation, answer_text):
            explanation = f"The correct answer is {answer_text}."
    else:
        explanation = explanation or ""
    q["explanation"] = explanation
    return q


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print("[]")
        return
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Input must be a JSON array of questions")
    cleaned = [clean_question(item) for item in data]
    json.dump(cleaned, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
