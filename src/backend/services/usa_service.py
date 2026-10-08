"""
JobIntel USA Inference Service
================================
Production service for USA salary prediction and feature transformation.
Consumes frozen XGBoost model and preprocessor via ModelRegistry.
Guarantees bitwise equivalence with research evaluation pipeline.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from src.backend.models.model_registry import get_model_registry

# Certified USA Tech Modeling Cohort Baseline Moments
USA_BASELINE_MEDIAN = 180413.0
USA_BASELINE_MEAN = 187834.0
USA_MODEL_MAE = 36380.64
USA_MODEL_RMSE = 51082.06

USA_SENIORITY_TIERS = [
    "Intern",
    "Junior / Entry",
    "Mid / Unspecified",
    "Senior",
    "Lead / Principal / Executive",
]

USA_ROLE_FAMILIES = [
    "Backend Developer",
    "Data / BI Analyst",
    "Data Engineer",
    "Data Scientist",
    "DevOps / Cloud / Platform",
    "Embedded & Hardware",
    "Engineering Management",
    "Frontend Developer",
    "Full-Stack Developer",
    "ML / AI Engineer",
    "Mobile Engineer",
    "Other Tech",
    "QA / SDET",
    "Security Engineer",
    "Software Engineer",
    "Solutions & Architecture",
    "Systems & Network Engineer",
    "Technical Product & PM",
]

USA_CITIES = [
    "Boston",
    "Chicago",
    "Costa Mesa",
    "Denver",
    "Hawthorne",
    "Long Beach",
    "Los Angeles",
    "Mountain View",
    "New York",
    "New York City",
    "Other",
    "San Francisco",
    "San Jose",
    "Seattle",
    "Toronto",
    "Washington",
]

# Mapping display labels to preprocessor category values if needed
SENIORITY_DISPLAY_MAP = {
    "Entry-level": "Junior / Entry",
    "Junior / Entry": "Junior / Entry",
    "Mid-level": "Mid / Unspecified",
    "Mid / Unspecified": "Mid / Unspecified",
    "Senior": "Senior",
    "Lead / Principal": "Lead / Principal / Executive",
    "Lead / Principal / Executive": "Lead / Principal / Executive",
    "Executive / Director": "Lead / Principal / Executive",
    "Intern": "Intern",
}


def normalize_seniority(seniority_input: str) -> str:
    """Normalize user seniority display name to preprocessor category."""
    if seniority_input in SENIORITY_DISPLAY_MAP:
        return SENIORITY_DISPLAY_MAP[seniority_input]
    for key, val in SENIORITY_DISPLAY_MAP.items():
        if key.lower() == seniority_input.lower():
            return val
    return "Mid / Unspecified"


class USAService:
    """
    Stateless service wrapping USA salary inference and input options.
    """

    @staticmethod
    def get_options() -> Dict[str, Any]:
        """Return available categorical choices and technical skills for USA."""
        registry = get_model_registry()
        tech_skills = registry.usa_feature_metadata.get("tech_skills", [])
        
        # Format skills for frontend presentation
        formatted_skills = []
        for s in tech_skills:
            clean_name = s.replace("skill_", "").replace("_", " ").title()
            # Preserve special acronyms
            for acr in ["Aws", "Gcp", "Sql", "Ci Cd", "Ai", "Ml", "Nlp", "Api", "Ui", "Ux", "Dbt", "Etl"]:
                clean_name = clean_name.replace(acr, acr.upper())
            formatted_skills.append({
                "id": s,
                "name": clean_name,
                "raw_key": s,
            })

        formatted_skills = sorted(formatted_skills, key=lambda x: x["name"])

        return {
            "country": "USA",
            "currency": "USD",
            "currency_symbol": "$",
            "scale": "Annual Base ($)",
            "roles": USA_ROLE_FAMILIES,
            "seniority_tiers": [
                "Entry-level",
                "Mid-level",
                "Senior",
                "Lead / Principal",
                "Executive / Director",
            ],
            "cities": USA_CITIES,
            "skills": formatted_skills,
            "default_profile": {
                "role_family": "ML / AI Engineer",
                "seniority": "Senior",
                "city_clean": "San Francisco",
                "is_remote": True,
                "selected_skills": ["skill_python", "skill_pytorch", "skill_machine_learning"],
            },
            "baseline": {
                "median_salary": USA_BASELINE_MEDIAN,
                "mean_salary": USA_BASELINE_MEAN,
                "mae": USA_MODEL_MAE,
            }
        }

    @staticmethod
    def build_feature_vector(
        role_family: str,
        seniority: str,
        city_clean: str,
        is_remote: bool,
        selected_skills: List[str],
    ) -> np.ndarray:
        """
        Build the exact 123-feature vector for USA XGBoost model.
        """
        registry = get_model_registry()
        meta_info = registry.usa_feature_metadata
        tech_skills = meta_info["tech_skills"]
        expected_features = meta_info["feature_names"]

        norm_seniority = normalize_seniority(seniority)
        norm_city = city_clean if city_clean in USA_CITIES else "Other"
        norm_role = role_family if role_family in USA_ROLE_FAMILIES else "Other Tech"

        num_skills_val = float(len(selected_skills))

        # Metadata DataFrame (order expected by MetadataTransformer: seniority, role_family, is_remote, city_clean, num_skills)
        df_meta = pd.DataFrame({
            "seniority": [norm_seniority],
            "role_family": [norm_role],
            "city_clean": [norm_city],
            "is_remote": [1.0 if is_remote else 0.0],
            "num_skills": [num_skills_val],
        })

        # Preprocess metadata through frozen pipeline
        pipeline = registry.usa_preprocessor
        meta_transformed = pipeline.transform(df_meta[meta_info["metadata_cols"]])

        # Construct 82-dim skills binary row
        skills_set = set()
        for s in selected_skills:
            s_clean = s.lower().strip()
            if not s_clean.startswith("skill_"):
                skills_set.add(f"skill_{s_clean.replace(' ', '_').replace('-', '_')}")
            skills_set.add(s_clean)

        skills_arr = np.zeros((1, len(tech_skills)), dtype=np.float32)
        for idx, skill_col in enumerate(tech_skills):
            if skill_col in skills_set or skill_col.replace("skill_", "") in skills_set:
                skills_arr[0, idx] = 1.0

        # Combine into complete 123-feature input
        X_input = np.hstack([meta_transformed, skills_arr])

        if X_input.shape[1] != len(expected_features):
            raise ValueError(
                f"USA Feature shape mismatch: expected {len(expected_features)} columns, got {X_input.shape[1]}"
            )

        return X_input, skills_arr

    @classmethod
    def predict(
        cls,
        role_family: str,
        seniority: str,
        city_clean: str,
        is_remote: bool,
        selected_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Execute live prediction for USA job profile.
        """
        registry = get_model_registry()
        X_input, skills_arr = cls.build_feature_vector(
            role_family=role_family,
            seniority=seniority,
            city_clean=city_clean,
            is_remote=is_remote,
            selected_skills=selected_skills,
        )

        # Run frozen XGBoost model
        pred_val = float(registry.usa_salary_model.predict(X_input)[0])
        pred_val = max(30000.0, pred_val)  # Floor at sensible lower bound

        # Archetype classification via service
        from src.backend.services.archetype_service import ArchetypeService
        arc_result = ArchetypeService.classify_usa_skills(skills_arr, len(selected_skills))

        # Deviation from cohort median
        delta_baseline = pred_val - USA_BASELINE_MEDIAN
        pct_baseline = (delta_baseline / USA_BASELINE_MEDIAN) * 100.0

        # Typical error for bounds
        typical_mae = arc_result.get("typical_mae", USA_MODEL_MAE)
        low_bound = max(30000.0, pred_val - typical_mae)
        high_bound = pred_val + typical_mae

        # Cohort distribution context (Fixed empirical quantiles from 34,036 tech postings)
        distribution_points = [
            {"label": "10th Pct", "salary": 95000.0, "is_user": False},
            {"label": "25th Pct (Q1)", "salary": 140000.0, "is_user": False},
            {"label": "Cohort Median", "salary": 180413.0, "is_user": False},
            {"label": "75th Pct (Q3)", "salary": 225000.0, "is_user": False},
            {"label": "90th Pct", "salary": 275000.0, "is_user": False},
            {"label": "Your Estimate", "salary": round(pred_val, 2), "is_user": True},
        ]
        distribution_points = sorted(distribution_points, key=lambda x: x["salary"])

        return {
            "country": "USA",
            "currency": "USD",
            "currency_symbol": "$",
            "predicted_salary": round(pred_val, 2),
            "predicted_salary_display": f"${pred_val:,.0f}",
            "confidence_interval": {
                "lower": round(low_bound, 2),
                "upper": round(high_bound, 2),
                "display": f"${low_bound:,.0f} - ${high_bound:,.0f}",
                "margin_mae": round(typical_mae, 2),
            },
            "baseline_salary": USA_BASELINE_MEDIAN,
            "delta_vs_baseline": round(delta_baseline, 2),
            "pct_vs_baseline": round(pct_baseline, 1),
            "archetype": arc_result,
            "num_skills": len(selected_skills),
            "distribution_context": distribution_points,
            "model_metadata": {
                "model_name": "XGBoost Regressor (Tuned)",
                "feature_count": 123,
                "overall_mae": USA_MODEL_MAE,
                "overall_rmse": USA_MODEL_RMSE,
            },
            "input_summary": {
                "role_family": role_family,
                "seniority": seniority,
                "city_clean": city_clean,
                "is_remote": is_remote,
                "selected_skills": selected_skills,
            },
        }
