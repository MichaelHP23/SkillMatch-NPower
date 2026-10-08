-- NPower Skills-Matching Tool -- SQLite schema
-- Replaces the flat-CSV-only model from the PoC with a normalized store.
-- The CSVs in data/ remain the *input* format (that's what staff export
-- from their systems); this schema is what the pipeline loads them into
-- and computes against. Designed for System Architecture, weeks 3-4.

PRAGMA foreign_keys = ON;

-- One row per student.
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    completed_courses TEXT  -- course ids from data/courses.csv, joined with "; "
);

-- One row per partner opportunity.
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id TEXT PRIMARY KEY,
    partner_org    TEXT,
    title          TEXT NOT NULL
);

-- The master list of canonical skill tags (was CANONICAL_TAGS in taxonomy.py).
CREATE TABLE IF NOT EXISTS canonical_tags (
    tag TEXT PRIMARY KEY
);

-- The taxonomy's explicit mapping (was EXPLICIT_MAP in taxonomy.py), now
-- data instead of a hardcoded dict -- editable without touching code (NFR-4).
CREATE TABLE IF NOT EXISTS taxonomy_map (
    raw_cleaned TEXT PRIMARY KEY,          -- output of taxonomy.clean()
    tag         TEXT NOT NULL REFERENCES canonical_tags(tag)
);

-- Every raw skill string a student has, and what it normalized to.
-- tag is NULL when normalize_skill() couldn't confidently map it (FR-6).
CREATE TABLE IF NOT EXISTS student_skills (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    raw_skill  TEXT NOT NULL,
    cleaned    TEXT NOT NULL,
    tag        TEXT REFERENCES canonical_tags(tag),
    matched_via TEXT CHECK (matched_via IN ('explicit', 'fuzzy', 'unmapped')),
    fuzzy_score REAL
);

-- Every raw required-skill string an opportunity lists, and what it
-- normalized to. Same shape as student_skills, mirrored for symmetry.
CREATE TABLE IF NOT EXISTS opportunity_requirements (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    raw_skill      TEXT NOT NULL,
    cleaned        TEXT NOT NULL,
    tag            TEXT REFERENCES canonical_tags(tag),
    matched_via    TEXT CHECK (matched_via IN ('explicit', 'fuzzy', 'unmapped')),
    fuzzy_score    REAL
);

-- One row per student-opportunity pair: the computed match (FR-7).
-- Repopulated on every pipeline run (see src/db.py: refresh_matches).
CREATE TABLE IF NOT EXISTS matches (
    student_id     TEXT NOT NULL REFERENCES students(student_id),
    opportunity_id TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    score          REAL NOT NULL,
    PRIMARY KEY (student_id, opportunity_id)
);

-- The per-skill detail behind each match's score (FR-8): for every
-- canonical tag an opportunity requires, was this student a match or a gap?
CREATE TABLE IF NOT EXISTS match_skill_status (
    student_id     TEXT NOT NULL,
    opportunity_id TEXT NOT NULL,
    tag            TEXT NOT NULL REFERENCES canonical_tags(tag),
    matched        INTEGER NOT NULL CHECK (matched IN (0, 1)),
    PRIMARY KEY (student_id, opportunity_id, tag),
    FOREIGN KEY (student_id, opportunity_id)
        REFERENCES matches(student_id, opportunity_id) ON DELETE CASCADE
);

-- Convenience view standing in for the old output/unmapped_skills.csv (FR-6).
CREATE VIEW IF NOT EXISTS unmapped_skills AS
    SELECT ss.student_id AS entity_id, s.name AS entity_name, 'student' AS source,
           ss.raw_skill, ss.cleaned
    FROM student_skills ss JOIN students s ON s.student_id = ss.student_id
    WHERE ss.tag IS NULL
    UNION ALL
    SELECT r.opportunity_id AS entity_id, o.title AS entity_name, 'opportunity' AS source,
           r.raw_skill, r.cleaned
    FROM opportunity_requirements r JOIN opportunities o ON o.opportunity_id = r.opportunity_id
    WHERE r.tag IS NULL;

-- Convenience view standing in for the old output/ranked_matches.csv (FR-9, FR-10),
-- with matched/missing skills aggregated back into semicolon-joined strings
-- so existing CSV-consuming code (and staff expectations) don't change shape.
CREATE VIEW IF NOT EXISTS ranked_matches AS
    SELECT
        m.student_id,
        s.name AS student_name,
        m.opportunity_id,
        o.title AS opportunity_title,
        o.partner_org,
        m.score AS match_score,
        (SELECT GROUP_CONCAT(tag, '; ') FROM match_skill_status
            WHERE student_id = m.student_id AND opportunity_id = m.opportunity_id
            AND matched = 1) AS matched_skills,
        (SELECT GROUP_CONCAT(tag, '; ') FROM match_skill_status
            WHERE student_id = m.student_id AND opportunity_id = m.opportunity_id
            AND matched = 0) AS missing_skills
    FROM matches m
    JOIN students s ON s.student_id = m.student_id
    JOIN opportunities o ON o.opportunity_id = m.opportunity_id
    ORDER BY m.student_id, m.score DESC;
