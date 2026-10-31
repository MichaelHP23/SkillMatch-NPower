from src.quiz import EXAM, score_quiz


def test_score_quiz_computes_fraction_correct():
    questions = [
        {"question": "Q1", "choices": ["a", "b"], "correct_choice_index": 0},
        {"question": "Q2", "choices": ["a", "b"], "correct_choice_index": 1},
        {"question": "Q3", "choices": ["a", "b"], "correct_choice_index": 1},
    ]

    # Q1 right, Q2 wrong, Q3 left blank.
    assert score_quiz(questions, [0, 0, None]) == round(1 / 3, 4)
    assert score_quiz(questions, [0, 1, 1]) == 1.0


def test_score_quiz_handles_no_questions():
    assert score_quiz([], []) == 0.0


def test_exam_is_robert_sized_and_answers_are_valid():
    # Robert asked for one exam of roughly 20-30 questions.
    assert 20 <= len(EXAM) <= 30
    for question in EXAM:
        assert 0 <= question["correct_choice_index"] < len(question["choices"])
