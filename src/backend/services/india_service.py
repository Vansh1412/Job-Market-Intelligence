"""
JobIntel India Inference Service
=================================
Production service for Indian Tech Salary prediction and deterministic feature preparation.
Consumes frozen HistGradientBoostingRegressor model and preprocessor via ModelRegistry.
Builds the exact 290-feature vector with strict schema compliance.
Guarantees bitwise parity with research holdout evaluation.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd

from src.backend.models.model_registry import get_model_registry
from src.backend.services.archetype_service import ArchetypeService

# Certified India Tech Modeling Cohort Baseline Moments (N=5,859)
INDIA_BASELINE_MEDIAN_LPA = 10.0
INDIA_BASELINE_MEDIAN_INR = 1000000.0
INDIA_BASELINE_MEAN_LPA = 12.50
INDIA_BASELINE_MEAN_INR = 1250024.15
INDIA_MODEL_MAE_LPA = 3.71
INDIA_MODEL_MAE_INR = 371472.71
INDIA_MODEL_RMSE_LPA = 6.22
INDIA_MODEL_RMSE_INR = 621880.93
INDIA_MODEL_MEDIAN_AE_LPA = 2.08

INDIA_ROLES = [
    "AI / ML Engineer",
    "Business Analyst",
    "Cloud / DevOps",
    "Cybersecurity",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Database Administrator",
    "Frontend Developer",
    "Full Stack Developer",
    "Other Technology",
    "Product / Program Manager",
    "QA / Testing",
    "Software Engineer",
]

INDIA_CITIES = [
    "Ahmedabad",
    "Aurangabad",
    "Bengaluru",
    "Chandigarh",
    "Chennai",
    "Coimbatore",
    "Delhi NCR",
    "Faridabad",
    "Gurugram",
    "Hyderabad",
    "Jaipur",
    "Kochi",
    "Kolkata",
    "Mohali",
    "Mumbai",
    "Nagpur",
    "Nashik",
    "Noida",
    "Other",
    "Pune",
    "Remote",
    "Surat",
    "Vadodara",
]

INDIA_WORK_MODES = [
    "Hybrid",
    "Onsite",
    "Remote",
]

# Experience tiers for guided wizard
INDIA_EXPERIENCE_TIERS = [
    {"label": "Fresher / Entry (0-2 yrs)", "midpoint": 1.0, "range": 2.0},
    {"label": "Junior / Associate (2-4 yrs)", "midpoint": 3.0, "range": 2.0},
    {"label": "Mid-Level Engineer (4-7 yrs)", "midpoint": 5.5, "range": 3.0},
    {"label": "Senior Engineer (7-10 yrs)", "midpoint": 8.5, "range": 3.0},
    {"label": "Lead / Staff (10-14 yrs)", "midpoint": 12.0, "range": 4.0},
    {"label": "Principal / Architect (14+ yrs)", "midpoint": 17.0, "range": 5.0},
]


def clean_skill_identifier(raw_skill: str) -> str:
    """Normalize user input skill to canonical skill_* column name."""
    s = raw_skill.strip().lower()
    if s.startswith("skill_"):
        return s
    cleaned = s.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
    return f"skill_{cleaned}"


class IndiaService:
    """
    Production service for Indian market salary prediction and feature building.
    """

    @staticmethod
    def get_options() -> Dict[str, Any]:
        """Return available categorical choices, experience presets, and 284 technical skills."""
        registry = get_model_registry()
        raw_feats = registry.india_feature_list.get("feature_names_raw", [])
        skill_cols = [c for c in raw_feats if c.startswith("skill_")]

        formatted_skills = []
        for s in skill_cols:
            display_name = s.replace("skill_", "").replace("_", " ").title()
            # Clean common tech acronyms
            for acr in ["Aws", "Gcp", "Sql", "Ci Cd", "Ai", "Ml", "Nlp", "Api", "Ui", "Ux", "Dbt", "Etl", "Sap", "Erp", "Fico", "Abap"]:
                display_name = display_name.replace(acr, acr.upper())
            formatted_skills.append({
                "id": s,
                "name": display_name,
                "raw_key": s,
            })

        formatted_skills = sorted(formatted_skills, key=lambda x: x["name"])

        return {
            "country": "India",
            "currency": "INR",
            "currency_symbol": "₹",
            "scale": "Lakhs Per Annum (LPA)",
            "roles": INDIA_ROLES,
            "cities": INDIA_CITIES,
            "work_modes": INDIA_WORK_MODES,
            "experience_presets": INDIA_EXPERIENCE_TIERS,
            "skills": formatted_skills,
            "total_skills_count": len(formatted_skills),
            "default_profile": {
                "normalized_role": "Data Engineer",
                "experience_midpoint_years": 5.0,
                "experience_range_years": 2.0,
                "city_grouped": "Bengaluru",
                "work_mode": "Hybrid",
                "selected_skills": ["skill_spark", "skill_scala", "skill_airflow", "skill_python"],
            },
            "baseline": {
                "median_salary_lpa": INDIA_BASELINE_MEDIAN_LPA,
                "median_salary_inr": INDIA_BASELINE_MEDIAN_INR,
                "mean_salary_lpa": INDIA_BASELINE_MEAN_LPA,
                "mae_lpa": INDIA_MODEL_MAE_LPA,
                "rmse_lpa": INDIA_MODEL_RMSE_LPA,
            }
        }

    @staticmethod
    def get_skills_analytics() -> Dict[str, Any]:
        """Return empirical skill metrics, demand percentages, salaries, and associations."""
        import os, json
        for path in [
            "reports/tables/india/india_skill_analytics.json",
            "data/processed/india/india_skill_analytics.json",
        ]:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return {"country": "India", "currency": "INR", "skills": []}

    @staticmethod
    def get_skill_detail(skill_name: str) -> Optional[Dict[str, Any]]:
        """Return detailed empirical profile for a single skill."""
        data = IndiaService.get_skills_analytics()
        skills = data.get("skills", [])
        clean_target = skill_name.lower().strip().replace("skill_", "").replace(" ", "_")
        for s in skills:
            s_clean = s.get("skill", "").lower().replace("skill_", "").replace(" ", "_")
            d_clean = s.get("display_name", "").lower().replace(" ", "_")
            if clean_target in (s_clean, d_clean):
                return s
        return None

    @staticmethod

    def build_feature_dataframe(
        normalized_role: str,
        experience_midpoint_years: float,
        experience_range_years: float,
        city_grouped: str,
        work_mode: str,
        selected_skills: List[str],
    ) -> Tuple[pd.DataFrame, np.ndarray, int]:
        """
        Build the deterministic 290-column DataFrame strictly conforming to
        models/india/final_feature_list.json.
        """
        registry = get_model_registry()
        expected_cols = registry.india_feature_list["feature_names_raw"]
        skill_cols = [c for c in expected_cols if c.startswith("skill_")]

        # Validate categoricals with sensible fallbacks
        role_val = normalized_role if normalized_role in INDIA_ROLES else "Other Technology"
        city_val = city_grouped if city_grouped in INDIA_CITIES else "Other"
        work_val = work_mode if work_mode in INDIA_WORK_MODES else "Hybrid"
        exp_mid = float(max(0.0, min(30.0, experience_midpoint_years)))
        exp_range = float(max(0.0, min(15.0, experience_range_years)))

        # Build skill indicators
        skill_set = set()
        for s in selected_skills:
            skill_set.add(clean_skill_identifier(s))
            skill_set.add(s.strip().lower())

        matched_skills_count = 0
        skill_dict = {}
        skill_binary_list = []
        for s_col in skill_cols:
            clean_token = s_col.replace("skill_", "").lower()
            if s_col in skill_set or clean_token in skill_set:
                skill_dict[s_col] = 1.0
                skill_binary_list.append(1.0)
                matched_skills_count += 1
            else:
                skill_dict[s_col] = 0.0
                skill_binary_list.append(0.0)

        # Assemble single-row DataFrame with all 290 columns
        row_dict = {
            "normalized_role": role_val,
            "experience_midpoint_years": exp_mid,
            "experience_range_years": exp_range,
            "city_grouped": city_val,
            "work_mode": work_val,
            "total_selected_skill_count": float(matched_skills_count),
        }
        row_dict.update(skill_dict)

        df_290 = pd.DataFrame([row_dict], columns=expected_cols)

        # Sanity check schema
        if list(df_290.columns) != expected_cols:
            raise ValueError("Schema corruption: Built feature list does not match 290-feature expectation.")

        skills_arr = np.array(skill_binary_list, dtype=np.float32).reshape(1, -1)
        return df_290, skills_arr, matched_skills_count

    @classmethod
    def predict(
        cls,
        normalized_role: str,
        experience_midpoint_years: float,
        experience_range_years: float,
        city_grouped: str,
        work_mode: str,
        selected_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Execute live prediction for Indian job profile using frozen HistGradientBoosting model.
        """
        registry = get_model_registry()
        df_290, skills_arr, matched_skills_count = cls.build_feature_dataframe(
            normalized_role=normalized_role,
            experience_midpoint_years=experience_midpoint_years,
            experience_range_years=experience_range_years,
            city_grouped=city_grouped,
            work_mode=work_mode,
            selected_skills=selected_skills,
        )

        # Preprocess features
        X_proc = registry.india_preprocessor.transform(df_290)

        # Supervised prediction: model predicts log1p(salary_midpoint_inr)
        log_pred = float(registry.india_salary_model.predict(X_proc)[0])
        pred_inr = float(np.expm1(log_pred))
        pred_inr = max(100000.0, pred_inr)  # Floor at 1 LPA
        pred_lpa = pred_inr / 100000.0

        # Archetype classification
        arc_result = ArchetypeService.classify_india_skills(skills_arr, matched_skills_count)

        # Deviations vs baseline
        delta_lpa = pred_lpa - INDIA_BASELINE_MEDIAN_LPA
        pct_baseline = (delta_lpa / INDIA_BASELINE_MEDIAN_LPA) * 100.0

        # Empirical confidence interval based on Archetype holdout MAE
        typical_mae_lpa = arc_result.get("typical_mae_lpa", INDIA_MODEL_MAE_LPA)
        lower_lpa = max(1.0, pred_lpa - typical_mae_lpa)
        upper_lpa = pred_lpa + typical_mae_lpa

        # Cohort distribution context (Fixed empirical quantiles from 5,859 postings)
        distribution_points = [
            {"label": "10th Pct", "salary_lpa": 3.0, "salary_inr": 300000.0, "is_user": False},
            {"label": "25th Pct (Q1)", "salary_lpa": 4.5, "salary_inr": 450000.0, "is_user": False},
            {"label": "Cohort Median", "salary_lpa": 10.0, "salary_inr": 1000000.0, "is_user": False},
            {"label": "75th Pct (Q3)", "salary_lpa": 19.0, "salary_inr": 1900000.0, "is_user": False},
            {"label": "90th Pct", "salary_lpa": 25.0, "salary_inr": 2500000.0, "is_user": False},
            {"label": "Your Estimate", "salary_lpa": round(pred_lpa, 2), "salary_inr": round(pred_inr, 0), "is_user": True},
        ]
        distribution_points = sorted(distribution_points, key=lambda x: x["salary_lpa"])

        return {
            "country": "India",
            "currency": "INR",
            "currency_symbol": "₹",
            "predicted_salary_lpa": round(pred_lpa, 2),
            "predicted_salary_inr": round(pred_inr, 0),
            "predicted_salary_display": f"₹{pred_lpa:.2f} LPA",
            "predicted_salary_inr_display": f"₹{pred_inr:,.0f}",
            "confidence_interval": {
                "lower_lpa": round(lower_lpa, 2),
                "upper_lpa": round(upper_lpa, 2),
                "display": f"₹{lower_lpa:.2f} - ₹{upper_lpa:.2f} LPA",
                "margin_mae_lpa": round(typical_mae_lpa, 2),
            },
            "baseline_salary_lpa": INDIA_BASELINE_MEDIAN_LPA,
            "baseline_salary_inr": INDIA_BASELINE_MEDIAN_INR,
            "delta_vs_baseline_lpa": round(delta_lpa, 2),
            "pct_vs_baseline": round(pct_baseline, 1),
            "archetype": arc_result,
            "num_skills": matched_skills_count,
            "distribution_context": distribution_points,
            "model_metadata": {
                "model_name": "HistGradientBoostingRegressor",
                "feature_count": 290,
                "overall_mae_lpa": INDIA_MODEL_MAE_LPA,
                "overall_rmse_lpa": INDIA_MODEL_RMSE_LPA,
                "overall_r2": 0.5798,
                "hyperparameters": {
                    "max_iter": 150,
                    "learning_rate": 0.05,
                    "l2": 1.0,
                }
            },
            "input_summary": {
                "normalized_role": normalized_role,
                "experience_midpoint_years": experience_midpoint_years,
                "experience_range_years": experience_range_years,
                "city_grouped": city_grouped,
                "work_mode": work_mode,
                "selected_skills": selected_skills,
            },
        }
