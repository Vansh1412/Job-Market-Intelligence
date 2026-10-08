"""
JobIntel End-to-End Integration Test Suite (Phase 6.17)
=======================================================
Verifies all unified and legacy endpoints across USA and India pipelines.
Guarantees backward compatibility, schema adherence, currency isolation,
and exact archetype taxonomy mapping.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. CORE API & METADATA CONTRACTS
# -----------------------------------------------------------------------------
def test_root_and_health_contract():
    root_res = client.get("/")
    assert root_res.status_code == 200
    root_data = root_res.json()
    assert "JobIntel" in root_data["service"]
    assert "USA" in root_data["markets_supported"]
    assert "India" in root_data["markets_supported"]

    health_res = client.get("/api/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "healthy"
    assert health_data["registry"]["status"] == "GREEN"
    assert health_data["registry"]["artifacts_verified_count"] == 10


def test_meta_contract():
    res = client.get("/api/meta")
    assert res.status_code == 200
    meta = res.json()
    assert meta["governance"]["zero_retraining"] is True
    assert meta["governance"]["zero_fx_currency_conversion"] is True
    assert meta["usa_pipeline"]["cohort_size"] == 34036
    assert meta["usa_pipeline"]["feature_count"] == 123
    assert meta["india_pipeline"]["cohort_size"] == 5859
    assert meta["india_pipeline"]["feature_count"] == 290


# -----------------------------------------------------------------------------
# 2. USA PIPELINE ENDPOINT CONTRACTS
# -----------------------------------------------------------------------------
def test_usa_options():
    res = client.get("/api/usa/options")
    assert res.status_code == 200
    data = res.json()
    assert data["country"] == "USA"
    assert data["currency"] == "USD"
    assert len(data["roles"]) == 18
    assert len(data["cities"]) >= 16
    assert len(data["skills"]) == 82


def test_usa_prediction_live():
    payload = {
        "role_family": "ML / AI Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_pytorch", "skill_machine_learning"],
    }
    res = client.post("/api/usa/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["country"] == "USA"
    assert data["currency"] == "USD"
    assert data["predicted_salary"] > 100000.0
    assert "$" in data["predicted_salary_display"]
    assert "₹" not in data["predicted_salary_display"]
    assert data["archetype"]["archetype_available"] is True
    assert data["archetype"]["code"] in [
        "FOUND_TECH", "DEVOPS_PLAT", "WEB_FRONT", "CLOUD_ARCH", "DATA_BI", "AI_ML", "SYS_ENG"
    ]


def test_usa_archetypes_list():
    res = client.get("/api/usa/archetypes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7
    codes = [a["code"] for a in data]
    assert "AI_ML" in codes
    assert "CLOUD_ARCH" in codes
    assert "DATA_BI" in codes


def test_usa_market_summary():
    res = client.get("/api/usa/market-summary")
    assert res.status_code == 200
    data = res.json()
    assert data["cohort_size"] == 34036
    assert data["moments"]["median"] == 180413.0
    assert len(data["by_role"]) > 10
    assert len(data["top_skills"]) > 10


# -----------------------------------------------------------------------------
# 3. INDIA PIPELINE ENDPOINT CONTRACTS
# -----------------------------------------------------------------------------
def test_india_options():
    res = client.get("/api/india/options")
    assert res.status_code == 200
    data = res.json()
    assert data["country"] == "India"
    assert data["currency"] == "INR"
    assert len(data["roles"]) == 14
    assert len(data["cities"]) == 23
    assert len(data["work_modes"]) == 3
    assert len(data["skills"]) == 284


def test_india_prediction_live():
    payload = {
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_scala", "skill_airflow", "skill_python"],
    }
    res = client.post("/api/india/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["country"] == "India"
    assert data["currency"] == "INR"
    assert data["predicted_salary_lpa"] > 2.0
    assert "₹" in data["predicted_salary_display"]
    assert "LPA" in data["predicted_salary_display"]
    assert "$" not in data["predicted_salary_display"]
    assert data["archetype"]["archetype_available"] is True
    assert data["archetype"]["archetype_id"] == "IND_ARC_01"


def test_india_archetypes_list():
    res = client.get("/api/india/archetypes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 6
    ids = [a["archetype_id"] for a in data]
    assert ids == [f"IND_ARC_0{i}" for i in range(1, 7)]


def test_india_market_summary():
    res = client.get("/api/india/market-summary")
    assert res.status_code == 200
    data = res.json()
    assert data["cohort_size"] == 5859
    assert data["moments"]["median_lpa"] == 10.0
    assert len(data["by_role"]) == 14
    assert len(data["top_skills"]) > 10


# -----------------------------------------------------------------------------
# 4. CROSS-MARKET INTEGRITY & CURRENCY ISOLATION
# -----------------------------------------------------------------------------
def test_cross_market_contract():
    res = client.get("/api/cross-market/summary")
    assert res.status_code == 200
    data = res.json()
    assert "USA vs India" in data["title"]
    assert "Zero Currency Conversion" in data["methodology_note"] or "native currencies" in data["methodology_note"]
    assert "$" in data["usa_overview"]["median_salary_display"]
    assert "₹" in data["india_overview"]["median_salary_display"]
    assert len(data["shared_skills_prevalence"]) >= 10
    assert len(data["role_demand_comparison"]) >= 6


# -----------------------------------------------------------------------------
# 5. LEGACY BACKWARD COMPATIBILITY ENDPOINTS
# -----------------------------------------------------------------------------
def test_legacy_overview_kpis():
    res = client.get("/api/overview/kpis")
    assert res.status_code == 200
    data = res.json()
    assert "curated_corpus" in data or "archetypes_count" in data


def test_legacy_salary_summary():
    res = client.get("/api/salary/summary")
    assert res.status_code == 200


def test_legacy_skills_frequency():
    res = client.get("/api/skills/frequency")
    assert res.status_code == 200


def test_legacy_models_benchmarks():
    res = client.get("/api/models/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert "cv_comparison" in data
    assert "test_results" in data


def test_legacy_error_analysis():
    res = client.get("/api/error-analysis/archetype-breakdown")
    assert res.status_code == 200
