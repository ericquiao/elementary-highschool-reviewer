# Elementary & High School Reviewer

Simple study app with a lightweight Python backend API and a plain HTML/CSS/JS frontend.

## Features

- Home page with selectors for grade, subject, and mode.
- Review mode with instant feedback.
- Exam mode with score summary.
- Result page that shows correct answers and explanations.
- Mobile-friendly layout with minimal styling.

## Run locally

```bash
python3 server.py
```

Then open <http://127.0.0.1:8000>.

## API endpoints

- `GET /api/config` returns grade, subject, and mode options.
- `GET /api/questions?grade=...&subject=...&mode=...` returns quiz questions.
- `POST /api/submit` scores answers and returns result details.

## Existing utilities

### Validator

```bash
python3 validator.py < questions.json
```

### Processor

```bash
python3 processor.py < some-array.json
```
