# Requirements Analysis

**Project:** NPower Skills-Matching Tool
**Course:** CISC 4900 Capstone
**Author:** Michael Pink
**Phase:** Week 2 -- Requirements Analysis
**Status:** Draft, based on the Project Intake Survey and the working Proof of Concept. Will be revised once real course syllabi and partner opportunity requirements are received from NPower (capstone contact: Robert).

---

## 1. Purpose

NPower placement staff currently match students to partner internship, apprenticeship, and job opportunities by manually comparing each student's completed coursework and certifications against each opportunity's stated requirements. Student and opportunity data both use inconsistent, free-text skill names (e.g. "A+", "CompTIA A+", "CompTIA A+ Certification"), so this comparison is slow, ad hoc, and does not scale as the number of students and opportunities grows.

This project builds a tool that normalizes both sides of that comparison against one canonical skills taxonomy, scores the overlap between a student's skills and an opportunity's requirements, and produces a ranked, explainable list of best-fit opportunities per student -- including the specific skills that are missing for a near-miss match.

### 1.1 Success criteria

This is a capstone project, not a production launch, so success is judged qualitatively rather than against a hard KPI target. The tool succeeds if, by the Pilot (weeks 7-9):

- A staff member can get a ranked, explainable opportunity list for any given student in seconds, replacing a manual spreadsheet cross-reference that currently takes real staff time per student.
- Every ranked result shows *why* it ranked where it did (matched skills and specific missing skills), not just a score -- so staff can trust it without re-verifying by hand.
- The taxonomy correctly resolves the large majority of real skill-name variants staff actually encounter in NPower's data (measured directly: the size of `output/unmapped_skills.csv` relative to total skills processed, once run against real data).
- Robert and at least one other staff member have run the tool themselves and confirmed the ranked output matches their own judgment for a sample of students.

## 2. Scope

### 2.1 In scope

- Ingesting student records and partner opportunity postings from CSV exports
- A skills taxonomy that maps raw, inconsistent skill/certification strings to one canonical tag per skill
- Normalizing both student skills and opportunity requirements against that taxonomy
- Scoring each student-opportunity pair by requirement overlap, and identifying matched vs. missing skills
- Producing a ranked list of opportunities per student, sorted best fit first
- Logging any raw skill string the taxonomy cannot confidently map, so the taxonomy can be extended
- A lightweight, non-developer-facing way to run the tool and view results (interface finalized during the Pilot phase, weeks 7-9)
- Repeated re-runs against updated student/opportunity data over time -- not a one-time batch job; staff should be able to re-run it as new cohorts or postings come in

### 2.2 Out of scope

- Automating or overriding staff placement decisions -- the tool ranks and informs, staff decide
- A public-facing or student-facing application (the primary user is NPower placement staff, per Section 3)
- Live/hosted production infrastructure with authenticated user accounts (not needed for a script/report-based tool; see NFR-6)
- Integration with any external skills-taxonomy or labor-market API (none identified as necessary; see Section 6, Assumptions)
- Modifying any existing NPower system -- this is a from-scratch, standalone tool
- The application/interview/onboarding workflow after a match is identified -- this tool ends at "here's a ranked list," it does not track applications, interviews, or offers
- Skill proficiency or depth -- matching is presence/absence of a canonical skill (a student "has" CompTIA A+ or doesn't); the tool does not model how strong a student is at a given skill
- Non-skill matching factors -- geographic proximity, scheduling/availability, and student interest or preference are not part of the score; the ranked list reflects skill fit only, not a complete placement recommendation
- Legal/compliance eligibility checks -- work authorization, background checks, or other placement eligibility requirements are assumed to be handled by NPower's existing process, not by this tool
- General-purpose or multi-organization use -- this is a tool built specifically around NPower's taxonomy and partner structure, not a reusable product for other workforce-development organizations

## 3. Stakeholders and users

| Role | Description | Relationship to the tool |
|---|---|---|
| NPower placement staff | Career coaches / placement coordinators | Primary end-user. Runs the tool against current student and opportunity data; acts on its ranked output. |
| NPower students | Enrolled in help desk, networking, cybersecurity, and related programs | Indirect beneficiary. Receives faster, more accurate placement recommendations; does not interact with the tool directly. |
| Robert (NPower capstone contact) | Domain expert / data source | Supplies real course syllabi, certification lists, and partner opportunity requirements; validates taxonomy accuracy during the Pilot. |
| Partner organizations | Employers posting internships/apprenticeships/jobs through NPower | Indirect stakeholder, not a direct user. Benefit from better-qualified candidate shortlists; harmed if poor matching wastes their time on unqualified referrals. Never interacts with the tool directly -- their requirements only reach it as data staff enter. |
| NPower program leadership | Manages the partnership pipeline and reports on placement outcomes (e.g. to funders) | Indirect stakeholder. Not a direct user, but relies on accurate, explainable matching to support placement-rate reporting; a factor in why explainability (NFR-1) matters beyond individual staff trust. |
| Project author (Michael Pink) | Capstone student / developer | Designs, builds, tests, and documents the tool. |
| Course instructor | CISC 4900 | Evaluates the project against course milestones (PoC, Prototype, Pilot, MVP, MDP). |

## 4. Functional requirements

Each requirement is tagged with its current status: **Implemented** (working in the PoC today, against mock data), or **Planned** (scoped for a later milestone).

| ID | Requirement | Status |
|---|---|---|
| FR-1 | The system shall ingest student records from a CSV file containing, at minimum, a student identifier, name, and a list of completed courses/certifications. | Implemented |
| FR-2 | The system shall ingest partner opportunity records from a CSV file containing, at minimum, an opportunity identifier, partner organization, title, and a list of required skills. | Implemented |
| FR-3 | The system shall maintain a skills taxonomy that maps one or more raw skill/certification strings to a single canonical tag. | Implemented |
| FR-4 | The system shall normalize a raw skill string by first checking it against an explicit taxonomy mapping. | Implemented |
| FR-5 | Where no explicit mapping exists, the system shall attempt a fuzzy-match against known taxonomy entries and accept the match only if it meets a defined confidence threshold. | Implemented |
| FR-6 | The system shall record any raw skill string that cannot be mapped (explicitly or via fuzzy match) to a log, rather than silently discarding it. | Implemented |
| FR-7 | For each student-opportunity pair, the system shall compute a match score equal to the proportion of the opportunity's required (canonical) skills that the student's (canonical) skills satisfy. | Implemented |
| FR-8 | For each student-opportunity pair, the system shall report the specific matched skills and the specific missing skills, not only the numeric score. | Implemented |
| FR-9 | For each student, the system shall produce a ranked list of all opportunities sorted by descending match score. | Implemented |
| FR-10 | The system shall export the ranked results to a CSV report. | Implemented |
| FR-11 | The taxonomy shall be maintained as data (not hardcoded logic) so it can be extended with new skill variants without changing the normalization or scoring code. | Implemented |
| FR-12 | The system shall provide a way for a non-developer NPower staff member to run the matching process and view results without editing code. | Implemented (Streamlit app, `app.py` -- see [Week 3-4](week-03-04-system-architecture.md)) |
| FR-13 | The system shall allow a staff member to re-run the matching process against updated student or opportunity data without developer involvement. | Planned (MVP, weeks 10-12) |
| FR-14 | The system shall accept alternate input file paths and output file paths as runtime arguments, rather than requiring code changes to point at different data. | Implemented |
| FR-15 | The system shall handle a malformed or incomplete data row (missing required column, empty skills field) without crashing the entire run -- at minimum, skip and log the offending row so the rest of the batch still completes. | Planned (Sprint 1, weeks 5-6) |
| FR-16 | Given identical input data, the system shall produce identical ranked output on every run (deterministic scoring and tie-breaking), so results are reproducible and testable. | Implemented |

## 5. Non-functional requirements

| ID | Requirement | Rationale |
|---|---|---|
| NFR-1 (Explainability) | Every match result must be traceable to the specific matched and missing canonical skills that produced its score -- no opaque or unexplained scores. | Staff need to trust and audit results, and use gaps as a coaching tool with students (see Section 8 of the Project Intake Survey response). |
| NFR-2 (Accuracy) | The taxonomy's explicit mapping should resolve the large majority of real, known skill-name variants; the fuzzy-match fallback is a safety net, not the primary matching mechanism, and its confidence threshold must be tunable. | An over-loose fuzzy threshold risks false matches; an over-tight one risks missing legitimate variants. |
| NFR-3 (Usability) | Non-technical staff must be able to run the tool and interpret its output without reading code. | The primary user (Section 3) is not a developer. |
| NFR-4 (Maintainability) | The taxonomy must be extensible by editing data (the explicit mapping), not by modifying normalization or scoring logic. | The taxonomy will grow as new course/certification names are encountered; logic changes carry more risk than data changes. |
| NFR-5 (Portability / cost) | The system must run on free, open-source tooling with no paid APIs, licenses, or hosting required. | No budget allocated to this project (see Project Intake Survey). |
| NFR-6 (No live-traffic requirement) | The system does not need to support concurrent, authenticated, real-time users; batch/report-based operation is sufficient. | Confirmed in the Project Intake Survey -- no live registered userbase is planned during the capstone. |
| NFR-7 (Data privacy) | Student records must stay within the project repository and local/staff-controlled storage; no student data is to be sent to an external API or third-party service. | Student PII (names, coursework) is sensitive; no external API is in scope (Section 2.2). |
| NFR-8 (Testability) | Core normalization and scoring logic must be covered by automated unit tests. | Confirmed with pytest coverage in the current PoC (`tests/`). |
| NFR-9 (Performance) | A full pipeline run should complete well under a minute on a standard laptop at NPower's expected data volume (on the order of hundreds of students, dozens of opportunities). No caching/optimization work is required now; revisit if real volume turns out to be significantly larger. | The fuzzy-match fallback in `taxonomy.py` re-scores against the full `EXPLICIT_MAP` for every unmapped skill with no caching -- fine at this scale, but worth a conscious decision rather than an unexamined one. |
| NFR-10 (Repository data privacy) | Real NPower student and opportunity data (once received from Robert) must never be committed to the GitHub repository, whether the repo is public or shared with the instructor as a collaborator. Only synthetic/mock data belongs in tracked files. | The course requires a publicly visible repo or instructor access (per the intake survey); real student PII in `data/` would otherwise be exposed. This is the highest-priority NFR to get right before real data arrives. |

## 6. Data requirements

The PoC uses the following schema against mock data. **This schema is provisional** and will be revised once real exports from NPower are available -- likely differences include additional student/opportunity metadata (cohort, program track, location, posting deadline) and possibly a wider or structured skills field.

CSV remains the *input* format described below. As of [Week 3-4](week-03-04-system-architecture.md), inputs are loaded into a normalized SQLite database (`db/schema.sql`) that the pipeline and Streamlit app both read from -- see that document for the full ERD.

**`data/sample_students.csv`**

| Column | Type | Notes |
|---|---|---|
| `student_id` | string | Unique identifier |
| `name` | string | Display name |
| `skills` | string | Semicolon-separated raw skill/certification strings |

**`data/sample_opportunities.csv`**

| Column | Type | Notes |
|---|---|---|
| `opportunity_id` | string | Unique identifier |
| `partner_org` | string | Partner organization name |
| `title` | string | Opportunity title |
| `required_skills` | string | Semicolon-separated raw required-skill strings |

**`src/taxonomy.py` -- `EXPLICIT_MAP`**: a Python dictionary of `{cleaned raw string: canonical tag}`. Currently seeded with 9 canonical tags covering the mock dataset's help-desk/networking/cybersecurity/general-professional skills. To be replaced/extended with NPower's real course and certification names once Robert's data is available.

### 6.1 Output schema

These are what staff actually read (FR-10, FR-12), so their schema is specified here just as concretely as the inputs.

**`output/ranked_matches.csv`** -- one row per student-opportunity pair, all opportunities included for every student, sorted best fit first per student:

| Column | Type | Notes |
|---|---|---|
| `student_id` | string | Matches `student_id` in the input |
| `student_name` | string | |
| `opportunity_id` | string | Matches `opportunity_id` in the input |
| `opportunity_title` | string | Job name |
| `partner_org` | string | Partner organization offering the opportunity |
| `match_score` | float, 0-1 | Fraction of the opportunity's required canonical skills the student meets |
| `matched_skills` | string | Semicolon-separated canonical tags the student has that the opportunity requires |
| `missing_skills` | string | Semicolon-separated canonical tags the opportunity requires that the student is missing |

**`output/unmapped_skills.csv`** -- one row per raw skill string that couldn't be confidently mapped (FR-6):

| Column | Type | Notes |
|---|---|---|
| `entity_id` | string | The `student_id` or `opportunity_id` the raw skill came from |
| `entity_name` | string | Student name or opportunity (job) title for that ID |
| `source` | string | `student` or `opportunity` |
| `raw_skill` | string | The original, unmodified string as it appeared in the input |
| `cleaned` | string | The string after `clean()`, for debugging why it didn't match |

## 7. Constraints

- **Team:** Solo project.
- **Timeline:** CISC 4900 capstone schedule -- PoC (weeks 1-3, complete), Prototype (weeks 4-6), Pilot (weeks 7-9), MVP (weeks 10-12), MDP (weeks 13-16).
- **Time availability:** Author works part-time (19 hrs/week) alongside a full course load; realistic weekly project time is variable and most likely to fall short of 15+ hrs in some weeks (see Project Intake Survey, time-constraint response).
- **Technology:** Python, pandas, rapidfuzz, Git/GitHub (repository required for the course); no external APIs; no budget for paid tools or hosting.
- **Data availability:** Real NPower syllabi and partner opportunity requirements are not yet available as of this writing; the taxonomy and CSV schema in Section 6 are provisional until Robert provides them.
- **Repository visibility:** CISC 4900 requires the project repository to be either publicly visible or shared with the instructor as a collaborator. This directly motivates NFR-10 (Section 5) -- real student data must never be committed, since "private to the team" is not guaranteed to be an option.
- **Project tracking:** The course requires a maintained, instructor-visible project tracker (e.g. a GitHub Project board) alongside the repository itself.

## 8. Assumptions and open questions

- **Assumption:** NPower's real course/certification names will follow a similarly bounded, enumerable structure to the mock taxonomy (a manageable, describable set of programs), making a rule-based taxonomy tractable without needing a machine-learning approach.
- **Assumption:** Student and opportunity data will continue to arrive as CSV/Excel exports rather than through a live system integration.
- **Open question:** Will opportunity requirements distinguish "required" from "preferred" skills? The current scoring model (FR-7) treats all listed requirements as equally weighted; this may need to change once real opportunity postings are reviewed.
- **Open question:** What format will Robert's real data arrive in, and will it need additional cleaning/restructuring beyond what `pipeline.py` currently handles?
- **Resolved (originally an open question):** Final scope of the staff-facing interface (FR-12) was going to be decided based on staff feedback during the Pilot, but my professor suggested looking into a UI and a real data-storage layer earlier than planned. Decided in [Week 3-4](week-03-04-system-architecture.md): Streamlit for the interface, SQLite for storage.
- **Open question / known limitation:** The current model treats every opportunity as having unlimited capacity and always being open. A real opportunity has a limited number of seats and a status (open/filled/closed) -- without that data, the tool could rank ten students as strong fits for a single-seat posting with no way to flag that it's already spoken for. Not a blocker for the Pilot (mock data has no capacity concept), but needs resolving before the MVP if Robert's real opportunity data includes capacity or status fields.

## 9. Acceptance criteria for this phase

Requirements analysis for this phase is complete when:

- [x] Functional and non-functional requirements are documented and traceable to the Project Intake Survey's stated problem, solution, and value-add
- [x] A provisional data schema exists and is implemented against mock data, including output schemas (Section 6.1)
- [x] Every implemented functional requirement (FR-1 through FR-11) has automated test coverage or a working, runnable demonstration
- [x] Real student/opportunity data is protected from accidental commit before any real data exists (NFR-10, `.gitignore` default-deny)
- [ ] FR-14 (CLI-configurable file paths) and FR-16 (deterministic output) are implemented but not yet covered by an explicit regression test -- both currently rely on the existing test suite passing incidentally rather than testing the behavior directly. Add tests before Sprint 1.
- [ ] FR-15 (graceful handling of malformed rows) is documented but not yet implemented -- scoped for Sprint 1, not a blocker for this phase
- [ ] Requirements are reviewed against NPower's real data once received, and this document is revised accordingly (tracked as a follow-up task, not a blocker for this phase)

---

## 10. Work log

Taken from the Tasks tab of my CISC 4900 time log. Dates, hours, and categories match the log; wording is lightly cleaned up for typos.

### Week 2 (9/7 - 9/13) -- 10 hours

**9/11/2026 -- Research, Training, Learning (1.5 h)**
- **Task:** Deep-dive research on ways to solve the issue at NPower: YouTube videos, similar code, and AI assistance to help find the solution needed.
- **Challenges / next steps:** Start my first set of design plans for the project.
- **Reflection:** This research was really helpful and should make the designs straightforward.

**9/11/2026 -- Design (2.5 h)**
- **Task:** Designed how to address the main issue and how the code will solve it, along with handwritten illustrations of where everything happens. The main goal was to simplify the matchmaking process and come up with short drafts of code.
- **Challenges / next steps:** Document and start coding. One challenge is not having student data yet, but I can use made-up test data in the meantime.
- **Reflection:** Making a mock design of everything took longer than I thought, but now I have a clear path of where to go.

**9/11/2026 -- Documentation (1.0 h)**
- **Task:** Set up my GitHub repo with my assignments and timelines of what needs to be done.
- **Challenges / next steps:** Start coding.
- **Reflection:** This was good, as it showed me and my supervisor when and what needs to be done.

**9/11/2026 -- Research, Training, Learning (0.5 h)**
- **Task:** Received NPower's courses/syllabi and did a quick review of what they offer.
- **Challenges / next steps:** Start coding.
- **Reflection:** The syllabus was very helpful and much-needed context.

**9/11/2026 -- Coding (4.0 h)**
- **Task:** Built my first set of code in Python; the first drafts were successful.
- **Challenges / next steps:** Meet with my supervisor and implement the NPower courses.
- **Reflection:** Coding was simple with minimal issues, and having AI teach me new concepts where I got stuck along the way was very helpful.

**9/12/2026 -- Supervisor Discussion (0.5 h)**
- **Task:** Met with my supervisor, who was impressed with what I have so far.
- **Challenges / next steps:** Continue coding, create a front end, find a way to store data, and send the GitHub repo to him.
- **Reflection:** We discussed what the code does and everything went well.

