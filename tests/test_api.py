from fastapi.testclient import TestClient

from app import app, repository

client = TestClient(app)


def test_questions_endpoint_filters_by_subject_and_difficulty():
    response = client.get('/questions', params={'subject': 'Math', 'difficulty': 'easy'})
    assert response.status_code == 200
    data = response.json()
    assert data['count'] > 0
    assert all(item['subject'] == 'Math' for item in data['questions'])
    assert all(item['difficulty'] == 'easy' for item in data['questions'])


def test_topics_endpoint_returns_nested_grade_and_subject_map():
    response = client.get('/topics')
    assert response.status_code == 200
    data = response.json()
    assert '5' in data or '6' in data
    assert any('Math' in subjects for subjects in data.values())


def test_submit_endpoint_scores_answers_and_returns_explanations():
    question = repository.get_questions(subject='Math')[0]
    wrong_choice = next(choice['text'] for choice in question['choices'] if not choice['is_correct'])

    response = client.post(
        '/submit',
        json={
            'answers': [
                {'question_id': question['id'], 'answer': question['answer']},
                {'question_id': question['id'], 'answer': wrong_choice},
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['score'] == 1
    assert data['total'] == 2
    assert data['results'][0]['is_correct'] is True
    assert data['results'][1]['is_correct'] is False
    assert data['results'][1]['correct_answer'] == question['answer']
    assert data['results'][1]['explanation']
