# Weeks 5-6: Development -- Sprint 1

**Status:** In progress
**Objective (per syllabus):** Core MVP functionality; initial code setup.

---

## Starting point

Initial code setup and a working core pipeline already exist from the Proof of Concept (Week 1-2 of the course's PoC/Prototype/Pilot/MVP/MDP milestone track): `src/taxonomy.py`, `src/scoring.py`, `src/pipeline.py`, and tests, all passing against mock data. Sprint 1 builds on that rather than starting from zero.

## Planned deliverables

- [ ] Swap mock `data/*.csv` for NPower's real student and opportunity data (once received from Robert)
- [ ] Extend `EXPLICIT_MAP` in `src/taxonomy.py` to cover NPower's actual course/certification names
- [ ] Handle real-data edge cases the mock data didn't exercise (malformed rows, missing fields, empty skill lists)
- [ ] Expand test coverage to match

## Course pipeline (added this sprint)

A main goal of the project is a pipeline for NPower's own courses, not only
partner opportunities. This sprint adds that, using the NPower Programs
Master Overview Deck as the first source of real course data.

**What it does**

- `data/courses.csv` -- one row per NPower program: weeks, hours,
  prerequisites, and skills taught. Staff can edit it without touching code.
- Students CSV gets an optional `completed_courses` column. Finished courses
  are turned into skills before opportunity matching runs.
- `src/courses.py` ranks the courses each student could take next
  (`output/ranked_courses.csv`) and builds a timeline of courses that close
  the gap to a target opportunity.
- The Streamlit app shows both: "Recommended NPower courses" and "Pathway
  timeline".

**Assumptions I made (need to confirm with Robert)**

The deck has no prerequisite information, so these are my guesses:

| Course | Assumed prerequisite |
|---|---|
| Networking & Systems Administration | CompTIA A+ |
| Cyber Security | CompTIA Network+ |
| AWS Solutions Architect | AWS Cloud Practitioner |

Other choices:

- "Skillbridge: Cyber Security" and "Cyber Security" have the same
  curriculum in the deck, so they are one row.
- Electives are not counted as skills taught, only the primary credentials
  and main topics.
- The timeline uses week numbers (Week 1-12, 13-22, ...), not calendar
  dates, because the deck has no cohort start dates. It assumes courses are
  taken one after another.

**Problems found in the deck (to ask Robert about)**

- The App Development credentials slide is a copy of the Networking &
  Systems Administration one, so that course only has its topics as skills.
- Tech Fundamentals + Data Analytics says 90 hours for an 18 week program,
  which looks wrong. Hours left blank.
- Networking & Systems Administration has no clock hours listed.
- Met Council MS 365 & Copilot says 76 hours on the overview but the
  modules add up to 72.

**Not done yet**

- Real prerequisites and real student course-completion data
- Calendar dates on the timeline
- Letting a student pick electives
