# Project Journal -- CISC 4900 Capstone

One markdown file per week (or week-pair) of the course schedule, tracking scope, requirements, architecture, and progress as the NPower Skills-Matching Tool is built.

| Weeks | Phase | Status |
|---|---|---|
| 1 | [Project Definition](week-01-project-definition.md) | Complete |
| 2 | [Requirements Analysis](week-02-requirements-analysis.md) | Complete (living document -- revisit once real NPower data arrives) |
| 3-4 | [System Architecture](week-03-04-system-architecture.md) | Complete (done early at professor's suggestion) |
| 4 | [Week 4 work log](week-03-04-system-architecture.md#week-4-921---927----65-hours) (inside the Weeks 3-4 file) | Complete |
| 5-6 | [Development -- Sprint 1](week-05-06-development-sprint-1.md) | In progress |
| 7-8 | [Development -- Sprint 2](week-07-08-development-sprint-2.md) | Not started |
| 9-10 | [Development -- Sprint 3](week-09-10-development-sprint-3.md) | Not started |
| 11-12 | [Integration & QA](week-11-12-integration-qa.md) | Not started |
| 13 | [Documentation](week-13-documentation.md) | Not started |
| 14 | [Code Refinement](week-14-code-refinement.md) | Not started |
| 15 | [Final Delivery](week-15-final-delivery.md) | Not started |

Each week's time-log entries are in a **Work log** section at the bottom of that week's file.

## Privacy, data integrity, and accessibility plan

This work was pulled forward into Sprint 1 instead of being left for
Weeks 13-14, because it has to be right before real student data arrives.
A box is ticked only when the change is in the code and covered by a test
or checked by hand.

**Phase 1 -- Ownership, privacy, and data inventory**

- [x] Licensing decision: all rights reserved (`LICENSE`)
- [x] Data inventory and data flows written down (`PRIVACY.md`)
- [x] Streamlit usage statistics turned off (`.streamlit/config.toml`)
- [ ] Ask Robert whether the course information in `data/courses.csv` may stay in a public repo
- [ ] Confirm with the course and NPower that neither has a claim on the code
- [ ] Agree with NPower what student data may be used, where it may be stored, and for how long
- [ ] Move the working copy out of any cloud-synced folder before loading real data

**Phase 2 -- Data integrity and security**

- [x] Fuzzy matching no longer maps partial strings ("C" -> Microsoft Excel) -- tested
- [x] CSVs checked for missing columns, empty required cells, and repeated ids -- tested
- [x] Course list skills must be in the taxonomy -- tested
- [x] The app no longer leaves uploaded student records in `db/` -- tested
- [x] Exported CSVs are safe to open in a spreadsheet -- tested
- [ ] Retention rule for command-line output (`db/`, `output/`)
- [ ] Decide whether student names are needed, or ids are enough
- [ ] Pin dependency versions in `requirements.txt`

**Phase 3 -- Accessibility and user experience**

- [x] Bad input shows a readable error instead of a traceback -- tested
- [ ] Gap and timeline tables changed to real HTML tables -- in the code, not yet checked in a browser
- [x] Match column shows real percentages (was showing 0% / 1%) -- checked in a browser on the sample data
- [ ] Fix the heading levels (page title is level 1, sections are level 3)
- [ ] Keyboard-only and screen-reader test of the app
- [ ] Replace or supplement the remaining `st.dataframe` grids
- [ ] Replace the deprecated `use_container_width` argument

**Phase 4 -- Transparency and verification**

- [x] AI and tool-use statement in the main `README.md`
- [ ] Re-check `PRIVACY.md` and the README against the code once real data is in use
