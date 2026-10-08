"""
Generation and Verification of Golden Predictions for USA and India Pipelines
=============================================================================
Computes direct on-disk model predictions vs API predictions for fixed deterministic
reference profiles and writes test fixtures to tests/golden_predictions/.
"""

import json
import os
import joblib
import pickle
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, ".")

from src.backend.main import app
from src.backend.services.usa_service import USAService
from src.backend.services.india_service import IndiaService

client = TestClient(app)

USA_GOLDEN_PROFILES = [
    {
        "id": "USA_GOLDEN_01_ML_AI",
        "name": "USA Senior ML/AI Engineer in San Francisco",
        "role_family": "ML / AI Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_pytorch", "skill_machine_learning", "skill_deep_learning"],
    },
    {
        "id": "USA_GOLDEN_02_BACKEND",
        "name": "USA Mid Backend Developer in New York",
        "role_family": "Backend Developer",
        "seniority": "Mid / Unspecified",
        "city_clean": "New York",
        "is_remote": False,
        "selected_skills": ["skill_java", "skill_sql", "skill_docker", "skill_kubernetes"],
    },
    {
        "id": "USA_GOLDEN_03_CLOUD_DATA",
        "name": "USA Lead Data Engineer in Seattle",
        "role_family": "Data Engineer",
        "seniority": "Lead / Principal / Executive",
        "city_clean": "Seattle",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_sql", "skill_aws", "skill_spark", "skill_snowflake"],
    },
]

INDIA_GOLDEN_PROFILES = [
    {
        "id": "IND_GOLDEN_01_PYTHON_AI",
        "name": "India Mid Data Scientist in Bengaluru",
        "normalized_role": "Data Scientist",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_python", "skill_machine_learning", "skill_deep_learning", "skill_nlp"],
    },
    {
        "id": "IND_GOLDEN_02_JAVA_MICROSERVICES",
        "name": "India Mid Backend Developer in Hyderabad",
        "normalized_role": "Backend Developer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Hyderabad",
        "work_mode": "In-office",
        "selected_skills": ["skill_java", "skill_spring_boot", "skill_microservices", "skill_mysql"],
    },
    {
        "id": "IND_GOLDEN_03_DATA_ENGINEERING",
        "name": "India Senior Data Engineer in Pune",
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 7.0,
        "experience_range_years": 3.0,
        "city_grouped": "Pune",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_scala", "skill_airflow", "skill_python", "skill_sql"],
    },
]


def run_golden_generation():
    os.makedirs("tests/golden_predictions", exist_ok=True)

    # 1. Load frozen USA models directly
    with open("models/phase5/best_model.pkl", "rb") as f:
        usa_raw_model = joblib.load(f)

    # 2. Load frozen India models directly
    with open("models/india/final_model.pkl", "rb") as f:
        ind_raw_model = pickle.load(f)
    with open("models/india/final_preprocessor.pkl", "rb") as f:
        ind_raw_prep = pickle.load(f)

    results = {"usa": [], "india": []}

    print("--- USA GOLDEN PREDICTIONS ---")
    for p in USA_GOLDEN_PROFILES:
        # Direct
        X_vec, _ = USAService.build_feature_vector(
            p["role_family"], p["seniority"], p["city_clean"], p["is_remote"], p["selected_skills"]
        )
        direct_pred = float(usa_raw_model.predict(X_vec)[0])

        # API
        res = client.post("/api/usa/predict", json={
            "role_family": p["role_family"],
            "seniority": p["seniority"],
            "city_clean": p["city_clean"],
            "is_remote": p["is_remote"],
            "selected_skills": p["selected_skills"],
        })
        api_data = res.json()
        api_pred = float(api_data["predicted_salary"])

        diff = abs(direct_pred - api_pred)
        print(f"[{p['id']}] Direct: ${direct_pred:,.2f} | API: ${api_pred:,.2f} | Diff: ${diff:.4f}")
        assert diff < 0.1, f"Parity mismatch for {p['id']}: {diff}"

        results["usa"].append({
            "id": p["id"],
            "profile": p,
            "direct_prediction_usd": round(direct_pred, 2),
            "api_prediction_usd": round(api_pred, 2),
            "delta_usd": round(diff, 4),
            "predicted_salary_display": api_data["predicted_salary_display"],
            "archetype_assigned": api_data["archetype"]["code"],
        })

    print("\n--- INDIA GOLDEN PREDICTIONS ---")
    for p in INDIA_GOLDEN_PROFILES:
        # Direct
        ind_df, _, _ = IndiaService.build_feature_dataframe(
            p["normalized_role"],
            p["experience_midpoint_years"],
            p["experience_range_years"],
            p["city_grouped"],
            p["work_mode"],
            p["selected_skills"],
        )
        direct_log_pred = float(ind_raw_model.predict(ind_raw_prep.transform(ind_df))[0])
        direct_lpa = float(np.expm1(direct_log_pred)) / 100000.0

        # API
        res = client.post("/api/india/predict", json={
            "normalized_role": p["normalized_role"],
            "experience_midpoint_years": p["experience_midpoint_years"],
            "experience_range_years": p["experience_range_years"],
            "city_grouped": p["city_grouped"],
            "work_mode": p["work_mode"],
            "selected_skills": p["selected_skills"],
        })
        api_data = res.json()
        api_lpa = float(api_data["predicted_salary_lpa"])

        diff = abs(direct_lpa - api_lpa)
        print(f"[{p['id']}] Direct: {direct_lpa:.4f} LPA | API: {api_lpa:.4f} LPA | Diff: {diff:.6f} LPA")
        assert diff < 0.01, f"Parity mismatch for {p['id']}: {diff}"

        results["india"].append({
            "id": p["id"],
            "profile": p,
            "direct_prediction_lpa": round(direct_lpa, 4),
            "api_prediction_lpa": round(api_lpa, 4),
            "delta_lpa": round(diff, 6),
            "predicted_salary_display": api_data["predicted_salary_display"],
            "archetype_assigned": api_data["archetype"]["archetype_id"],
        })

    out_path = "tests/golden_predictions/golden_predictions_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved golden predictions manifest: {out_path}")


if __name__ == "__main__":
    run_golden_generation()
