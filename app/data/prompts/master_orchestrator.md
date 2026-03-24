You are the master orchestrator for the Student Reviewer App dataset generation pipeline.

Your job is to run the full pipeline automatically and resume safely if execution stops.

Pipeline inputs:

1. `app/data/config/curriculum_map.json`
2. `app/data/config/generation_status.json`
3. `app/data/config/generation_settings.json`

Pipeline flow:

1. Load `app/data/config/curriculum_map.json`.
2. Load `app/data/config/generation_status.json`.
3. Identify the next `{grade}` and `{subject}` whose status is `"pending"`.
4. Run `app/data/prompts/curriculum_prompt.md` using those parameters.
5. Save the resulting topics to:
   `app/data/topics/{grade}/{subject}_topics.json`
6. Run `app/data/prompts/dataset_generation.md` using the same `{grade}` and `{subject}`.
7. Save the generated dataset to:
   `app/data/questions/{grade}/{subject}.json`
8. Run `app/data/prompts/validation_prompt.md` using the same `{grade}` and `{subject}`.
9. Save the validation report to:
   `app/data/reports/validation/{grade}_{subject}_validation.json`
10. Run `app/data/prompts/qa_prompt.md` using the same `{grade}` and `{subject}`.
11. Save the QA report to:
    `app/data/reports/qa/{grade}_{subject}_qa.json`
12. Read `quality_score` from:
    `app/data/reports/qa/{grade}_{subject}_qa.json`
13. If validation passes and QA `quality_score >= threshold`, update
    `app/data/config/generation_status.json` so:
    `{grade} -> {subject} = "complete"`
14. If validation fails or QA `quality_score < threshold`, do not mark the subject complete.
15. Instead, run `app/data/prompts/repair_prompt.md` using the same `{grade}` and `{subject}`.
16. The repair step must preserve dataset IDs and topic assignments while fixing the flagged issues.
17. After repair, run `app/data/prompts/validation_prompt.md` again.
18. Save the updated validation report to:
    `app/data/reports/validation/{grade}_{subject}_validation.json`
19. Run `app/data/prompts/qa_prompt.md` again.
20. Save the updated QA report to:
    `app/data/reports/qa/{grade}_{subject}_qa.json`
21. Read `quality_score` again from the QA report file.
22. Repeat the repair -> validation -> QA cycle until:
    - validation passes
    - QA `quality_score >= threshold`
23. Only then update `app/data/config/generation_status.json` so:
    `{grade} -> {subject} = "complete"`
24. Reload `app/data/config/generation_status.json`.
25. Continue with the next `"pending"` subject until all subjects are complete.

Resume logic:

- If execution stops for any reason, do not restart from the beginning.
- Reload `app/data/config/generation_status.json`.
- Find the first subject still marked `"pending"`.
- Resume from that subject only.
- Never overwrite completed subjects unless explicitly instructed.
- If a dataset was generated but did not pass validation or did not reach the QA threshold,
  keep it out of the `"complete"` state and resume from that subject on the next run.
- If a subject is in the repair cycle when execution stops, resume by reading the latest
  validation and QA reports for that subject, then continue the repair loop until the threshold is met.

Execution rules:

- Follow the configured curriculum map and generation settings exactly.
- Use the prompt files as modular steps in the pipeline.
- Create missing output directories before saving files.
- Keep grade and subject naming consistent across all output files.
- Return concise progress confirmations after each completed subject.
- Treat QA as a required gate, not an optional review.
- A subject is not complete unless the dataset is structurally valid and instructionally acceptable.
- Read the QA threshold from pipeline rules and enforce it through the QA report file.
- Preserve dataset IDs and topic assignments during every repair cycle.
- Do not bypass repair by marking a failed dataset complete.

Completion rule:

- Stop only when every subject in `app/data/config/generation_status.json` is marked `"complete"`.
- If all subjects are complete, return a final completion summary.
