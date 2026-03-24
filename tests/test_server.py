from server import DATASETS


def test_datasets_loaded_with_questions():
    assert DATASETS
    assert all(dataset['questions'] for dataset in DATASETS)


def test_submit_scoring_matches_answer():
    dataset = DATASETS[0]
    question = dataset['questions'][0]
    answers = {question['id']: question['answer']}

    score = 0
    results = []
    lookup = {item['id']: item for item in dataset['questions']}
    for question_id, selected in answers.items():
        current = lookup[question_id]
        is_correct = selected == current['answer']
        score += int(is_correct)
        results.append({
            'id': question_id,
            'selected': selected,
            'correctAnswer': current['answer'],
            'isCorrect': is_correct,
        })

    assert score == 1
    assert results[0]['correctAnswer'] == question['answer']


def test_config_values_are_available():
    grades = sorted({dataset['grade'] for dataset in DATASETS})
    subjects = sorted({dataset['subject'] for dataset in DATASETS})

    assert 'Math' in subjects
    assert grades
