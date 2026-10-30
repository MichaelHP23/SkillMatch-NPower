"""Practice readiness quiz a student can take before enrolling in a
recommended course. Advisory only: it never blocks a recommendation, and
attempts are not saved anywhere (kept in the Streamlit session only).

Added at Robert's (NPower) request. There is one quiz for now, keyed by
canonical tag from src/taxonomy.py.

PLACEHOLDER CONTENT: the questions below are sample questions written for
this prototype, not real CompTIA certification material. Replace them with
real material from NPower once it is available (same as the mock data in
data/sample_students.csv).
"""
from __future__ import annotations

# A score at or above this fraction counts as "looks like a good fit".
READY_THRESHOLD = 0.7

QUIZZES: dict[str, list[dict]] = {
    "CompTIA Network+": [
        {
            "question": "Which device forwards traffic between different networks using IP addresses?",
            "choices": ["Switch", "Router", "Hub", "Repeater"],
            "correct_choice_index": 1,
        },
        {
            "question": "How many layers does the OSI model have?",
            "choices": ["4", "5", "7", "9"],
            "correct_choice_index": 2,
        },
        {
            "question": "Which protocol automatically gives a computer an IP address on a network?",
            "choices": ["DNS", "DHCP", "FTP", "SMTP"],
            "correct_choice_index": 1,
        },
        {
            "question": "What does DNS do?",
            "choices": [
                "Encrypts web traffic",
                "Turns domain names into IP addresses",
                "Assigns MAC addresses",
                "Blocks unwanted traffic",
            ],
            "correct_choice_index": 1,
        },
        {
            "question": "Which of these is a private IPv4 address?",
            "choices": ["8.8.8.8", "192.168.1.10", "172.217.0.1", "1.1.1.1"],
            "correct_choice_index": 1,
        },
        {
            "question": "Which port does HTTPS use by default?",
            "choices": ["21", "25", "80", "443"],
            "correct_choice_index": 3,
        },
    ],
}


def score_quiz(questions: list[dict], answers: list[int | None]) -> float:
    """Fraction of questions answered correctly, 0-1. answers[i] is the
    chosen choice index for questions[i], or None if left blank."""
    if not questions:
        return 0.0
    correct = sum(
        1
        for question, answer in zip(questions, answers)
        if answer == question["correct_choice_index"]
    )
    return round(correct / len(questions), 4)
