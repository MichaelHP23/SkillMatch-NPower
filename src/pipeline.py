"""End-to-end pipeline: ingest -> normalize -> score -> rank -> export.

Run against the mock data in data/ out of the box:

    python -m src.pipeline

Once real data is available from NPower, point --students / --opportunities
at the real exports -- the normalization/scoring logic doesn't need to change,
only the taxonomy's EXPLICIT_MAP (see src/taxonomy.py) may need extending.

As of the System Architecture pass (weeks 3-4), this loads both CSVs into a
SQLite database (db/schema.sql) and computes matches there via src/db.py,
rather than staying purely in-memory with pandas. The CSV inputs and outputs
are unchanged in shape -- this is what lets the same data also be queried
directly (by the Streamlit app in app.py, or by staff via plain SQL) instead
of only existing as a point-in-time export.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.courses import DEFAULT_COURSES_CSV, load_courses
from src.db import (
    DEFAULT_DB_PATH,
    build_database,
    get_ranked_courses_df,
    get_ranked_matches_df,
    get_unmapped_skills_df,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STUDENTS_CSV = PROJECT_ROOT / "data" / "sample_students.csv"
DEFAULT_OPPORTUNITIES_CSV = PROJECT_ROOT / "data" / "sample_opportunities.csv"
DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "output" / "ranked_matches.csv"
DEFAULT_UNMAPPED_CSV = PROJECT_ROOT / "output" / "unmapped_skills.csv"
DEFAULT_COURSES_OUTPUT_CSV = PROJECT_ROOT / "output" / "ranked_courses.csv"


def run_pipeline(
    students_csv: Path,
    opportunities_csv: Path,
    output_csv: Path,
    unmapped_csv: Path,
    db_path: Path = DEFAULT_DB_PATH,
    courses_csv: Path = DEFAULT_COURSES_CSV,
    courses_output_csv: Path = DEFAULT_COURSES_OUTPUT_CSV,
):
    conn = build_database(students_csv, opportunities_csv, db_path, courses_csv)

    output_df = get_ranked_matches_df(conn)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_csv, index=False)

    unmapped_df = get_unmapped_skills_df(conn)
    unmapped_csv.parent.mkdir(parents=True, exist_ok=True)
    unmapped_df.to_csv(unmapped_csv, index=False)

    # Course side of the pipeline: which courses each student should take next.
    courses_df = get_ranked_courses_df(conn, load_courses(courses_csv))
    courses_output_csv.parent.mkdir(parents=True, exist_ok=True)
    courses_df.to_csv(courses_output_csv, index=False)

    conn.close()
    return output_df


def main():
    parser = argparse.ArgumentParser(description="NPower skills-matching pipeline")
    parser.add_argument("--students", type=Path, default=DEFAULT_STUDENTS_CSV)
    parser.add_argument("--opportunities", type=Path, default=DEFAULT_OPPORTUNITIES_CSV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--unmapped", type=Path, default=DEFAULT_UNMAPPED_CSV)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite file to build/overwrite")
    parser.add_argument("--courses", type=Path, default=DEFAULT_COURSES_CSV, help="NPower course list CSV")
    parser.add_argument("--courses-output", type=Path, default=DEFAULT_COURSES_OUTPUT_CSV)
    args = parser.parse_args()

    output_df = run_pipeline(
        args.students, args.opportunities, args.output, args.unmapped, args.db,
        args.courses, args.courses_output,
    )
    print(f"Wrote {len(output_df)} ranked student-opportunity rows to {args.output}")
    print(f"Wrote course recommendations to {args.courses_output}")
    print(f"Database written to {args.db}")
    if len(output_df):
        print(f"Unmapped skills (if any) logged to {args.unmapped}")


if __name__ == "__main__":
    main()
