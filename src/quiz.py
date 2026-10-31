"""Practice aptitude exam a student can take before enrolling. Advisory
only: it never blocks a recommendation, and attempts are not saved
anywhere (kept in the Streamlit session only).

Added at Robert's (NPower) request. Per his feedback, this is one exam
covering all course offerings (he suggested 20-30 questions) to gauge
technical aptitude, rather than a separate quiz per course.

PLACEHOLDER CONTENT: the questions below are sample questions written for
this prototype, not real certification material. NPower plans to write
the real exam; replace EXAM with it once it is available (same as the mock
data in data/sample_students.csv).
"""
from __future__ import annotations

# A score at or above this fraction counts as "looks like a good fit".
READY_THRESHOLD = 0.7

EXAM: list[dict] = [
    # Basic computer skills
    {
        "question": "What is a web browser used for?",
        "choices": ["Editing photos", "Viewing websites", "Writing code only", "Storing files offline"],
        "correct_choice_index": 1,
    },
    {
        "question": "Which keyboard shortcut usually copies selected text?",
        "choices": ["Ctrl + V", "Ctrl + X", "Ctrl + C", "Ctrl + Z"],
        "correct_choice_index": 2,
    },
    {
        "question": "What is the safest way to handle a password?",
        "choices": [
            "Use the same one everywhere",
            "Write it on a sticky note",
            "Use a unique one for each account",
            "Share it with coworkers",
        ],
        "correct_choice_index": 2,
    },
    {
        "question": "Which of these is an email attachment most likely to be?",
        "choices": ["A file sent along with the message", "The subject line", "The sender's address", "A reply"],
        "correct_choice_index": 0,
    },
    {
        "question": "What does saving a file do?",
        "choices": [
            "Deletes it",
            "Stores your changes so they are kept",
            "Sends it to someone",
            "Prints it",
        ],
        "correct_choice_index": 1,
    },
    # Hardware and operating systems (CompTIA A+ level)
    {
        "question": "Which part of a computer does most of the processing?",
        "choices": ["RAM", "CPU", "Hard drive", "Power supply"],
        "correct_choice_index": 1,
    },
    {
        "question": "What happens to data in RAM when the computer turns off?",
        "choices": ["It is saved", "It is lost", "It moves to the CPU", "It is backed up online"],
        "correct_choice_index": 1,
    },
    {
        "question": "Which Windows tool shows running programs and lets you end one that is frozen?",
        "choices": ["Control Panel", "File Explorer", "Task Manager", "Paint"],
        "correct_choice_index": 2,
    },
    {
        "question": "A user's computer won't turn on at all. What should you check first?",
        "choices": ["The power cable and outlet", "The monitor settings", "The Wi-Fi password", "The printer"],
        "correct_choice_index": 0,
    },
    {
        "question": "Which of these is an operating system?",
        "choices": ["Microsoft Word", "Google Chrome", "Windows 11", "Adobe Reader"],
        "correct_choice_index": 2,
    },
    # Networking (CompTIA Network+ level)
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
    # Cloud (AWS Cloud Practitioner level)
    {
        "question": "Which AWS service stores files (objects) in buckets?",
        "choices": ["EC2", "S3", "RDS", "Lambda"],
        "correct_choice_index": 1,
    },
    {
        "question": "Which AWS service provides virtual servers?",
        "choices": ["S3", "IAM", "EC2", "CloudFront"],
        "correct_choice_index": 2,
    },
    {
        "question": "What does IAM control?",
        "choices": ["Who can access which AWS resources", "Website speed", "Database backups", "Billing currency"],
        "correct_choice_index": 0,
    },
    {
        "question": "What is a main benefit of cloud computing's pay-as-you-go pricing?",
        "choices": [
            "You buy all hardware up front",
            "You pay only for what you use",
            "Prices never change",
            "It is always free",
        ],
        "correct_choice_index": 1,
    },
    {
        "question": "What is an AWS Region?",
        "choices": [
            "A single server",
            "A geographic area with multiple data centers",
            "A type of database",
            "A billing account",
        ],
        "correct_choice_index": 1,
    },
]


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
