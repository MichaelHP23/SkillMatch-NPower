"""Course side of the pipeline.

The opportunity pipeline answers "which partner jobs fit this student?".
This module answers three course questions using the same skill tags:

  1. What skills does a student get from the NPower courses they finished?
  2. Which NPower courses should the student take next?
  3. What order of courses (a timeline) gets a student ready for a job?

The course list lives in data/courses.csv so staff can edit it without
touching code.
"""
from pathlib import Path

import pandas as pd

from src.taxonomy import normalize_skill

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COURSES_CSV = PROJECT_ROOT / "data" / "courses.csv"


def split_list(cell):
    """Turn a cell like "A+; Excel" into ["A+", "Excel"]. Empty cell -> []."""
    if pd.isna(cell):
        return []
    items = []
    for part in str(cell).split(";"):
        part = part.strip()
        if part:
            items.append(part)
    return items


def to_tags(raw_skills):
    """Normalize a list of raw skill strings into a set of canonical tags."""
    tags = set()
    for raw in raw_skills:
        result = normalize_skill(raw)
        if result.canonical_tag is not None:
            tags.add(result.canonical_tag)
    return tags


def load_courses(courses_csv=DEFAULT_COURSES_CSV):
    """Read courses.csv into a list of dictionaries, one per course."""
    df = pd.read_csv(courses_csv)
    courses = []
    for _, row in df.iterrows():
        course = {
            "course_id": str(row["course_id"]).strip(),
            "name": str(row["name"]).strip(),
            "weeks": int(row["weeks"]),
            "prerequisites": to_tags(split_list(row["prerequisites"])),
            "skills_taught": to_tags(split_list(row["skills_taught"])),
        }
        courses.append(course)
    return courses


def find_course(text, courses):
    """Find a course by its id or its name (ignoring upper/lower case)."""
    wanted = text.strip().lower()
    for course in courses:
        if wanted == course["course_id"].lower() or wanted == course["name"].lower():
            return course
    return None


def rank_courses(student_tags, completed_ids, courses):
    """Score every course the student could take next, best first.

    The score is the fraction of the course's prerequisites the student
    already has. A course with no prerequisites is open to everyone, so it
    scores 1.0. Courses the student finished, or that would teach them
    nothing new, are left out.
    """
    results = []
    for course in courses:
        if course["course_id"] in completed_ids:
            continue

        new_skills = course["skills_taught"] - student_tags
        if len(new_skills) == 0:
            continue

        prerequisites = course["prerequisites"]
        met = prerequisites & student_tags
        missing = prerequisites - student_tags
        if len(prerequisites) == 0:
            score = 1.0
        else:
            score = round(len(met) / len(prerequisites), 4)

        results.append({
            "course_id": course["course_id"],
            "course_name": course["name"],
            "weeks": course["weeks"],
            "readiness_score": score,
            "prerequisites_met": sorted(met),
            "prerequisites_missing": sorted(missing),
            "new_skills": sorted(new_skills),
        })

    # Best score first. On a tie, the course with more prerequisites goes
    # first, because that is the more advanced course.
    results.sort(key=lambda r: (-r["readiness_score"], -len(r["prerequisites_met"])))
    return results


def courses_teaching(skill, courses):
    """Names of every course that teaches this skill."""
    names = []
    for course in courses:
        if skill in course["skills_taught"]:
            names.append(course["name"])
    return names


def build_timeline(student_tags, missing_skills, courses):
    """Plan which courses to take, in order, to learn the missing skills.

    Returns two things:
      steps         - list of courses with a start week and an end week
      still_missing - skills that no course in the list can teach

    This is a simple greedy plan: each round it picks the course the student
    is ready for that teaches the most skills still needed. It is not
    guaranteed to be the shortest possible path, and it assumes courses are
    taken one after another (not at the same time).
    """
    have = set(student_tags)
    needed = set(missing_skills) - have
    steps = []
    week = 1

    while len(needed) > 0:
        # Courses that teach something we still need.
        helpful = []
        for course in courses:
            if len(course["skills_taught"] & needed) > 0:
                helpful.append(course)
        if len(helpful) == 0:
            break

        # Of those, which ones is the student ready for right now?
        ready = []
        for course in helpful:
            if course["prerequisites"] <= have:
                ready.append(course)

        if len(ready) == 0:
            # Not ready for any of them yet. Take the course that is closest
            # (fewest missing prerequisites) and plan for its prerequisites.
            closest = min(helpful, key=lambda c: len(c["prerequisites"] - have))
            new_needs = closest["prerequisites"] - have - needed
            if len(new_needs) == 0:
                break  # stuck: nothing teaches the prerequisite
            needed = needed | new_needs
            continue

        # Pick the ready course that teaches the most needed skills.
        # If two tie, take the shorter one.
        best = ready[0]
        for course in ready:
            course_count = len(course["skills_taught"] & needed)
            best_count = len(best["skills_taught"] & needed)
            if course_count > best_count:
                best = course
            elif course_count == best_count and course["weeks"] < best["weeks"]:
                best = course

        steps.append({
            "course_id": best["course_id"],
            "course_name": best["name"],
            "start_week": week,
            "end_week": week + best["weeks"] - 1,
            "skills_gained": sorted(best["skills_taught"] & needed),
        })
        week = week + best["weeks"]
        have = have | best["skills_taught"]
        needed = needed - have

    return steps, sorted(needed)
