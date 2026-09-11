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

## 2. Scope

### 2.1 In scope

- Ingesting student records and partner opportunity postings from CSV exports
- A skills taxonomy that maps raw, inconsistent skill/certification strings to one canonical tag per skill
- Normalizing both student skills and opportunity requirements against that taxonomy
- Scoring each student-opportunity pair by requirement overlap, and identifying matched vs. missing skills
- Producing a ranked list of opportunities per student, sorted best fit first
- Logging any raw skill string the taxonomy cannot confidently map, so the taxonomy can be extended
- A lightweight, non-developer-facing way to run the tool and view results (interface finalized during the Pilot phase, weeks 7-9)

### 2.2 Out of scope

- Automating or overriding staff placement decisions -- the tool ranks and informs, staff decide
- A public-facing or student-facing application (the primary user is NPower placement staff, per Section 3)
- Live/hosted production infrastructure with authenticated user accounts (not needed for a script/report-based tool; see NFR-6)
- Integration with any external skills-taxonomy or labor-market API (none identified as necessary; see Section 6, Assumptions)
- Modifying any existing NPower system -- this is a from-scratch, standalone tool

## 3. Stakeholders and users

| Role | Description | Relationship to the tool |
|---|---|---|
| NPower placement staff | Career coaches / placement coordinators | Primary end-user. Runs the tool against current student and opportunity data; acts on its ranked output. |
| NPower students | Enrolled in help desk, networking, cybersecurity, and related programs | Indirect beneficiary. Receives faster, more accurate placement recommendations; does not interact with the tool directly. |
| Robert (NPower capstone contact) | Domain expert / data source | Supplies real course syllabi, certification lists, and partner opportunity requirements; validates taxonomy accuracy during the Pilot. |
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
| FR-12 | The system shall provide a way for a non-developer NPower staff member to run the matching process and view results without editing code. | Planned (Pilot, weeks 7-9) |
| FR-13 | The system shall allow a staff member to re-run the matching process against updated student or opportunity data without developer involvement. | Planned (MVP, weeks 10-12) |

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

## 6. Data requirements

The PoC uses the following schema against mock data. **This schema is provisional** and will be revised once real exports from NPower are available -- likely differences include additional student/opportunity metadata (cohort, program track, location, posting deadline) and possibly a wider or structured skills field.

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

## 7. Constraints

- **Team:** Solo project.
- **Timeline:** CISC 4900 capstone schedule -- PoC (weeks 1-3, complete), Prototype (weeks 4-6), Pilot (weeks 7-9), MVP (weeks 10-12), MDP (weeks 13-16).
- **Time availability:** Author works part-time (19 hrs/week) alongside a full course load; realistic weekly project time is variable and most likely to fall short of 15+ hrs in some weeks (see Project Intake Survey, time-constraint response).
- **Technology:** Python, pandas, rapidfuzz, Git/GitHub (repository required for the course); no external APIs; no budget for paid tools or hosting.
- **Data availability:** Real NPower syllabi and partner opportunity requirements are not yet available as of this writing; the taxonomy and CSV schema in Section 6 are provisional until Robert provides them.

## 8. Assumptions and open questions

- **Assumption:** NPower's real course/certification names will follow a similarly bounded, enumerable structure to the mock taxonomy (a manageable, describable set of programs), making a rule-based taxonomy tractable without needing a machine-learning approach.
- **Assumption:** Student and opportunity data will continue to arrive as CSV/Excel exports rather than through a live system integration.
- **Open question:** Will opportunity requirements distinguish "required" from "preferred" skills? The current scoring model (FR-7) treats all listed requirements as equally weighted; this may need to change once real opportunity postings are reviewed.
- **Open question:** What format will Robert's real data arrive in, and will it need additional cleaning/restructuring beyond what `pipeline.py` currently handles?
- **Open question:** Final scope of the staff-facing interface (FR-12) -- CLI vs. Streamlit app -- will be decided based on staff feedback gathered during the Pilot.

## 9. Acceptance criteria for this phase

Requirements analysis for this phase is complete when:

- [x] Functional and non-functional requirements are documented and traceable to the Project Intake Survey's stated problem, solution, and value-add
- [x] A provisional data schema exists and is implemented against mock data
- [x] Every implemented functional requirement (FR-1 through FR-11) has automated test coverage or a working, runnable demonstration
- [ ] Requirements are reviewed against NPower's real data once received, and this document is revised accordingly (tracked as a follow-up task, not a blocker for this phase)
