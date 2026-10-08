"""
Golden Prediction Automated Regression Test Suite (Phase 7.4)
=============================================================
Enforces deterministic parity between direct frozen on-disk model execution
and live FastAPI endpoints across 6 certified cross-market golden profiles.
"""

import json
import os
import joblib
import pickle
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.services.usa_service import USAService
from src.backend.services.india_service import IndiaService

client = TestClient(app)

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "golden_predictions", "golden_predictions_manifest.json")


@pytest.fixture(scope="module")
def golden_manifest():
    assert os.path.exists(MANIFEST_PATH), f"Golden manifest missing at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_usa_golden_predictions_parity(golden_manifest):
    with open("models/phase5/best_model.pkl", "rb") as f:
        usa_raw_model = joblib.load(f)

    for item in golden_manifest["usa"]:
        p = item["profile"]
        # Direct inference
        X_vec, _ = USAService.build_feature_vector(
            p["role_family"], p["seniority"], p["city_clean"], p["is_remote"], p["selected_skills"]
        )
        direct_pred = float(usa_raw_model.predict(X_vec)[0])

        # API inference
        res = client.post("/api/usa/predict", json={
            "role_family": p["role_family"],
            "seniority": p["seniority"],
            "city_clean": p["city_clean"],
            "is_remote": p["is_remote"],
            "selected_skills": p["selected_skills"],
        })
        assert res.status_code == 200, f"API failed for {item['id']}: {res.text}"
        api_data = res.json()
        api_pred = float(api_data["predicted_salary"])

        # Numerical parity (< $0.10 tolerance)
        diff = abs(direct_pred - api_pred)
        assert diff < 0.10, f"USA Golden Parity failed for {item['id']}: Direct {direct_pred} != API {api_pred}"

        # Manifest consistency (< $0.50 tolerance)
        assert abs(api_pred - item["api_prediction_usd"]) < 0.50
        assert api_data["archetype"]["code"] == item["archetype_assigned"]


def test_india_golden_predictions_parity(golden_manifest):
    with open("models/india/final_model.pkl", "rb") as f:
        ind_raw_model = pickle.load(f)
    with open("models/india/final_preprocessor.pkl", "rb") as f:
        ind_raw_prep = pickle.load(f)

    for item in golden_manifest["india"]:
        p = item["profile"]
        # Direct inference
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

        # API inference
        res = client.post("/api/india/predict", json={
            "normalized_role": p["normalized_role"],
            "experience_midpoint_years": p["experience_midpoint_years"],
            "experience_range_years": p["experience_range_years"],
            "city_grouped": p["city_grouped"],
            "work_mode": p["work_mode"],
            "selected_skills": p["selected_skills"],
        })
        assert res.status_code == 200, f"API failed for {item['id']}: {res.text}"
        api_data = res.json()
        api_lpa = float(api_data["predicted_salary_lpa"])

        # Numerical parity (< 0.05 LPA tolerance)
        diff = abs(direct_lpa - api_lpa)
        assert diff < 0.05, f"India Golden Parity failed for {item['id']}: Direct {direct_lpa} != API {api_lpa}"

        # Manifest consistency
        assert abs(api_lpa - item["api_prediction_lpa"]) < 0.05
        assert api_data["archetype"]["archetype_id"] == item["archetype_assigned"]
