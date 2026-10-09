"""
tests/test_zero_storage_deployment.py
=====================================
Validation tests for Zero-Additional-Storage Cloud Deployment:
1. Production startup without private row-level Parquet datasets.
2. Mandatory model verification (9/9 frozen models) intact.
3. /api/ready probe returning 200 ready=True.
4. USA live salary prediction (USD, exact 123 predictors).
5. India live salary prediction (INR LPA, exact 290 predictors).
6. Archetype classification for USA (k=7) and India (k=6).
7. Market analytics baseline from verified aggregate research tables.
8. Dynamic cross-filtering graceful fallback (filter_unsupported=True).
9. India skill analytics loading from reports/tables/india/india_skill_analytics.json.
10. Strict research mode enforcement when JOBINTEL_STRICT_RESEARCH=1.
"""

import os
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.models.model_registry import ModelRegistry, ModelIntegrityError, get_model_registry
from src.backend.services.market_service import MarketService
from src.backend.services.india_service import IndiaService

client = TestClient(app)


def test_production_startup_without_private_parquets():
    """Verify ModelRegistry loads all 9 core models bitwise when private parquet is unmounted."""
    registry = ModelRegistry()
    orig_exists = os.path.exists

    def mock_exists(path):
        if str(path).endswith(".parquet"):
            return False
        return orig_exists(path)

    with patch("os.path.exists", side_effect=mock_exists):
        registry.initialize_and_verify()
        status = registry.get_status_report()

        assert status["status"] == "GREEN"
        assert status["mandatory_verified_count"] == 9
        assert status["artifacts"]["india_cohort"]["status"] == "UNMOUNTED_RESEARCH_COHORT"
        assert status["artifacts"]["india_cohort"]["verified"] is False
        for k in ["usa_salary_model", "india_salary_model", "usa_preprocessor", "india_preprocessor",
                  "usa_scaler", "usa_pca", "usa_kmeans", "india_pca", "india_kmeans"]:
            assert status["artifacts"][k]["status"] == "VERIFIED"
            assert status["artifacts"][k]["verified"] is True


def test_readiness_probe_unmounted():
    """Verify /api/ready probe reports ready: True when only mandatory 9 models are verified."""
    registry = get_model_registry()
    with patch.object(registry, "get_status_report", return_value={
        "status": "GREEN",
        "artifacts_verified_count": 9,
        "mandatory_verified_count": 9,
        "artifacts": {},
        "models_loaded": {},
    }):
        res = client.get("/api/ready")
        assert res.status_code == 200
        data = res.json()
        assert data["ready"] is True
        assert data["status"] == "ready"


def test_usa_prediction_without_private_parquets():
    """Verify USA live salary prediction works in USD with 123 features without any Parquet reads."""
    with patch.object(MarketService, "get_usa_cohort_df", return_value=None):
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
        assert data["predicted_salary"] > 50000
        assert "$" in data["predicted_salary_display"]
        assert data["archetype"]["archetype_available"] is True
        assert data["archetype"]["code"] in ["FOUND_TECH", "DEVOPS_PLAT", "WEB_FRONT", "CLOUD_ARCH", "DATA_BI", "AI_ML", "SYS_ENG"]


def test_india_prediction_without_private_parquets():
    """Verify India live salary prediction works in INR (LPA) with 290 features without any Parquet reads."""
    with patch.object(MarketService, "get_india_cohort_df", return_value=None):
        payload = {
            "normalized_role": "Data Engineer",
            "experience_midpoint_years": 5.0,
            "experience_range_years": 2.0,
            "city_grouped": "Bengaluru",
            "work_mode": "Hybrid",
            "selected_skills": ["skill_spark", "skill_scala", "skill_airflow", "skill_python"]
        }
        res = client.post("/api/india/predict", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["country"] == "India"
        assert data["currency"] == "INR"
        assert data["predicted_salary_lpa"] > 0
        assert "₹" in data["predicted_salary_display"]
        assert data["archetype"]["archetype_available"] is True
        assert data["archetype"]["archetype_id"] in [f"IND_ARC_0{i}" for i in range(1, 7)]


def test_archetypes_list_without_private_parquets():
    """Verify all 7 USA and 6 India archetypes are returned via API without Parquet dependencies."""
    res_usa = client.get("/api/usa/archetypes")
    assert res_usa.status_code == 200
    usa_data = res_usa.json()
    assert len(usa_data) == 7

    res_ind = client.get("/api/india/archetypes")
    assert res_ind.status_code == 200
    ind_data = res_ind.json()
    assert len(ind_data) == 6


def test_market_analytics_baseline_without_private_parquets():
    """Verify USA and India market summary baselines load from aggregate research tables."""
    with patch.object(MarketService, "get_usa_cohort_df", return_value=None), \
         patch.object(MarketService, "get_india_cohort_df", return_value=None):
        res_u = client.get("/api/usa/market-summary")
        assert res_u.status_code == 200
        u_data = res_u.json()
        assert u_data["country"] == "USA"
        assert u_data["cohort_size"] == 34036
        assert len(u_data["by_role"]) > 0
        assert len(u_data["by_location"]) > 0
        assert len(u_data["top_skills"]) > 0

        res_i = client.get("/api/india/market-summary")
        assert res_i.status_code == 200
        i_data = res_i.json()
        assert i_data["country"] == "India"
        assert i_data["cohort_size"] == 5859
        assert len(i_data["by_role"]) > 0
        assert len(i_data["by_location"]) > 0
        assert len(i_data["top_skills"]) > 0


def test_market_analytics_filtered_unsupported_when_unmounted():
    """Verify filtered requests return explicit filter_unsupported payload when private cohort is unmounted."""
    with patch.object(MarketService, "get_usa_cohort_df", return_value=None), \
         patch.object(MarketService, "get_india_cohort_df", return_value=None):
        res_u = client.get("/api/usa/market-summary?role=Data+Engineer")
        assert res_u.status_code == 200
        u_data = res_u.json()
        assert u_data.get("filter_unsupported") is True
        assert "unmounted" in u_data.get("message", "").lower()

        res_i = client.get("/api/india/market-summary?role=Software+Engineer")
        assert res_i.status_code == 200
        i_data = res_i.json()
        assert i_data.get("filter_unsupported") is True
        assert "unmounted" in i_data.get("message", "").lower()


def test_india_skills_analytics_from_reports_table():
    """Verify India skills analytics loads successfully from reports/tables/india/india_skill_analytics.json."""
    data = IndiaService.get_skills_analytics()
    assert data["country"] == "India"
    assert len(data.get("skills", [])) == 284


def test_cross_market_summary_unmounted():
    """Verify cross-market summary returns native distributions without private parquets."""
    with patch.object(MarketService, "get_usa_cohort_df", return_value=None), \
         patch.object(MarketService, "get_india_cohort_df", return_value=None):
        if hasattr(MarketService, "_cached_cross_market_analytics"):
            delattr(MarketService, "_cached_cross_market_analytics")
        res = client.get("/api/cross-market/summary")
        assert res.status_code == 200
        data = res.json()
        assert "USA vs India" in data["title"]
        assert len(data["shared_skills_prevalence"]) == 12
        assert len(data["role_demand_comparison"]) == 8


def test_strict_research_mode_preserves_local_integrity():
    """Verify JOBINTEL_STRICT_RESEARCH=1 causes ModelRegistry to fail closed if any artifact is missing."""
    registry = ModelRegistry()
    orig_exists = os.path.exists

    def mock_missing_cohort(path):
        if "india_modeling_cohort.parquet" in str(path):
            return False
        return orig_exists(path)

    with patch.dict(os.environ, {"JOBINTEL_STRICT_RESEARCH": "1"}), \
         patch("os.path.exists", side_effect=mock_missing_cohort):
        with pytest.raises((ModelIntegrityError, FileNotFoundError)) as exc_info:
            registry.verify_all_artifacts()
        assert "india_cohort" in str(exc_info.value) or "india_modeling_cohort.parquet" in str(exc_info.value)
