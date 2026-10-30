from src.quiz import QUIZZES, score_quiz
from src.taxonomy import CANONICAL_TAGS


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


def test_quiz_tags_are_canonical_and_answers_are_valid():
    for tag, questions in QUIZZES.items():
        assert tag in CANONICAL_TAGS
        for question in questions:
            assert 0 <= question["correct_choice_index"] < len(question["choices"])
