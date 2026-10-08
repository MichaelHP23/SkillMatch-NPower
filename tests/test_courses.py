import pandas as pd

from src.courses import build_timeline, courses_teaching, load_courses, rank_courses, split_list
from src.db import build_database, get_ranked_courses_df, get_student_tags, get_unmapped_skills_df

STUDENTS_CSV = "data/sample_students.csv"
OPPORTUNITIES_CSV = "data/sample_opportunities.csv"

# A tiny made-up course list so the tests don't depend on data/courses.csv.
COURSES = [
    {"course_id": "T1", "name": "Intro", "weeks": 10, "prerequisites": set(),
     "skills_taught": {"CompTIA A+"}},
    {"course_id": "T2", "name": "Networking", "weeks": 8, "prerequisites": {"CompTIA A+"},
     "skills_taught": {"CompTIA Network+"}},
    {"course_id": "T3", "name": "Security", "weeks": 6, "prerequisites": {"CompTIA Network+"},
     "skills_taught": {"CompTIA Security+"}},
]


def test_every_skill_in_courses_csv_is_in_the_taxonomy():
    df = pd.read_csv("data/courses.csv")
    courses = load_courses()
    assert len(courses) == len(df)
    for (_, row), course in zip(df.iterrows(), courses):
        assert len(course["skills_taught"]) == len(split_list(row["skills_taught"])), row["name"]
        assert len(course["prerequisites"]) == len(split_list(row["prerequisites"])), row["name"]


def test_rank_courses_puts_ready_advanced_course_first():
    ranked = rank_courses({"CompTIA A+"}, [], COURSES)
    # T1 teaches nothing new, T2 is fully ready, T3 is missing its prerequisite.
    assert [r["course_id"] for r in ranked] == ["T2", "T3"]
    assert ranked[0]["readiness_score"] == 1.0
    assert ranked[1]["readiness_score"] == 0.0
    assert ranked[1]["prerequisites_missing"] == ["CompTIA Network+"]


def test_rank_courses_skips_completed_courses():
    ranked = rank_courses(set(), ["T1"], COURSES)
    assert "T1" not in [r["course_id"] for r in ranked]


def test_courses_teaching_lists_course_names():
    assert courses_teaching("CompTIA Network+", COURSES) == ["Networking"]
    assert courses_teaching("SQL", COURSES) == []


def test_timeline_adds_prerequisite_courses_in_order():
    steps, still_missing = build_timeline(set(), ["CompTIA Security+"], COURSES)
    assert [s["course_id"] for s in steps] == ["T1", "T2", "T3"]
    assert [(s["start_week"], s["end_week"]) for s in steps] == [(1, 10), (11, 18), (19, 24)]
    assert still_missing == []


def test_timeline_reports_skills_no_course_teaches():
    steps, still_missing = build_timeline({"CompTIA A+"}, ["CompTIA Network+", "SQL"], COURSES)
    assert [s["course_id"] for s in steps] == ["T2"]
    assert still_missing == ["SQL"]


def test_timeline_is_empty_when_nothing_is_missing():
    steps, still_missing = build_timeline({"CompTIA A+"}, ["CompTIA A+"], COURSES)
    assert steps == []
    assert still_missing == []


def test_completed_course_adds_its_skills_to_the_student(tmp_path):
    conn = build_database(STUDENTS_CSV, OPPORTUNITIES_CSV, tmp_path / "c.db")
    tags = get_student_tags(conn)
    ranked = get_ranked_courses_df(conn, load_courses())
    conn.close()
    # S004 lists "AWS Cloud Practitioner" as a completed course, not as a skill.
    assert "AWS Cloud Practitioner" in tags["S004"]
    s004 = ranked[ranked["student_id"] == "S004"]
    assert "C07" not in list(s004["course_id"])
    # Finishing C07 is what makes S004 ready for the advanced AWS course.
    aws_sa = s004[s004["course_id"] == "C08"].iloc[0]
    assert aws_sa["readiness_score"] == 1.0
    assert aws_sa["prerequisites_met"] == "AWS Cloud Practitioner"


def test_unknown_completed_course_is_reported_as_unmapped(tmp_path):
    students_csv = tmp_path / "students.csv"
    students_csv.write_text("student_id,name,skills,completed_courses\nS1,A,A+,Basket Weaving 101\n")
    conn = build_database(students_csv, OPPORTUNITIES_CSV, tmp_path / "u.db")
    unmapped = get_unmapped_skills_df(conn)
    conn.close()
    assert list(unmapped["raw_skill"]) == ["course: Basket Weaving 101"]
