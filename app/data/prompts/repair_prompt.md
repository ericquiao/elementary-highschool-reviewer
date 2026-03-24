You are repairing a dataset that failed QA checks.

Inputs:

Grade: {grade}
Subject: {subject}

Dataset location:

app/data/questions/{grade}/{subject}.json

QA report:

app/data/reports/qa/{grade}_{subject}_qa.json

---

Goal

Improve datasets that fail QA without regenerating the entire dataset.

---

Repair rules

Do not regenerate the entire dataset.

Only fix flagged issues.

---

Repair modes

Mode 1 — Independent question repair

For subjects:

Math
Science
AP
ESP
TLE

Fix issues detected in the QA report:

• duplicates
• difficulty mismatches
• ambiguous questions
• topic mismatches

Repair rules:

Rewrite flagged questions while preserving:

• question ID
• topic
• difficulty label

---

Mode 2 — Passage-based repair

For subject:

English

When QA reports template or shallow questions:

Group related questions by topic.

Create reading passages.

Each passage should generate 3–5 comprehension questions.

---

Passage format

Save passages to:

app/data/passages/{grade}/english_passages.json

Structure:

{
"passage_id": "",
"grade": 5,
"subject": "English",
"topic": "",
"text": ""
}

---

Questions referencing passages

Questions must include:

"passage_id"

Example:

{
"id": "",
"passage_id": "",
"question": "",
"choices": [],
"correct_answer": ""
}

---

Independent repair rules

1. Duplicate questions

Rewrite duplicate questions so they:

• keep the same topic
• keep the same difficulty
• use different context or wording

---

2. Difficulty mismatch

Either:

• adjust the difficulty label

OR

• rewrite the question so its difficulty matches the label

---

3. Ambiguous questions

Rewrite the question so:

• only one answer is correct
• wording is clear

---

4. Topic mismatch

Rewrite the question so it clearly belongs to the assigned topic.

---

5. Template duplicates

Rewrite template-style questions with more varied structure and context.

---

Passage-based English repair process

1. Identify weak questions from QA report
2. Group them by topic
3. Generate passages
4. Replace weak questions with passage-based questions

For English repairs:

• preserve question IDs where questions are replaced
• preserve topic assignments
• add `passage_id` to repaired questions
• make the repaired questions depend on the passage text
• vary question types across:
  • explicit detail
  • vocabulary in context
  • inference
  • main idea
  • author's intent

---

Output

Update the dataset file in place:

app/data/questions/{grade}/{subject}.json

Preserve:

• question IDs
• topic assignments

If `subject = English`, also update:

app/data/passages/{grade}/english_passages.json

---

After repair:

Run:

validation_prompt.md
qa_prompt.md

Repeat repair cycle until:

quality_score ≥ threshold
