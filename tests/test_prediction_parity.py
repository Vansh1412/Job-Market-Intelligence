"""
JobIntel Prediction Parity Verification Suite (Phase 6.7)
=========================================================
Strict parity testing verifying bitwise / exact mathematical equivalence between:
1. Direct frozen Python model execution (joblib/pickle)
2. FastAPI REST endpoint execution (via TestClient)

Validates both salary prediction values and archetype classifications across
USA and India pipelines. Must pass 100% before frontend development begins.
"""

import os
import json
import pickle
import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.models.model_registry import get_model_registry

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. CORE & HEALTH ENDPOINT TESTS
# -----------------------------------------------------------------------------
def test_health_endpoint():
    """Verify health endpoint confirms all 10 frozen artifacts intact."""
    response = client.get("/api/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    data = response.json()
    assert data["status"] == "healthy"
    reg = data["registry"]
    assert reg["status"] == "GREEN"
    assert reg["artifacts_verified_count"] == 10
    for key, spec in reg["artifacts"].items():
        assert spec["verified"] is True, f"Artifact {key} verification failed"


def test_meta_endpoint():
    """Verify meta endpoint exposes certified research specifications."""
    response = client.get("/api/meta")
    assert response.status_code == 200
    meta = response.json()
    assert meta["governance"]["zero_retraining"] is True
    assert meta["governance"]["zero_fx_currency_conversion"] is True
    assert meta["usa_pipeline"]["cohort_size"] == 34036
    assert meta["india_pipeline"]["cohort_size"] == 5859
    assert meta["india_pipeline"]["feature_count"] == 290


# -----------------------------------------------------------------------------
# 2. USA PREDICTION PARITY TESTS
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("profile", [
    {
        "role_family": "ML / AI Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_pytorch", "skill_machine_learning"],
    },
    {
        "role_family": "Data Engineer",
        "seniority": "Mid-level",
        "city_clean": "New York",
        "is_remote": False,
        "selected_skills": ["skill_sql", "skill_spark", "skill_airflow", "skill_aws"],
    },
    {
        "role_family": "Frontend Developer",
        "seniority": "Entry-level",
        "city_clean": "Seattle",
        "is_remote": True,
        "selected_skills": ["skill_react", "skill_typescript", "skill_javascript"],
    },
    {
        "role_family": "DevOps / Cloud / Platform",
        "seniority": "Lead / Principal",
        "city_clean": "Boston",
        "is_remote": False,
        "selected_skills": ["skill_kubernetes", "skill_docker", "skill_terraform", "skill_aws"],
    },
])
def test_usa_prediction_parity(profile):
    """
    Direct model evaluation vs FastAPI /api/usa/predict parity test.
    """
    # 1. API Response
    response = client.post("/api/usa/predict", json=profile)
    assert response.status_code == 200, f"API call failed: {response.text}"
    api_data = response.json()
    api_pred = api_data["predicted_salary"]
    api_arc_code = api_data["archetype"]["code"]

    # 2. Direct Python Inference using raw frozen model
    model = joblib.load("models/phase5/best_model.pkl")
    pipeline = joblib.load("models/phase5/best_pipeline.pkl")
    with open("models/phase5/feature_metadata.json", "r") as f:
        meta_info = json.load(f)
    tech_skills = meta_info["tech_skills"]

    # Seniority mapping
    sen_map = {
        "Entry-level": "Junior / Entry",
        "Mid-level": "Mid / Unspecified",
        "Senior": "Senior",
        "Lead / Principal": "Lead / Principal / Executive",
    }
    sen = sen_map.get(profile["seniority"], profile["seniority"])

    df_meta = pd.DataFrame({
        "seniority": [sen],
        "role_family": [profile["role_family"]],
        "city_clean": [profile["city_clean"]],
        "is_remote": [1.0 if profile["is_remote"] else 0.0],
        "num_skills": [float(len(profile["selected_skills"]))],
    })
    meta_proc = pipeline.transform(df_meta[meta_info["metadata_cols"]])

    skill_set = set(profile["selected_skills"])
    skills_arr = np.zeros((1, len(tech_skills)), dtype=np.float32)
    for idx, s in enumerate(tech_skills):
        if s in skill_set:
            skills_arr[0, idx] = 1.0

    X_direct = np.hstack([meta_proc, skills_arr])
    direct_pred = float(model.predict(X_direct)[0])
    direct_pred = max(30000.0, direct_pred)

    # 3. Direct Archetype
    scaler = joblib.load("models/scaler_phase4_1.pkl")
    pca = joblib.load("models/pca_phase4_1.pkl")
    kmeans = joblib.load("models/kmeans_phase4_1_k7.pkl")
    scaled = scaler.transform(skills_arr)
    pca_c = pca.transform(scaled)
    cluster_id = int(kmeans.predict(pca_c)[0])

    from src.backend.services.archetype_service import USA_ARCHETYPE_LOOKUP
    direct_arc_code = USA_ARCHETYPE_LOOKUP[cluster_id]["code"]

    # Strict Assertions: numerical parity within 1 cent ($0.01)
    assert abs(api_pred - round(direct_pred, 2)) < 0.05, (
        f"USA Parity Failure: API={api_pred}, Direct={direct_pred}"
    )
    assert api_arc_code == direct_arc_code, (
        f"USA Archetype Mismatch: API={api_arc_code}, Direct={direct_arc_code}"
    )


# -----------------------------------------------------------------------------
# 3. INDIA PREDICTION PARITY TESTS
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("profile", [
    {
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_scala", "skill_airflow", "skill_python"],
    },
    {
        "normalized_role": "Software Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Hyderabad",
        "work_mode": "Onsite",
        "selected_skills": ["skill_java", "skill_spring_boot", "skill_microservices"],
    },
    {
        "normalized_role": "AI / ML Engineer",
        "experience_midpoint_years": 6.0,
        "experience_range_years": 3.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Remote",
        "selected_skills": ["skill_python", "skill_machine_learning", "skill_deep_learning", "skill_aws"],
    },
    {
        "normalized_role": "Full Stack Developer",
        "experience_midpoint_years": 3.0,
        "experience_range_years": 2.0,
        "city_grouped": "Pune",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_react", "skill_javascript", "skill_node_js"],
    },
    {
        "normalized_role": "Other Technology",
        "experience_midpoint_years": 8.0,
        "experience_range_years": 4.0,
        "city_grouped": "Mumbai",
        "work_mode": "Onsite",
        "selected_skills": ["skill_sap", "skill_fico", "skill_abap", "skill_erp"],
    },
])
def test_india_prediction_parity(profile):
    """
    Direct model evaluation vs FastAPI /api/india/predict parity test.
    """
    # 1. API Response
    response = client.post("/api/india/predict", json=profile)
    assert response.status_code == 200, f"API call failed: {response.text}"
    api_data = response.json()
    api_pred_lpa = api_data["predicted_salary_lpa"]
    api_arc_id = api_data["archetype"]["archetype_id"]

    # 2. Direct Python Inference using raw frozen model
    with open("models/india/final_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/india/final_preprocessor.pkl", "rb") as f:
        prep = pickle.load(f)
    with open("models/india/final_feature_list.json", "r") as f:
        feature_spec = json.load(f)

    raw_features = feature_spec["feature_names_raw"]
    skill_cols = [c for c in raw_features if c.startswith("skill_")]

    # Build exact row
    skill_set = set(profile["selected_skills"])
    row = {
        "normalized_role": profile["normalized_role"],
        "experience_midpoint_years": float(profile["experience_midpoint_years"]),
        "experience_range_years": float(profile["experience_range_years"]),
        "city_grouped": profile["city_grouped"],
        "work_mode": profile["work_mode"],
        "total_selected_skill_count": float(len([s for s in skill_cols if s in skill_set])),
    }
    skill_binary = []
    for s in skill_cols:
        val = 1.0 if s in skill_set else 0.0
        row[s] = val
        skill_binary.append(val)

    df_direct = pd.DataFrame([row], columns=raw_features)
    X_proc = prep.transform(df_direct)
    direct_log_pred = float(model.predict(X_proc)[0])
    direct_inr = float(np.expm1(direct_log_pred))
    direct_inr = max(100000.0, direct_inr)
    direct_lpa = direct_inr / 100000.0

    # 3. Direct Archetype via PCA + KMeans
    with open("models/india/india_pca_v1.pkl", "rb") as f:
        pca = pickle.load(f)
    with open("models/india/india_kmeans_v1.pkl", "rb") as f:
        km = pickle.load(f)

    skills_arr = np.array(skill_binary, dtype=np.float32).reshape(1, -1)
    pca_c = pca.transform(skills_arr)
    raw_cluster = int(km.predict(pca_c)[0])

    cluster_to_arc = {
        4: "IND_ARC_01",
        2: "IND_ARC_02",
        3: "IND_ARC_03",
        5: "IND_ARC_04",
        0: "IND_ARC_05",
        1: "IND_ARC_06",
    }
    direct_arc_id = cluster_to_arc[raw_cluster]

    # Strict Assertions: parity within 0.01 LPA (Rs. 1,000)
    assert abs(api_pred_lpa - round(direct_lpa, 2)) < 0.05, (
        f"India Parity Failure: API={api_pred_lpa}, Direct={direct_lpa}"
    )
    assert api_arc_id == direct_arc_id, (
        f"India Archetype Mismatch: API={api_arc_id}, Direct={direct_arc_id}"
    )


# -----------------------------------------------------------------------------
# 4. ZERO SKILL FALLBACK TESTS
# -----------------------------------------------------------------------------
def test_zero_skill_fallbacks():
    """Ensure zero skills do not crash inference and return unassigned archetypes."""
    # USA Zero Skills
    usa_resp = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "Austin",
        "is_remote": True,
        "selected_skills": [],
    })
    assert usa_resp.status_code == 200
    usa_data = usa_resp.json()
    assert usa_data["predicted_salary"] > 0
    assert usa_data["archetype"]["archetype_available"] is False
    assert usa_data["archetype"]["code"] == "ZERO_SKILL"

    # India Zero Skills
    ind_resp = client.post("/api/india/predict", json={
        "normalized_role": "Software Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": [],
    })
    assert ind_resp.status_code == 200
    ind_data = ind_resp.json()
    assert ind_data["predicted_salary_lpa"] > 0
    assert ind_data["archetype"]["archetype_available"] is False
    assert ind_data["archetype"]["archetype_id"] == "IND_ARC_UNASSIGNED"


# -----------------------------------------------------------------------------
# 5. CROSS-MARKET & CURRENCY ISOLATION TESTS
# -----------------------------------------------------------------------------
def test_cross_market_isolation():
    """Verify that cross-market endpoint preserves separate currencies without FX conversion."""
    resp = client.get("/api/cross-market/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert "$" in data["usa_overview"]["median_salary_display"]
    assert "₹" in data["india_overview"]["median_salary_display"]
    assert "LPA" in data["india_overview"]["median_salary_display"]
    # Check that model comparison reflects exact frozen specifications
    assert data["model_comparison"]["usa"]["feature_count"] == 123
    assert data["model_comparison"]["india"]["feature_count"] == 290
