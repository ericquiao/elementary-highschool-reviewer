You are generating a structured question dataset for the Student Reviewer App.

Input parameters:

Grade: {grade}
Subject: {subject}

Required inputs:

1. Load topics from:
   `app/data/topics/{grade}/{subject}_topics.json`
2. Load generation settings from:
   `app/data/config/generation_settings.json`
3. If `subject = English`, also use passage storage under:
   `app/data/passages/{grade}/`

Use the settings exactly as provided:

- `questions_per_topic`
- `difficulty_distribution`
- `choices_per_question`
- `bucket_count`

Generation rules:

- Generate `questions_per_topic` questions for each topic.
- Match the difficulty distribution from the settings file across the full dataset.
- Each question must have exactly `choices_per_question` answer choices.
- Questions must match the target grade level.
- Avoid duplicate questions.
- Variations of the same concept are allowed if they are meaningfully different.
- Explanations must be short, correct, and student-friendly.
- Assign IDs in ascending order for the grade and subject.
- Distribute bucket numbers evenly from `1` to `bucket_count`, cycling as needed.
- Questions must test actual subject competencies, not just recognition of the lesson topic name.
- Do not use template patterns such as:
  `In Grade X subject, a student practices topic Y...`
  or other topic-label matching formats.

Subject-aware generation rules:

- If `subject = English`, generate shared reading passages first, then generate passage-linked comprehension questions.
- If `subject` is not English, continue generating independent questions using the standard schema and rules.
- Non-English subjects must preserve the current pipeline behavior.

Math generation rules:

- Math questions must assess real mathematical skill and understanding.
- Do not write questions that ask the learner to identify or recognize the topic title.
- Use this question-type distribution across the Math dataset:
  - `40%` concept questions
  - `40%` computation questions
  - `20%` word problems
- Concept questions should test understanding of place value, properties, relationships, classification, or interpretation.
- Computation questions should require the learner to solve a numeric expression or procedure.
- Word problems should place the skill in a short realistic scenario and require the correct mathematical operation or reasoning.

Examples of acceptable Math questions:

- Concept:
  `What is the place value of the digit 7 in 3,472,615?`
- Computation:
  `345,728 + 47,192 = ?`
- Word problem:
  `A library has 345,728 books and buys 47,192 more. How many books are there now?`

Science generation rules:

- Science questions must assess actual science understanding rather than topic-name recognition.
- Use varied science question types across the dataset:
  - concept understanding
  - real-life application
  - cause and effect
  - classification
  - simple experiments
- Questions should ask about observable properties, processes, relationships, evidence, or outcomes.
- Real-life application items should connect the concept to common materials, situations, or classroom observations.
- Simple experiment items should ask about setup, prediction, result, or conclusion at a grade-appropriate level.

Example of an acceptable Science question:

- `Which material is a good conductor of electricity?`

Passage schema for English:

```json
{
  "passage_id": "",
  "grade": 5,
  "subject": "English",
  "topic": "",
  "text": ""
}
```

Example:

```json
{
  "passage_id": "P-G5-ENG-001",
  "grade": 5,
  "subject": "English",
  "topic": "Reading Comprehension",
  "text": "Short reading passage text..."
}
```

English generation rules:

1. Generate reading passages first.
2. Each passage must produce `3` to `5` comprehension questions.
3. Questions must reference the shared passage using `passage_id`.
4. Use varied comprehension targets across the set:
   - explicit detail
   - vocabulary in context
   - inference
   - main idea
   - author's intent
5. Passage text and questions must match the target grade level.
6. Preserve topic coverage while grouping related English questions around shared passages.
7. English questions remain passage-based and should continue to use `passage_id`.

English question schema:

```json
{
  "id": "",
  "passage_id": "",
  "grade": 5,
  "subject": "English",
  "topic": "",
  "difficulty": "",
  "question": "",
  "choices": ["", "", "", ""],
  "correct_answer": "",
  "explanation": "",
  "bucket": 1
}
```

English output guidance:

- Save passage records under `app/data/passages/{grade}/`.
- Passage IDs must be stable and reusable by the linked English questions.
- English questions must include `passage_id` so future QA and repair steps can trace them back to a shared passage.

Question schema:

```json
{
  "id": "",
  "grade": {grade},
  "subject": "{subject}",
  "topic": "",
  "difficulty": "",
  "difficulty_level": 1,
  "question": "",
  "choices": ["", "", "", ""],
  "correct_answer": "",
  "explanation": "",
  "source": "codex_seed",
  "bucket": 1
}
```

ID rules:

- Format IDs as:
  `G{grade_number}-{SUBJECT}-{sequence}`
- Example:
  `G5-MATH-0001`
  `G5-MATH-0002`

Difficulty mapping:

- `easy` -> `difficulty_level: 1`
- `medium` -> `difficulty_level: 2`
- `hard` -> `difficulty_level: 3`

Output rules:

- Return a JSON array only.
- Do not include prose before or after the JSON.
- For English, the dataset output remains the question array, while passages are generated and stored separately in the passage directory.
- For Math and Science, generate competency-based standalone questions instead of topic-recognition templates.

Output destination:

`app/data/questions/{grade}/{subject}.json`

Create the destination directory if it does not exist.
