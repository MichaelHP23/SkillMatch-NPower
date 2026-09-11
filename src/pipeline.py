"""End-to-end pipeline: ingest -> normalize -> score -> rank -> export.

Run against the mock data in data/ out of the box:

    python -m src.pipeline

Once real data is available from NPower, point --students / --opportunities
at the real exports -- the normalization/scoring logic doesn't need to change,
only the taxonomy's EXPLICIT_MAP (see src/taxonomy.py) may need extending.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.scoring import rank_opportunities_for_student
from src.taxonomy import normalize_skill_list

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STUDENTS_CSV = PROJECT_ROOT / "data" / "sample_students.csv"
DEFAULT_OPPORTUNITIES_CSV = PROJECT_ROOT / "data" / "sample_opportunities.csv"
DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "output" / "ranked_matches.csv"
DEFAULT_UNMAPPED_CSV = PROJECT_ROOT / "output" / "unmapped_skills.csv"


def _split_skills(cell) -> list[str]:
    if pd.isna(cell):
        return []
    return [s.strip() for s in str(cell).split(";") if s.strip()]


def _normalize_entity_skills(df: pd.DataFrame, id_col: str, skills_col: str):
    """Return ({entity_id: set(canonical_tags)}, [unmapped-skill log rows])."""
    tag_sets: dict[str, set[str]] = {}
    unmapped_rows = []

    for _, row in df.iterrows():
        entity_id = row[id_col]
        results = normalize_skill_list(_split_skills(row[skills_col]))

        tags = set()
        for r in results:
            if r.canonical_tag:
                tags.add(r.canonical_tag)
            else:
                unmapped_rows.append(
                    {"entity_id": entity_id, "raw_skill": r.raw, "cleaned": r.cleaned}
                )
        tag_sets[entity_id] = tags

    return tag_sets, unmapped_rows


def run_pipeline(
    students_csv: Path,
    opportunities_csv: Path,
    output_csv: Path,
    unmapped_csv: Path,
) -> pd.DataFrame:
    students_df = pd.read_csv(students_csv)
    opportunities_df = pd.read_csv(opportunities_csv)

    student_tags, student_unmapped = _normalize_entity_skills(
        students_df, "student_id", "skills"
    )
    opportunity_tags, opp_unmapped = _normalize_entity_skills(
        opportunities_df, "opportunity_id", "required_skills"
    )

    all_rows = []
    for _, srow in students_df.iterrows():
        sid = srow["student_id"]
        for r in rank_opportunities_for_student(sid, student_tags[sid], opportunity_tags):
            opp_title = opportunities_df.loc[
                opportunities_df["opportunity_id"] == r.opportunity_id, "title"
            ].iloc[0]
            all_rows.append(
                {
                    "student_id": r.student_id,
                    "student_name": srow["name"],
                    "opportunity_id": r.opportunity_id,
                    "opportunity_title": opp_title,
                    "match_score": r.score,
                    "matched_skills": "; ".join(r.matched_skills),
                    "missing_skills": "; ".join(r.missing_skills),
                }
            )

    output_df = pd.DataFrame(all_rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_csv, index=False)

    unmapped_df = pd.DataFrame(student_unmapped + opp_unmapped)
    unmapped_csv.parent.mkdir(parents=True, exist_ok=True)
    unmapped_df.to_csv(unmapped_csv, index=False)

    return output_df


def main():
    parser = argparse.ArgumentParser(description="NPower skills-matching pipeline")
    parser.add_argument("--students", type=Path, default=DEFAULT_STUDENTS_CSV)
    parser.add_argument("--opportunities", type=Path, default=DEFAULT_OPPORTUNITIES_CSV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--unmapped", type=Path, default=DEFAULT_UNMAPPED_CSV)
    args = parser.parse_args()

    output_df = run_pipeline(args.students, args.opportunities, args.output, args.unmapped)
    print(f"Wrote {len(output_df)} ranked student-opportunity rows to {args.output}")
    if len(output_df):
        print(f"Unmapped skills (if any) logged to {args.unmapped}")


if __name__ == "__main__":
    main()
