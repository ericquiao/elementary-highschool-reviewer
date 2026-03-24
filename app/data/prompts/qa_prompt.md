You are performing quality assurance on a generated question dataset for a student reviewer system.

Input parameters:

Grade: {grade}
Subject: {subject}

Dataset location:

app/data/questions/{grade}/{subject}.json

---

Sampling rule

Randomly sample 50 questions for every grade of every subject from the dataset.

Do not modify the dataset during this QA step.

---

QA checks

1. Answer Integrity

Verify that correct_answer exists inside choices[].

Flag any questions where:

* correct_answer is missing from choices
* choices contain duplicates
* choices are empty

---

2. Duplicate Detection

Detect:

* exact duplicates
* near duplicates
* template duplicates

---

3. Difficulty Alignment

Verify that difficulty labels match question complexity.

easy → recall or single-step
medium → multi-step reasoning
hard → complex reasoning

---

4. Topic Alignment

Verify the question belongs to the assigned topic.

---

5. Ambiguity Check

Detect questions where:

* multiple answers may be correct
* wording is unclear

---

Output report location:

app/data/reports/qa/{grade}_{subject}_qa.json

---

Report structure

{
"dataset": "",
"sample_size": 50,
"issues_found": {
"answer_integrity": [],
"duplicates": [],
"difficulty_mismatch": [],
"topic_mismatch": [],
"ambiguity": []
},
"quality_score": ""
}

---

Quality score guideline

90–100 → excellent
75–89 → good
60–74 → moderate revision recommended
<60 → regenerate dataset
