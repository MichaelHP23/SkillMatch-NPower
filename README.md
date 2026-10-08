# NPower Skills-Matching Tool

CISC 4900 capstone project. A skills-matching tool that pairs NPower
students with NPower's partner internship/apprenticeship/job opportunities,
based on completed coursework and certifications versus each opportunity's
stated requirements.

## The problem

NPower staff currently match students to partner opportunities by hand.
Student skill data and partner requirements are both recorded in free text,
so the same skill can appear as "A+", "CompTIA A+", or "CompTIA A+
Certification" across different records. There's no automated way to
reconcile that and surface the best-fit opportunities for a given student
(or the specific skill gaps standing in the way of a near-miss).

## How it works

1. **Normalize** -- every raw skill/certification string (from both student
   records and opportunity postings) is mapped to one canonical tag using a
   skills taxonomy: an explicit lookup table, with a fuzzy-matching fallback
   (`rapidfuzz`) for near-duplicate spellings not yet in the table.
2. **Score** -- for each student-opportunity pair, compute the fraction of
   the opportunity's requirements the student's normalized skills cover,
   plus the specific matched and missing (gap) skills.
3. **Rank** -- for each student, sort every opportunity by that score,
   best fit first.

### Course pipeline

The same skill tags also drive a course side, so the tool matches students
to NPower's own courses and not only to partner opportunities:

1. **Courses in** -- a student's `completed_courses` are turned into the
   skills those courses teach (from `data/courses.csv`), then fed into the
   opportunity matching above.
2. **Course matching** -- every course the student hasn't taken is scored by
   how many of its prerequisites the student already has, so the more
   advanced courses a student is ready for come out on top.
3. **Timeline** -- for a student and a target opportunity, list the courses
   that teach the missing skills, in order, with week ranges.

`data/courses.csv` was built from the NPower Programs Master Overview Deck.
The deck does not list prerequisites, so the three prerequisites in that
file are my own assumptions until NPower confirms them -- see
[`docs/week-05-06-development-sprint-1.md`](docs/week-05-06-development-sprint-1.md).

## Status

This currently runs against a small **mock dataset** (`data/sample_students.csv`,
`data/sample_opportunities.csv`) with intentionally messy skill-name variants,
to prove the ingest -> normalize -> score -> rank pipeline works end to end.
Real NPower course/certification and partner opportunity data (from my
capstone contact, Robert) will replace the mock data once available -- the
taxonomy in `src/taxonomy.py` will need to be extended to cover NPower's
actual course/cert names, but the rest of the pipeline shouldn't need to change.

Student and opportunity CSVs are loaded into a small SQLite database
(`db/schema.sql`) that the pipeline and the Streamlit UI both query -- see
[`docs/week-03-04-system-architecture.md`](docs/week-03-04-system-architecture.md)
for the full schema (ERD), module structure, and sequence diagram.

## Project layout

```
src/
  taxonomy.py   # canonical skill tags + raw-string -> tag normalization
  scoring.py    # overlap scoring + per-student ranking
  courses.py    # course list, course recommendations, pathway timeline
  db.py         # SQLite persistence: load CSVs, seed taxonomy, compute matches
  pipeline.py   # CLI: ingest CSVs -> build db -> normalize -> score -> rank -> export
app.py          # Streamlit staff-facing UI (upload CSVs, run matching, browse/download results)
db/
  schema.sql    # SQLite schema (tables + views)
data/           # input CSVs (mock data for now) + courses.csv (NPower course list)
output/         # generated ranked_matches.csv, ranked_courses.csv, unmapped_skills.csv (gitignored)
tests/          # pytest unit tests for taxonomy, scoring, and db
docs/           # weekly capstone journal (requirements, architecture, etc.)
```

## Setup

```bash
pip install -r requirements.txt
```

## Run the pipeline (CLI)

```bash
python -m src.pipeline
```

Builds/overwrites `db/skills_match.db`, then writes `output/ranked_matches.csv`
(every student, every opportunity, sorted best-fit-first per student),
`output/ranked_courses.csv` (every student, every course they could take
next, most-ready-first) and `output/unmapped_skills.csv` (any raw skill
string the taxonomy couldn't confidently map -- a to-do list for extending
`EXPLICIT_MAP`).

To run against different data:

```bash
python -m src.pipeline --students path/to/real_students.csv --opportunities path/to/real_opportunities.csv --courses path/to/courses.csv
```

The students CSV can have an optional `completed_courses` column (course ids
or course names from `courses.csv`, separated by `;`).

## Run the staff-facing UI (Streamlit)

```bash
streamlit run app.py
```

Lets a non-developer staff member upload student/opportunity CSVs (or use the
built-in sample data), run the matcher, browse results per student, and
download `ranked_matches.csv` -- no code required (FR-12). It also shows each
student's recommended courses and a pathway timeline to a chosen opportunity.

## Run the tests

```bash
pytest
```
