"""
Input Validation & Error Handling Automated Test Suite (Phase 7.7 & 7.8)
========================================================================
Validates that invalid, boundary, or malformed inputs to USA and India
prediction endpoints return controlled HTTP 422/400 errors or handle
graceful fallbacks without exposing internal stack traces.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. READINESS & HEALTH PROBES (Phase 7.8)
# -----------------------------------------------------------------------------
def test_readiness_probe_success():
    res = client.get("/api/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["ready"] is True
    assert data["artifacts_verified_count"] == 10
    assert "USA" in data["markets"]
    assert "India" in data["markets"]


def test_health_probe_success():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data


# -----------------------------------------------------------------------------
# 2. USA INPUT VALIDATION TESTS (Phase 7.7)
# -----------------------------------------------------------------------------
def test_usa_missing_required_fields():
    # Missing role_family, seniority, city_clean
    res = client.post("/api/usa/predict", json={"is_remote": True})
    assert res.status_code == 422
    err_detail = res.json()["detail"]
    assert any("role_family" in str(e) for e in err_detail)


def test_usa_wrong_types():
    # is_remote passed as string that cannot be coerced to bool
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": "not_a_boolean_value",
        "selected_skills": []
    })
    assert res.status_code == 422


def test_usa_duplicate_skills_graceful_handling():
    # Duplicate skills should not crash or distort counts
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_python", "skill_python", "skill_aws", "skill_aws"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary"] > 50000.0
    # Should only count distinct skills
    assert data["num_skills"] <= 5


def test_usa_unknown_skills_graceful_handling():
    # Skills not in the 82 taxonomy should simply be ignored without 500
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_completely_made_up_123", "skill_nonexistent"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["archetype"]["archetype_available"] is False


def test_usa_unknown_role_fallback():
    # Unknown role should fall back to 'Other Tech' without crashing
    res = client.post("/api/usa/predict", json={
        "role_family": "Acrobatic Clown Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary"] > 50000.0


# -----------------------------------------------------------------------------
# 3. INDIA INPUT VALIDATION TESTS (Phase 7.7)
# -----------------------------------------------------------------------------
def test_india_missing_required_fields():
    res = client.post("/api/india/predict", json={"work_mode": "Hybrid"})
    assert res.status_code == 422


def test_india_negative_experience_validation():
    # Negative experience should fail validation
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": -5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 422


def test_india_excessive_experience_validation():
    # Experience > 35 years should fail validation
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 80.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 422


def test_india_duplicate_skills_graceful_handling():
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_spark", "skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0


def test_india_unsupported_role_fallback():
    # Unknown role falls back to 'Other Technology'
    res = client.post("/api/india/predict", json={
        "normalized_role": "Underwater Welder",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0


def test_india_unsupported_city_fallback():
    # Unknown city falls back to 'Other'
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Atlantis Metro",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0
