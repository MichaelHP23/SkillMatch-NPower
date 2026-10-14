import pandas as pd
import pytest

from src.db import (
    build_database,
    get_ranked_matches_df,
    get_unmapped_skills_df,
    get_connection,
    init_schema,
    load_opportunities,
    load_students,
    refresh_matches,
    seed_taxonomy,
    to_safe_csv,
)
from src.taxonomy import CANONICAL_TAGS, EXPLICIT_MAP

STUDENTS_CSV = "data/sample_students.csv"
OPPORTUNITIES_CSV = "data/sample_opportunities.csv"


@pytest.fixture
def conn(tmp_path):
    c = get_connection(tmp_path / "test.db")
    init_schema(c)
    yield c
    c.close()


def test_seed_taxonomy_populates_canonical_tags_and_map(conn):
    seed_taxonomy(conn)
    tag_count = conn.execute("SELECT COUNT(*) AS n FROM canonical_tags").fetchone()["n"]
    map_count = conn.execute("SELECT COUNT(*) AS n FROM taxonomy_map").fetchone()["n"]
    assert tag_count == len(CANONICAL_TAGS)
    assert map_count == len(EXPLICIT_MAP)


def test_load_students_normalizes_messy_skill_variants(conn):
    seed_taxonomy(conn)
    students = pd.DataFrame(
        [{"student_id": "S1", "name": "Test Student", "skills": "A+ Certification; comptia a plus"}]
    )
    load_students(conn, students)

    rows = conn.execute(
        "SELECT raw_skill, tag, matched_via FROM student_skills WHERE student_id = 'S1'"
    ).fetchall()
    assert len(rows) == 2
    assert all(r["tag"] == "CompTIA A+" for r in rows)
    assert all(r["matched_via"] == "explicit" for r in rows)


def test_refresh_matches_computes_expected_score(conn):
    seed_taxonomy(conn)
    students = pd.DataFrame([{"student_id": "S1", "name": "A", "skills": "A+; Excel"}])
    opportunities = pd.DataFrame(
        [{"opportunity_id": "O1", "partner_org": "Acme", "title": "Role", "required_skills": "A+; Excel; Network+"}]
    )
    load_students(conn, students)
    load_opportunities(conn, opportunities)
    refresh_matches(conn)

    match = conn.execute(
        "SELECT score FROM matches WHERE student_id = 'S1' AND opportunity_id = 'O1'"
    ).fetchone()
    # score_match() rounds to 4 decimals (see src/scoring.py), so compare
    # against that same rounded value rather than the raw fraction.
    assert match["score"] == pytest.approx(round(2 / 3, 4))

    statuses = {
        row["tag"]: row["matched"]
        for row in conn.execute(
            "SELECT tag, matched FROM match_skill_status WHERE student_id = 'S1' AND opportunity_id = 'O1'"
        )
    }
    assert statuses == {"CompTIA A+": 1, "Microsoft Excel": 1, "CompTIA Network+": 0}


def test_unmapped_skill_appears_in_view(conn):
    seed_taxonomy(conn)
    students = pd.DataFrame([{"student_id": "S1", "name": "A", "skills": "Underwater Basket Weaving"}])
    opportunities = pd.DataFrame(
        [{"opportunity_id": "O1", "partner_org": "Acme", "title": "Role", "required_skills": "CompTIA A+"}]
    )
    load_students(conn, students)
    load_opportunities(conn, opportunities)

    unmapped = get_unmapped_skills_df(conn)
    assert list(unmapped["raw_skill"]) == ["Underwater Basket Weaving"]
    assert list(unmapped["entity_id"]) == ["S1"]
    assert list(unmapped["entity_name"]) == ["A"]


def test_build_database_matches_pipeline_row_count(tmp_path):
    conn = build_database(STUDENTS_CSV, OPPORTUNITIES_CSV, tmp_path / "full.db")
    df = get_ranked_matches_df(conn)
    conn.close()
    # 6 students x 5 opportunities, per data/sample_*.csv
    assert len(df) == 30


def test_refresh_matches_is_deterministic(tmp_path):
    conn = build_database(STUDENTS_CSV, OPPORTUNITIES_CSV, tmp_path / "det.db")
    first = get_ranked_matches_df(conn).sort_values(["student_id", "opportunity_id"]).reset_index(drop=True)
    refresh_matches(conn)
    second = get_ranked_matches_df(conn).sort_values(["student_id", "opportunity_id"]).reset_index(drop=True)
    conn.close()
    pd.testing.assert_frame_equal(first, second)


def test_ranked_matches_carry_ids_and_names(tmp_path):
    conn = build_database(STUDENTS_CSV, OPPORTUNITIES_CSV, tmp_path / "cols.db")
    df = get_ranked_matches_df(conn)
    conn.close()
    for col in ["student_id", "student_name", "opportunity_id", "opportunity_title", "partner_org"]:
        assert col in df.columns
        assert df[col].notna().all()


def _write_csvs(tmp_path, students_rows, students_columns=("student_id", "name", "skills")):
    students_csv = tmp_path / "students.csv"
    pd.DataFrame(students_rows, columns=list(students_columns)).to_csv(students_csv, index=False)
    return students_csv


def test_build_database_rejects_missing_column(tmp_path):
    students_csv = _write_csvs(tmp_path, [["S1", "A"]], students_columns=("student_id", "name"))
    with pytest.raises(ValueError, match="skills"):
        build_database(students_csv, OPPORTUNITIES_CSV, tmp_path / "bad.db")
    # Nothing was loaded, so no database file should be left behind.
    assert not (tmp_path / "bad.db").exists()


def test_build_database_rejects_duplicate_student_id(tmp_path):
    students_csv = _write_csvs(tmp_path, [["S1", "A", "A+"], ["S1", "B", "Excel"]])
    with pytest.raises(ValueError, match="S1"):
        build_database(students_csv, OPPORTUNITIES_CSV, tmp_path / "dupe.db")


def test_build_database_rejects_blank_name(tmp_path):
    students_csv = _write_csvs(tmp_path, [["S1", None, "A+"]])
    with pytest.raises(ValueError, match="name"):
        build_database(students_csv, OPPORTUNITIES_CSV, tmp_path / "blank.db")


def test_to_safe_csv_neutralizes_spreadsheet_formulas():
    df = pd.DataFrame([{"student_name": "=HYPERLINK(\"http://x\")", "match_score": -0.5, "note": "A+"}])
    lines = to_safe_csv(df).splitlines()
    assert lines[1].startswith("'=HYPERLINK") or lines[1].startswith("\"'=HYPERLINK")
    # Numbers and ordinary text are left alone.
    assert "-0.5" in lines[1]
    assert lines[1].endswith(",A+")
