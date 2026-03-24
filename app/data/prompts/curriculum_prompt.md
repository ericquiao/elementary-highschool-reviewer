You are extracting curriculum topics for the Student Reviewer App dataset pipeline.

Input parameters:

Grade: {grade}
Subject: {subject}

Primary source priority:

1. DepEd official learning competencies
2. Philippine K-12 curriculum guides
3. DepEd LRMDS materials
4. International curriculum standards only as secondary support

Goal:

Extract the core competency-level topics students in Grade {grade} must master in {subject} before moving to the next grade level.

Topic extraction rules:

- Use DepEd-aligned competencies as the primary basis.
- Prefer narrow learning competencies instead of broad chapter names.
- Avoid overlapping or redundant topics.
- Use short, clear, curriculum-friendly titles.
- Let the final topic count be determined by actual curriculum coverage.
- Prefer language that would be understandable in a dataset pipeline and review app.

Examples of good topics:

- "Comparing and Ordering Decimals"
- "Adding and Subtracting Fractions with Unlike Denominators"
- "Interactions in Estuaries and Intertidal Zones"

Examples to avoid:

- "Decimals"
- "Fractions"
- "Living Things"

Output requirements:

- Return JSON only.
- The response must be a single JSON array of strings.
- Do not include notes, headings, bullets, or explanations outside the JSON.

Output format example:

```json
[
  "Topic 1",
  "Topic 2",
  "Topic 3"
]
```

Output destination:

`app/data/topics/{grade}/{subject}_topics.json`

Create the directory if it does not exist.
