import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.services.india_service import IndiaService
from src.backend.routers.skills import get_skill_detail

client = TestClient(app)


def test_usa_skill_denominator_lineage_and_prevalence():
    """Verify that USA skill detail returns the true 335,995 general corpus denominator, not the 34,036 salary model size."""
    detail = get_skill_detail("python")
    assert detail["skill"] == "python"
    assert detail["postings"] == 31676
    assert detail["population_size"] == 335995
    assert detail["market"] == "USA"
    assert detail["population_type"] == "Deduplicated Tech & General Job Postings Corpus"
    assert detail["population_size"] != 34036, "MUST NOT use salary-model training sample size as skill denominator!"

    # Verify mathematical quotient: 31,676 / 335,995 = 9.4275% -> rounds to 9.4%
    calc_prev = (detail["postings"] / detail["population_size"]) * 100.0
    assert abs(calc_prev - detail["prevalence_pct"]) < 0.05
    assert round(calc_prev, 1) == 9.4


def test_india_skill_denominator_lineage_and_prevalence():
    """Verify that India skill detail returns the verified 5,323 active skill-bearing cohort denominator, not 5,859."""
    detail = IndiaService.get_skill_detail("Development")
    assert detail is not None
    assert detail["posting_count"] == 723
    assert detail["population_size"] == 5323
    assert detail["market"] == "India"
    assert detail["population_size"] != 5859, "MUST NOT use unfiltered cohort size; must use active skill-bearing cohort!"

    # Verify mathematical quotient: 723 / 5,323 = 13.582% -> rounds to 13.6%
    calc_prev = (detail["posting_count"] / detail["population_size"]) * 100.0
    assert abs(calc_prev - detail["demand_percentage"]) < 0.15
    assert round(calc_prev, 1) == 13.6


def test_skills_api_http_endpoints_return_verified_denominators():
    """Verify that HTTP endpoints expose the verified population metadata."""
    res_usa = client.get("/api/skills/detail/python")
    assert res_usa.status_code == 200
    usa_data = res_usa.json()
    assert usa_data["population_size"] == 335995
    assert usa_data["population_size"] != 34036

    res_ind = client.get("/api/india/skills/Development")
    assert res_ind.status_code == 200
    ind_data = res_ind.json()
    assert ind_data["population_size"] == 5323
    assert ind_data["population_size"] != 5859


def test_all_india_skills_prevalence_quotients():
    """Verify every skill in the India analytics table reconciles against the 5,323 active subpopulation."""
    analytics = IndiaService.get_skills_analytics()
    skills = analytics.get("skills", [])
    assert len(skills) > 0

    for s in skills:
        cnt = s.get("posting_count", 0)
        pct = s.get("demand_percentage", 0.0)
        calc_pct = (cnt / 5323.0) * 100.0
        # Allow minor delta (<= 0.2%) due to floating point and table rounding
        assert abs(calc_pct - pct) < 0.25, f"Skill {s.get('skill')} failed quotient check: {cnt}/5323 = {calc_pct:.2f}% vs {pct}%"
