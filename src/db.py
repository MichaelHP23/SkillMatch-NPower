"""SQLite persistence layer for the skills-matching pipeline.

taxonomy.py and scoring.py stay pure, DB-free modules (simple to unit test
in isolation); this module is the only place that touches SQLite. It seeds
the taxonomy tables from taxonomy.py's constants, loads student/opportunity
CSVs into normalized tables (db/schema.sql), and computes + stores match
results so they can be queried directly -- by the Streamlit app, or by
staff via plain SQL -- instead of only existing as a point-in-time CSV.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.scoring import score_match
from src.taxonomy import CANONICAL_TAGS, EXPLICIT_MAP, normalize_skill_list

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"
DEFAULT_DB_PATH = PROJECT_ROOT / "db" / "skills_match.db"


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection, schema_path: Path = SCHEMA_PATH) -> None:
    conn.executescript(schema_path.read_text())
    conn.commit()


def seed_taxonomy(conn: sqlite3.Connection) -> None:
    """Mirror taxonomy.py's CANONICAL_TAGS / EXPLICIT_MAP into the DB.

    taxonomy.py stays the source of truth for now (see the "future work"
    note in docs/week-03-04-system-architecture.md); this just keeps the
    DB's copy in sync every time the pipeline runs, so it's queryable
    alongside the data it produced.
    """
    conn.executemany(
        "INSERT OR IGNORE INTO canonical_tags (tag) VALUES (?)",
        [(tag,) for tag in CANONICAL_TAGS],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO taxonomy_map (raw_cleaned, tag) VALUES (?, ?)",
        list(EXPLICIT_MAP.items()),
    )
    conn.commit()


def _split_skills(cell) -> list[str]:
    if pd.isna(cell):
        return []
    return [s.strip() for s in str(cell).split(";") if s.strip()]


def load_students(conn: sqlite3.Connection, students_df: pd.DataFrame) -> None:
    conn.execute("DELETE FROM student_skills")
    conn.execute("DELETE FROM students")
    for _, row in students_df.iterrows():
        conn.execute(
            "INSERT INTO students (student_id, name) VALUES (?, ?)",
            (row["student_id"], row["name"]),
        )
        for r in normalize_skill_list(_split_skills(row["skills"])):
            conn.execute(
                """INSERT INTO student_skills
                   (student_id, raw_skill, cleaned, tag, matched_via, fuzzy_score)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (row["student_id"], r.raw, r.cleaned, r.canonical_tag, r.matched_via, r.fuzzy_score),
            )
    conn.commit()


def load_opportunities(conn: sqlite3.Connection, opportunities_df: pd.DataFrame) -> None:
    conn.execute("DELETE FROM opportunity_requirements")
    conn.execute("DELETE FROM opportunities")
    for _, row in opportunities_df.iterrows():
        conn.execute(
            "INSERT INTO opportunities (opportunity_id, partner_org, title) VALUES (?, ?, ?)",
            (row["opportunity_id"], row.get("partner_org"), row["title"]),
        )
        for r in normalize_skill_list(_split_skills(row["required_skills"])):
            conn.execute(
                """INSERT INTO opportunity_requirements
                   (opportunity_id, raw_skill, cleaned, tag, matched_via, fuzzy_score)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (row["opportunity_id"], r.raw, r.cleaned, r.canonical_tag, r.matched_via, r.fuzzy_score),
            )
    conn.commit()


def _tag_set(conn: sqlite3.Connection, table: str, id_col: str, entity_id: str) -> set[str]:
    rows = conn.execute(
        f"SELECT DISTINCT tag FROM {table} WHERE {id_col} = ? AND tag IS NOT NULL",
        (entity_id,),
    ).fetchall()
    return {r["tag"] for r in rows}


def refresh_matches(conn: sqlite3.Connection) -> None:
    """Recompute every student-opportunity match from whatever is currently
    loaded into student_skills / opportunity_requirements. Safe to call
    repeatedly (FR-16, determinism) -- clears and rebuilds matches and
    match_skill_status from scratch every time, rather than patching them.
    """
    conn.execute("DELETE FROM match_skill_status")
    conn.execute("DELETE FROM matches")

    student_ids = [r["student_id"] for r in conn.execute("SELECT student_id FROM students")]
    opportunity_ids = [r["opportunity_id"] for r in conn.execute("SELECT opportunity_id FROM opportunities")]

    opp_tags = {
        oid: _tag_set(conn, "opportunity_requirements", "opportunity_id", oid)
        for oid in opportunity_ids
    }

    for sid in student_ids:
        s_tags = _tag_set(conn, "student_skills", "student_id", sid)
        for oid in opportunity_ids:
            result = score_match(sid, oid, s_tags, opp_tags[oid])
            conn.execute(
                "INSERT INTO matches (student_id, opportunity_id, score) VALUES (?, ?, ?)",
                (sid, oid, result.score),
            )
            for tag in result.matched_skills:
                conn.execute(
                    """INSERT INTO match_skill_status
                       (student_id, opportunity_id, tag, matched) VALUES (?, ?, ?, 1)""",
                    (sid, oid, tag),
                )
            for tag in result.missing_skills:
                conn.execute(
                    """INSERT INTO match_skill_status
                       (student_id, opportunity_id, tag, matched) VALUES (?, ?, ?, 0)""",
                    (sid, oid, tag),
                )
    conn.commit()


def get_ranked_matches_df(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM ranked_matches", conn)


def get_unmapped_skills_df(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM unmapped_skills", conn)


def build_database(
    students_csv: Path,
    opportunities_csv: Path,
    db_path: Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    """End-to-end: fresh DB file, schema, taxonomy seed, load both CSVs,
    compute matches. This is what pipeline.py and the Streamlit app call."""
    if db_path.exists():
        db_path.unlink()
    conn = get_connection(db_path)
    init_schema(conn)
    seed_taxonomy(conn)
    load_students(conn, pd.read_csv(students_csv))
    load_opportunities(conn, pd.read_csv(opportunities_csv))
    refresh_matches(conn)
    return conn
