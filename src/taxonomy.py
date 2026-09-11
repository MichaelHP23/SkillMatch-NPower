"""Skills taxonomy: maps messy raw skill/certification strings to one
canonical tag.

Two layers:
  1. EXPLICIT_MAP - exact matches after light text cleaning (fast, certain)
  2. Fuzzy fallback (rapidfuzz) - catches near-duplicate spellings not yet
     in EXPLICIT_MAP, above a confidence threshold.

This is a starter taxonomy built for the mock/sample data in data/. Once
real course syllabi and partner opportunity requirements are available
from NPower, extend EXPLICIT_MAP with the actual canonical skill list --
the normalization/scoring/pipeline code below does not need to change.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz, process

# Canonical tags -- the single, standardized name for each real-world skill.
CANONICAL_TAGS = [
    "CompTIA A+",
    "CompTIA Network+",
    "CompTIA Security+",
    "Customer Service",
    "Microsoft Excel",
    "Windows OS Administration",
    "Linux Fundamentals",
    "AWS Cloud Practitioner",
    "Help Desk Support",
]

# Explicit mapping from a *cleaned* raw string to its canonical tag.
# Add every known real-world variant here as they're discovered in NPower's
# actual course/cert names and partner opportunity postings.
EXPLICIT_MAP: dict[str, str] = {
    "comptia a+": "CompTIA A+",
    "a+": "CompTIA A+",
    "a+ certification": "CompTIA A+",
    "comptia a+ certification": "CompTIA A+",
    "comptia network+": "CompTIA Network+",
    "network+": "CompTIA Network+",
    "comptia security+": "CompTIA Security+",
    "security+": "CompTIA Security+",
    "customer service": "Customer Service",
    "customer service skills": "Customer Service",
    "microsoft excel": "Microsoft Excel",
    "excel": "Microsoft Excel",
    "windows os administration": "Windows OS Administration",
    "windows administration": "Windows OS Administration",
    "linux fundamentals": "Linux Fundamentals",
    "aws cloud practitioner": "AWS Cloud Practitioner",
    "help desk support": "Help Desk Support",
}

FUZZY_MATCH_THRESHOLD = 85  # 0-100; below this, a skill is left unmapped


def clean(raw: str) -> str:
    """Lowercase, collapse whitespace, and normalize 'plus' / '+' spelling
    so 'Network Plus' and 'Network+' land on the same cleaned string."""
    text = raw.strip().lower()
    text = re.sub(r"\bplus\b", "+", text)
    text = re.sub(r"\s+\+", "+", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class NormalizationResult:
    raw: str
    cleaned: str
    canonical_tag: str | None
    matched_via: str  # "explicit" | "fuzzy" | "unmapped"
    fuzzy_score: float | None = None


def normalize_skill(raw: str) -> NormalizationResult:
    """Map one raw skill/certification string to its canonical tag."""
    cleaned = clean(raw)

    if cleaned in EXPLICIT_MAP:
        return NormalizationResult(raw, cleaned, EXPLICIT_MAP[cleaned], "explicit")

    match = process.extractOne(cleaned, EXPLICIT_MAP.keys(), scorer=fuzz.WRatio)
    if match is not None:
        best_key, score, _ = match
        if score >= FUZZY_MATCH_THRESHOLD:
            return NormalizationResult(
                raw, cleaned, EXPLICIT_MAP[best_key], "fuzzy", fuzzy_score=score
            )

    return NormalizationResult(raw, cleaned, None, "unmapped")


def normalize_skill_list(raw_skills: list[str]) -> list[NormalizationResult]:
    return [normalize_skill(s) for s in raw_skills if s.strip()]
