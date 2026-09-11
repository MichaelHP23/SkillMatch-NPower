from src.taxonomy import normalize_skill


def test_explicit_variants_map_to_same_canonical_tag():
    variants = ["CompTIA A+", "A+ Certification", "comptia a plus", "a+"]
    for raw in variants:
        result = normalize_skill(raw)
        assert result.canonical_tag == "CompTIA A+", f"failed for {raw!r}"


def test_spacing_before_plus_is_normalized():
    result = normalize_skill("Network +")
    assert result.canonical_tag == "CompTIA Network+"
    assert result.matched_via == "explicit"


def test_fuzzy_fallback_catches_near_duplicate_spelling():
    result = normalize_skill("Customer Servicee")  # typo
    assert result.canonical_tag == "Customer Service"
    assert result.matched_via == "fuzzy"
    assert result.fuzzy_score is not None and result.fuzzy_score >= 85


def test_unrelated_skill_is_left_unmapped():
    result = normalize_skill("Underwater Basket Weaving")
    assert result.canonical_tag is None
    assert result.matched_via == "unmapped"
