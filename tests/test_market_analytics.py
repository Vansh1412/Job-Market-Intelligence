"""
tests/test_market_analytics.py
==============================
Validates that market analytics endpoints for both USA and India return genuine,
empirically computed statistics without hardcoded synthetic values.
Tests dynamic cross-filtering (role, seniority/experience, location, skill)
and validates macro KPI calculations.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_usa_market_summary_baseline():
    """Verify USA market summary baseline returns expected empirical cohort values."""
    response = client.get("/api/usa/market-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "USA"
    assert data["cohort_size"] == 34036
    assert data["moments"]["median"] == 180413.0
    assert "kpis" in data
    assert data["kpis"]["median_salary_formatted"] == "$180,413 / yr"
    assert data["kpis"]["largest_role_group"] == "Software Engineer"
    assert len(data["by_role"]) > 0
    assert len(data["by_seniority"]) > 0
    assert len(data["by_location"]) > 0
    assert len(data["top_skills"]) > 0


def test_usa_market_summary_filtered():
    """Verify USA market summary dynamically filters when role or location is supplied."""
    response = client.get("/api/usa/market-summary?role=Software+Engineer")
    assert response.status_code == 200
    data = response.json()
    assert data["cohort_size"] > 0
    assert data["cohort_size"] < 34036
    assert "kpis" in data
    assert data["kpis"]["largest_role_group"] == "Software Engineer"


def test_india_market_summary_baseline():
    """Verify India market summary baseline returns expected empirical cohort values."""
    response = client.get("/api/india/market-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "India"
    assert data["cohort_size"] == 5859
    assert data["moments"]["median_lpa"] == 10.0
    assert "kpis" in data
    assert "median_salary_formatted" in data["kpis"]
    assert "typical_experience" in data["kpis"]
    assert len(data["by_role"]) > 0
    assert len(data["by_experience"]) > 0
    assert len(data["by_location"]) > 0
    assert len(data["top_skills"]) > 0


def test_india_market_summary_filtered():
    """Verify India market summary dynamically cross-filters on role and experience."""
    response = client.get("/api/india/market-summary?role=Data+Engineer")
    assert response.status_code == 200
    data = response.json()
    assert data["cohort_size"] > 0
    assert data["cohort_size"] < 5859
    # The role list in the filtered summary should reflect the filtered cohort
    assert any(r["role"] == "Data Engineer" for r in data["by_role"])


def test_empty_state_handling():
    """Verify filtering that returns 0 postings yields an honest empty state, not fake numbers."""
    response = client.get("/api/india/market-summary?role=NonexistentRole123")
    assert response.status_code == 200
    data = response.json()
    assert data["cohort_size"] == 0
    assert data.get("empty_state") is True
    assert data["kpis"]["median_salary_formatted"] == "N/A"
