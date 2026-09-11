# Week 1: Project Definition

**Project:** NPower Skills-Matching Tool
**Course:** CISC 4900 Capstone
**Author:** Michael Pink
**Status:** Complete

---

## 1. Problem statement

NPower's placement staff have no automated way to determine which partner opportunities a given student is qualified for. Student skill data (completed courses, earned certifications) is recorded inconsistently, and partner opportunities describe required skills in free text with no shared vocabulary -- the same skill can appear as "A+", "CompTIA A+", or "CompTIA A+ Certification" across different records. Matching students to opportunities today is manual and ad hoc, which is slow and risks overlooking qualified students or good-fit opportunities as the number of students and partner postings grows.

## 2. Objectives

1. Build a skills taxonomy that normalizes messy, real-world variations in course and certification names into a single canonical tag per skill.
2. Apply that taxonomy to both student records and partner opportunity requirements so the two sides can be compared on equal terms.
3. Score the overlap between a student's normalized skills and an opportunity's normalized requirements, surfacing both the match and the specific skill gaps.
4. Produce a ranked, per-student list of best-fit opportunities that NPower placement staff can act on directly.
5. Deliver all of the above as a from-scratch, standalone Python tool, version-controlled on GitHub, buildable without a budget or paid infrastructure.

Success for this project means NPower staff can go from "manually cross-referencing spreadsheets" to "running a tool and getting a ranked, explainable shortlist" for any given student.

## 3. Stakeholders (summary)

- **Primary user:** NPower placement staff (career coaches / placement coordinators)
- **Indirect beneficiary:** NPower students
- **Domain expert / data source:** Robert, NPower capstone contact
- **Full detail:** see [Week 2 -- Requirements Analysis](week-02-requirements-analysis.md), Section 3.

## 4. Scope (summary)

In scope: CSV-based ingestion, taxonomy-driven normalization, overlap scoring, per-student ranking, an unmapped-skill log, and (later) a lightweight non-developer interface.

Out of scope: automating placement decisions, a public/student-facing app, live hosted infrastructure with user accounts, and any external skills-taxonomy or labor-market API.

Full scope boundaries are formalized in [Week 2 -- Requirements Analysis](week-02-requirements-analysis.md), Section 2.

## 5. Research: existing solutions

No existing product was found that solves this exact problem (skills-taxonomy-based matching of workforce-development trainees to partner opportunities, purpose-built for a single training nonprofit's internal pipeline). Three reference points were identified during competitive research:

| Type | Solution | Why it's positioned this way |
|---|---|---|
| Direct competitor | [RiseKit](https://www.risekit.co/communitykit) -- nonprofit workforce software | Closest existing product to this problem and audience: connects job seekers/trainees at workforce-development nonprofits to employer opportunities. |
| Indirect competitor | [SkillSmart](https://www.skillsmart.us/) -- construction/energy workforce-compliance platform (InSight IQ) with a secondary skills-based talent-pipeline product (Seeker) | Solves an adjacent piece of the same broad problem (skills-based matching) but for a different core audience and use case: contractors, project owners, and municipalities managing prevailing-wage and apprenticeship compliance, not a training nonprofit's internal student-to-opportunity pipeline. |
| Replacement competitor | Manual spreadsheet/email matching by staff, or general job boards (Indeed, LinkedIn) | The current status quo -- what this tool replaces, or what a student could fall back on if they bypassed NPower's structured placement process entirely. |

**Conclusion:** the gap this project fills -- a lightweight, taxonomy-driven matcher built specifically around NPower's own course/certification structure and partner requirements, producing explainable per-student rankings -- is not directly served by any of the above. This supports building a from-scratch tool rather than adopting or adapting an existing product.

## 6. Next step

Week 2 formalizes the objectives and scope above into concrete functional and non-functional requirements -- see [`week-02-requirements-analysis.md`](week-02-requirements-analysis.md).
