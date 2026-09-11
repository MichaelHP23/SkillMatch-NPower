# Weeks 3-4: System Architecture

**Status:** Not started
**Objective (per syllabus):** Flesh out ideas with DB schema, UML diagrams, and API endpoints.

---

## Planned deliverables

- [ ] Data schema for students, opportunities, the skills taxonomy, and match results -- an ERD if a database is introduced, or a documented file/table schema if the tool stays CSV/SQLite-based (decision to be made here; current PoC is flat-file CSV, see [Week 2](week-02-requirements-analysis.md) Section 6)
- [ ] UML class diagram for `src/` (`taxonomy.py`, `scoring.py`, `pipeline.py`) and how they depend on each other
- [ ] Sequence diagram for one pipeline run: CSV read -> normalize -> score -> rank -> CSV export
- [ ] API endpoints -- only applicable if the staff-facing interface (FR-12) is built as a small local API/app rather than a script or Streamlit UI; document that decision here once made
- [ ] Revisit the provisional data schema in Week 2 against NPower's real data, if received by this point, and note any changes

This file will be filled in as this phase of work happens.
