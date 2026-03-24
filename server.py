#!/usr/bin/env python3
import json
import random
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / 'frontend'
DATA_FILES = [ROOT / 'questions.json', ROOT / 'grade5_6_math_mcq.json']


def load_datasets():
    datasets = []
    for path in DATA_FILES:
        raw = json.loads(path.read_text())
        questions = []
        for item in raw.get('questions', []):
            choices = item.get('choices') or item.get('options') or []
            questions.append({
                'id': f"{path.stem}-{item.get('id')}",
                'topic': item.get('topic', 'General'),
                'question': item.get('question', ''),
                'choices': choices,
                'answer': item.get('answer', ''),
                'explanation': item.get('explanation', ''),
                'difficulty': item.get('difficulty', 'medium'),
            })

        grade = str(raw.get('grade') or raw.get('grade_band') or '')
        datasets.append({
            'id': path.stem,
            'label': path.stem.replace('_', ' ').title(),
            'grade': grade,
            'subject': raw.get('subject', 'General'),
            'topics': raw.get('topics', []),
            'questions': questions,
        })
    return datasets


DATASETS = load_datasets()


class ReviewRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/config':
            config = {
                'grades': sorted({dataset['grade'] for dataset in DATASETS}),
                'subjects': sorted({dataset['subject'] for dataset in DATASETS}),
                'modes': ['review', 'exam'],
            }
            return self._send_json(config)

        if parsed.path == '/api/questions':
            params = parse_qs(parsed.query)
            grade = params.get('grade', [''])[0]
            subject = params.get('subject', [''])[0]
            mode = params.get('mode', ['review'])[0]

            dataset = next(
                (
                    item for item in DATASETS
                    if (not grade or item['grade'] == grade) and (not subject or item['subject'].lower() == subject.lower())
                ),
                DATASETS[0],
            )
            questions = list(dataset['questions'])
            if mode == 'exam':
                random.shuffle(questions)
                questions = questions[: min(len(questions), 10)]

            payload = {
                'dataset': {
                    'id': dataset['id'],
                    'grade': dataset['grade'],
                    'subject': dataset['subject'],
                    'topics': dataset['topics'],
                },
                'questions': [
                    {
                        'id': question['id'],
                        'topic': question['topic'],
                        'question': question['question'],
                        'choices': question['choices'],
                        'answer': question['answer'],
                        'explanation': question['explanation'],
                    }
                    for question in questions
                ],
            }
            return self._send_json(payload)

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/submit':
            return self._send_json({'error': 'Not found'}, status=HTTPStatus.NOT_FOUND)

        payload = self._read_json()
        dataset_id = payload.get('datasetId')
        answers = payload.get('answers', {})
        dataset = next((item for item in DATASETS if item['id'] == dataset_id), DATASETS[0])
        lookup = {item['id']: item for item in dataset['questions']}

        results = []
        score = 0
        for question_id, selected in answers.items():
            question = lookup.get(question_id)
            if not question:
                continue
            is_correct = selected == question['answer']
            score += int(is_correct)
            results.append({
                'id': question_id,
                'question': question['question'],
                'selected': selected,
                'correctAnswer': question['answer'],
                'explanation': question['explanation'],
                'isCorrect': is_correct,
            })

        return self._send_json({
            'score': score,
            'total': len(results),
            'results': results,
        })


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8000), ReviewRequestHandler)
    print('Serving on http://127.0.0.1:8000')
    server.serve_forever()
