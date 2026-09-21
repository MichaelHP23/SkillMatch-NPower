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
