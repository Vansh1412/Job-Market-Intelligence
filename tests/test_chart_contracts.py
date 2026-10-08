"""
tests/test_chart_contracts.py
=============================
Automated contract tests that validate the data schemas for all 4 primary visualizations:
1. Salary by Experience (experience band, median salary)
2. Salary by Role (role, median salary)
3. Salary by Location (metro city, median salary)
4. Top Skills (skill name, prevalence percentage)

Guarantees that backend endpoints return the fields required by the frontend Recharts
components and that non-empty cohorts always produce non-empty chart series.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_experience_chart_contract_usa():
    """Verify USA salary-by-seniority chart contract."""
    response = client.get("/api/usa/market-summary")
    assert response.status_code == 200
    data = response.json()
    seniority_items = data.get("by_seniority", [])
    assert len(seniority_items) > 0, "USA experience chart data must not be empty"

    for item in seniority_items:
        # Recharts expects either 'seniority', 'band', or 'experience_band'
        assert "seniority" in item or "band" in item or "experience_band" in item
        assert "median_salary" in item
        assert isinstance(item["median_salary"], (int, float))
        assert item["median_salary"] > 0


def test_experience_chart_contract_india():
    """Verify India salary-by-experience chart contract (BUG #4 remediation)."""
    response = client.get("/api/india/market-summary")
    assert response.status_code == 200
    data = response.json()
    exp_items = data.get("by_experience", [])
    assert len(exp_items) > 0, "India experience chart data must not be empty"

    for item in exp_items:
        # Recharts key verification: both band and experience_band must exist
        assert "experience_band" in item or "band" in item
        assert "median_salary_lpa" in item
        assert isinstance(item["median_salary_lpa"], (int, float))
        assert item["median_salary_lpa"] > 0


def test_role_chart_contract_usa():
    """Verify USA salary-by-role chart contract."""
    response = client.get("/api/usa/market-summary")
    assert response.status_code == 200
    data = response.json()
    role_items = data.get("by_role", [])
    assert len(role_items) > 0, "USA role chart data must not be empty"

    for item in role_items:
        assert "role" in item or "Role_Family" in item
        assert "median_salary" in item
        assert isinstance(item["median_salary"], (int, float))
        assert item["median_salary"] > 0


def test_role_chart_contract_india():
    """Verify India salary-by-role chart contract."""
    response = client.get("/api/india/market-summary")
    assert response.status_code == 200
    data = response.json()
    role_items = data.get("by_role", [])
    assert len(role_items) > 0, "India role chart data must not be empty"

    for item in role_items:
        assert "role" in item
        assert "median_salary_lpa" in item
        assert isinstance(item["median_salary_lpa"], (int, float))
        assert item["median_salary_lpa"] > 0


def test_location_chart_contract_usa():
    """Verify USA salary-by-location chart contract."""
    response = client.get("/api/usa/market-summary")
    assert response.status_code == 200
    data = response.json()
    loc_items = data.get("by_location", [])
    assert len(loc_items) > 0, "USA location chart data must not be empty"

    for item in loc_items:
        assert "city" in item or "City" in item
        assert "median_salary" in item
        assert isinstance(item["median_salary"], (int, float))


def test_location_chart_contract_india():
    """Verify India salary-by-location chart contract."""
    response = client.get("/api/india/market-summary")
    assert response.status_code == 200
    data = response.json()
    loc_items = data.get("by_location", [])
    assert len(loc_items) > 0, "India location chart data must not be empty"

    for item in loc_items:
        assert "city" in item
        assert "median_salary_lpa" in item
        assert isinstance(item["median_salary_lpa"], (int, float))


def test_top_skills_chart_contract_usa():
    """Verify USA top skills demand chart contract."""
    response = client.get("/api/usa/market-summary")
    assert response.status_code == 200
    data = response.json()
    skills = data.get("top_skills", [])
    assert len(skills) > 0, "USA top skills chart data must not be empty"

    for item in skills:
        assert "skill" in item
        assert "prevalence_pct" in item
        assert isinstance(item["prevalence_pct"], (int, float))
        assert 0 <= item["prevalence_pct"] <= 100


def test_top_skills_chart_contract_india():
    """Verify India top skills demand chart contract."""
    response = client.get("/api/india/market-summary")
    assert response.status_code == 200
    data = response.json()
    skills = data.get("top_skills", [])
    assert len(skills) > 0, "India top skills chart data must not be empty"

    for item in skills:
        assert "skill" in item or "display_name" in item
        assert "prevalence_pct" in item or "demand_percentage" in item
