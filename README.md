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
tests/          # pytest tests for taxonomy, scoring, courses, db, and the app
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

The CSVs are checked before anything is loaded. A missing column, an empty
id/name/title, a repeated id, or a skill in the course list that is not in
the taxonomy stops the run with a message saying what to fix.

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

## Privacy and data handling

The tool runs locally, has no accounts, and sends nothing to an external
service. The Streamlit app keeps uploaded student records only in a
temporary folder that is deleted after each run. The command-line pipeline
leaves a database and CSVs in `db/` and `output/` until you delete them.
Details, deletion steps, and known limits are in [`PRIVACY.md`](PRIVACY.md).

## Accessibility

What has been done: every input has a text label, bad input files give a
plain-language error message instead of a code traceback, scores are shown
as numbers and not only as bars, and the gap and timeline tables are real
HTML tables (the timeline chart has the same data in a table under it).

Known limits: the larger result grids use Streamlit's `st.dataframe`, which
is drawn on a canvas. It exposes its cells to assistive technology, but
scores appear there as raw numbers (0.6667) instead of percentages, and I
have not tried it with a screen reader; the CSV downloads are the
alternative. Section headings jump from level 1 to level 3. The app has not
been audited against WCAG, so I make no compliance claim.

## AI and tool use

**In the application:** none. The tool does not use AI or call any external
service when it runs. Skill matching is a lookup table plus `rapidfuzz`
string similarity, which is a fixed formula, not a trained model. Every
score can be traced to the matched and missing skills shown next to it.

**In development:** I designed and built this project. I used Claude
(Anthropic), mainly through Claude Code, for research and brainstorming, to
explain concepts I was stuck on, and to suggest or draft code where I was
stuck, which I reviewed before keeping. The October 2026 hardening pass
(CSV checks, spreadsheet-safe exports, the app's temporary database, the
tests for those, and `PRIVACY.md`) was drafted with Claude Code and reviewed
by me. The weekly journal in `docs/` notes where AI helped as it happened.

Libraries: pandas, rapidfuzz, Streamlit (with Altair for the timeline
chart), SQLite through Python's standard library, and pytest.

## License

All rights reserved -- see [`LICENSE`](LICENSE). The repository is public
for course review; it is not open source. NPower's course information and
the third-party libraries are not covered by that notice.
