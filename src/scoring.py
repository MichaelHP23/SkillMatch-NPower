"""Overlap scoring between a student's normalized skill set and a partner
opportunity's normalized requirement set, plus per-student ranking."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MatchResult:
    student_id: str
    opportunity_id: str
    score: float  # fraction of the opportunity's requirements the student meets, 0-1
    matched_skills: list[str]
    missing_skills: list[str]


def score_match(
    student_id: str,
    opportunity_id: str,
    student_tags: set[str],
    opportunity_tags: set[str],
) -> MatchResult:
    """Score = |matched requirements| / |all requirements| for this opportunity."""
    if not opportunity_tags:
        return MatchResult(student_id, opportunity_id, 0.0, [], [])

    matched = sorted(student_tags & opportunity_tags)
    missing = sorted(opportunity_tags - student_tags)
    score = len(matched) / len(opportunity_tags)

    return MatchResult(student_id, opportunity_id, round(score, 4), matched, missing)


def rank_opportunities_for_student(
    student_id: str,
    student_tags: set[str],
    opportunities: dict[str, set[str]],
) -> list[MatchResult]:
    """Every opportunity's MatchResult for this student, best fit first."""
    results = [
        score_match(student_id, opp_id, student_tags, opp_tags)
        for opp_id, opp_tags in opportunities.items()
    ]
    return sorted(results, key=lambda r: r.score, reverse=True)
