from src.scoring import rank_opportunities_for_student, score_match


def test_score_match_computes_fraction_of_requirements_met():
    student_tags = {"CompTIA A+", "Customer Service"}
    opportunity_tags = {"CompTIA A+", "Customer Service", "Microsoft Excel"}

    result = score_match("S001", "O001", student_tags, opportunity_tags)

    assert result.score == round(2 / 3, 4)
    assert result.matched_skills == ["CompTIA A+", "Customer Service"]
    assert result.missing_skills == ["Microsoft Excel"]


def test_score_match_handles_empty_requirements():
    result = score_match("S001", "O001", {"CompTIA A+"}, set())
    assert result.score == 0.0
    assert result.matched_skills == []
    assert result.missing_skills == []


def test_rank_opportunities_orders_best_fit_first():
    student_tags = {"CompTIA A+", "Customer Service"}
    opportunities = {
        "O001": {"CompTIA A+", "Customer Service", "Microsoft Excel"},  # 2/3
        "O002": {"CompTIA A+", "Customer Service"},  # 2/2, best
        "O003": {"AWS Cloud Practitioner"},  # 0/1, worst
    }

    ranked = rank_opportunities_for_student("S001", student_tags, opportunities)

    assert [r.opportunity_id for r in ranked] == ["O002", "O001", "O003"]
    assert ranked[0].score == 1.0
    assert ranked[-1].score == 0.0
