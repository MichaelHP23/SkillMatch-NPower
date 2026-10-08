"""Staff-facing interface for the NPower skills-matching tool.

Run with:

    streamlit run app.py

Lets a non-developer staff member upload (or use the built-in sample) student
and opportunity CSVs, run the same normalize -> score -> rank pipeline as
src/pipeline.py, and browse/download the ranked results -- no code required.
This is FR-12 in docs/week-02-requirements-analysis.md.

It also shows the course side (src/courses.py): which NPower courses each
student should take next, and a week-by-week timeline of the courses that
close the gap to a chosen opportunity.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.courses import DEFAULT_COURSES_CSV, build_timeline, courses_teaching, load_courses, split_list
from src.db import (
    build_database,
    get_ranked_courses_df,
    get_ranked_matches_df,
    get_student_tags,
    get_unmapped_skills_df,
)

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_STUDENTS_CSV = PROJECT_ROOT / "data" / "sample_students.csv"
SAMPLE_OPPORTUNITIES_CSV = PROJECT_ROOT / "data" / "sample_opportunities.csv"

st.set_page_config(page_title="NPower Skills Match", page_icon="\U0001F9E9", layout="wide")

st.title("NPower Skills-Matching Tool")
st.caption(
    "Upload a student list and an opportunity list, or use the sample data below, "
    "then run the matcher to get a ranked, explainable opportunity list per student."
)

with st.sidebar:
    st.header("1. Data")
    students_file = st.file_uploader("Student records CSV", type="csv")
    opportunities_file = st.file_uploader("Opportunity postings CSV", type="csv")
    courses_file = st.file_uploader("Course list CSV (optional)", type="csv")
    using_sample = students_file is None and opportunities_file is None
    if using_sample:
        st.info("No files uploaded -- using the built-in sample data.")

    st.header("2. Run")
    run_clicked = st.button("Run matching", type="primary", use_container_width=True)

    with st.expander("Expected CSV format"):
        st.markdown(
            "**Students:** `student_id, name, skills` (skills separated by `;`)\n\n"
            "**Opportunities:** `opportunity_id, partner_org, title, required_skills` "
            "(required_skills separated by `;`)\n\n"
            "**Students (optional column):** `completed_courses` -- course ids or names "
            "separated by `;`\n\n"
            "**Courses:** `course_id, name, weeks, hours, prerequisites, skills_taught`"
        )


def _resolve_csv(uploaded_file, sample_path: Path, tmpdir: Path, filename: str) -> Path:
    if uploaded_file is None:
        return sample_path
    dest = tmpdir / filename
    dest.write_bytes(uploaded_file.getvalue())
    return dest


if "ranked_df" not in st.session_state:
    st.session_state.ranked_df = None
    st.session_state.unmapped_df = None
    st.session_state.courses_df = None
    st.session_state.student_tags = {}
    st.session_state.courses = []

if run_clicked:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        students_csv = _resolve_csv(students_file, SAMPLE_STUDENTS_CSV, tmp_path, "students.csv")
        opportunities_csv = _resolve_csv(opportunities_file, SAMPLE_OPPORTUNITIES_CSV, tmp_path, "opportunities.csv")
        courses_csv = _resolve_csv(courses_file, DEFAULT_COURSES_CSV, tmp_path, "courses.csv")

        with st.spinner("Normalizing skills and scoring matches..."):
            courses = load_courses(courses_csv)
            conn = build_database(students_csv, opportunities_csv, courses_csv=courses_csv)
            st.session_state.ranked_df = get_ranked_matches_df(conn)
            st.session_state.unmapped_df = get_unmapped_skills_df(conn)
            st.session_state.courses_df = get_ranked_courses_df(conn, courses)
            st.session_state.student_tags = get_student_tags(conn)
            st.session_state.courses = courses
            conn.close()

ranked_df: pd.DataFrame | None = st.session_state.ranked_df
unmapped_df: pd.DataFrame | None = st.session_state.unmapped_df
courses_df: pd.DataFrame | None = st.session_state.courses_df

if ranked_df is None:
    st.info("Choose your data in the sidebar (or leave it blank for the sample data) and click **Run matching**.")
else:
    st.subheader("Best-fit opportunities, per student")
    student_options = ranked_df[["student_id", "student_name"]].drop_duplicates()
    student_label = st.selectbox(
        "Student",
        options=student_options["student_id"],
        format_func=lambda sid: f"{sid} - {student_options.loc[student_options['student_id'] == sid, 'student_name'].iloc[0]}",
    )
    student_view = ranked_df[ranked_df["student_id"] == student_label].sort_values(
        "match_score", ascending=False
    )
    st.dataframe(
        student_view[
            ["student_id", "student_name", "opportunity_id", "opportunity_title", "partner_org",
             "match_score", "matched_skills", "missing_skills"]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "match_score": st.column_config.ProgressColumn(
                "Match", min_value=0, max_value=1, format="%.0f%%"
            ),
        },
    )

    st.divider()
    st.subheader("Recommended NPower courses for this student")
    st.caption(
        "Readiness = how many of the course's prerequisites the student already has. "
        "Courses the student finished, or that teach nothing new, are hidden."
    )
    student_courses = courses_df[courses_df["student_id"] == student_label]
    st.dataframe(
        student_courses[
            ["course_id", "course_name", "weeks", "readiness_score",
             "prerequisites_missing", "new_skills"]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "readiness_score": st.column_config.ProgressColumn(
                "Readiness", min_value=0, max_value=1, format="%.0f%%"
            ),
        },
    )

    st.divider()
    st.subheader("Pathway timeline")
    st.caption("Pick a target opportunity to see which courses close the gap, and in what order.")
    target_id = st.selectbox(
        "Target opportunity",
        options=student_view["opportunity_id"],
        format_func=lambda oid: f"{oid} - {student_view.loc[student_view['opportunity_id'] == oid, 'opportunity_title'].iloc[0]}",
    )
    target_row = student_view[student_view["opportunity_id"] == target_id].iloc[0]
    missing_skills = split_list(target_row["missing_skills"])

    if len(missing_skills) == 0:
        st.success("This student already meets every requirement for this opportunity.")
    else:
        # Which courses teach each missing skill.
        gap_rows = []
        for skill in missing_skills:
            teaching = courses_teaching(skill, st.session_state.courses)
            gap_rows.append({
                "missing_skill": skill,
                "taught_by": "; ".join(teaching) if teaching else "(no NPower course teaches this)",
            })
        st.dataframe(pd.DataFrame(gap_rows), use_container_width=True, hide_index=True)

        steps, still_missing = build_timeline(
            st.session_state.student_tags[student_label], missing_skills, st.session_state.courses
        )
        if len(steps) > 0:
            timeline_df = pd.DataFrame(steps)
            timeline_df["skills_gained"] = timeline_df["skills_gained"].apply("; ".join)
            # The bar starts at the beginning of the first week, so subtract 1.
            timeline_df["bar_start"] = timeline_df["start_week"] - 1
            chart = alt.Chart(timeline_df).mark_bar().encode(
                x=alt.X("bar_start", title="Week"),
                x2="end_week",
                y=alt.Y("course_name", sort=None, title=None),
                tooltip=["course_name", "start_week", "end_week", "skills_gained"],
            )
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(
                timeline_df[["course_name", "start_week", "end_week", "skills_gained"]],
                use_container_width=True,
                hide_index=True,
            )
            st.info(f"Ready for this opportunity after about {steps[-1]['end_week']} weeks of courses.")
        if len(still_missing) > 0:
            st.warning("No NPower course in the list teaches: " + "; ".join(still_missing))

    st.divider()
    st.subheader("Full ranked results")
    st.dataframe(ranked_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download ranked_matches.csv",
        data=ranked_df.to_csv(index=False),
        file_name="ranked_matches.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download ranked_courses.csv",
        data=courses_df.to_csv(index=False),
        file_name="ranked_courses.csv",
        mime="text/csv",
    )

    if unmapped_df is not None and len(unmapped_df):
        with st.expander(f"⚠️ {len(unmapped_df)} skill(s) couldn't be matched to the taxonomy"):
            st.caption(
                "These raw skill strings didn't resolve to a canonical tag. "
                "Add them to EXPLICIT_MAP in src/taxonomy.py so future runs catch them."
            )
            st.dataframe(unmapped_df, use_container_width=True, hide_index=True)
    else:
        st.success("Every skill in this data mapped to a canonical tag.")
