"""
JobIntel Backend Inference Service — Zero Streamlit Dependencies
Executes live XGBoost inference and archetype classification against frozen artifacts.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from src.backend.data_service import (
    get_salary_model,
    get_metadata_pipeline,
    get_archetype_pipeline,
    get_feature_metadata,
)

ARCHETYPE_LOOKUP = {
    0: {
        "code": "FOUND_TECH",
        "name": "Foundational & Broad Technical Roles",
        "desc": "A heterogeneous residual cluster dominated by low-skill-count postings and foundational IT/software roles.",
        "color": "#F97316",
        "typical_mae": 37194.0,
        "rel_error": 22.16,
    },
    1: {
        "code": "DEVOPS_PLAT",
        "name": "DevOps & Cloud Infrastructure Engineering",
        "desc": "Specialized platform, container orchestration, and CI/CD infrastructure roles.",
        "color": "#06B6D4",
        "typical_mae": 37887.0,
        "rel_error": 19.38,
    },
    2: {
        "code": "WEB_FRONT",
        "name": "Frontend & Modern Web Application Engineering",
        "desc": "Client-side interfaces, responsive frameworks, and full-stack web application development.",
        "color": "#EC4899",
        "typical_mae": 33932.0,
        "rel_error": 20.20,
    },
    3: {
        "code": "CLOUD_ARCH",
        "name": "Multi-Cloud & Enterprise Cloud Architecture",
        "desc": "Enterprise cloud engineering across AWS, Azure, and distributed architectures.",
        "color": "#14B8A6",
        "typical_mae": 46098.0,
        "rel_error": 20.69,
    },
    4: {
        "code": "DATA_BI",
        "name": "Data Engineering & Business Analytics",
        "desc": "Data warehousing, ETL pipelines, SQL analytics, and BI reporting systems.",
        "color": "#F59E0B",
        "typical_mae": 36142.0,
        "rel_error": 21.65,
    },
    5: {
        "code": "AI_ML",
        "name": "AI / Machine Learning & LLM Engineering",
        "desc": "Deep learning, predictive modeling, NLP, and modern generative AI frameworks.",
        "color": "#8B5CF6",
        "typical_mae": 27002.0,
        "rel_error": 14.42,
    },
    6: {
        "code": "SYS_ENG",
        "name": "Systems & Core Backend Engineering",
        "desc": "Low-level systems programming, embedded firmware, Linux kernel, and C/C++ backend engines.",
        "color": "#10B981",
        "typical_mae": 34850.0,
        "rel_error": 20.37,
    },
}

COHORT_BASELINE = 180413.0


def predict_job_profile(
    role_family: str,
    seniority: str,
    city_clean: str,
    is_remote: bool,
    selected_skills: List[str],
) -> Dict[str, Any]:
    """
    Executes live XGBoost inference and real-time archetype classification.
    """
    meta_info = get_feature_metadata()
    tech_skills = meta_info["tech_skills"]
    expected_features = meta_info["feature_names"]

    num_skills_val = float(len(selected_skills))
    row_meta = {
        "seniority": [seniority],
        "role_family": [role_family],
        "city_clean": [city_clean],
        "is_remote": [1.0 if is_remote else 0.0],
        "num_skills": [num_skills_val],
    }
    df_meta = pd.DataFrame(row_meta)

    # Prepare skill indicators
    selected_set = {f"skill_{s.lower().replace(' ', '_').replace('-', '_')}" for s in selected_skills}
    selected_set.update({s.lower() for s in selected_skills})

    skills_arr = np.zeros((1, len(tech_skills)), dtype=np.float32)
    for idx, skill_col in enumerate(tech_skills):
        skills_arr[0, idx] = 1.0 if skill_col in selected_set else 0.0

    # Pipeline transform
    pipeline = get_metadata_pipeline()
    meta_transformed = pipeline.transform(df_meta[meta_info["metadata_cols"]])

    # Horizontal stack
    X_input = np.hstack([meta_transformed, skills_arr])
    if X_input.shape[1] != len(expected_features):
        raise ValueError(f"Feature count mismatch: Expected {len(expected_features)}, got {X_input.shape[1]}")

    # XGBoost prediction
    model = get_salary_model()
    pred_val = float(model.predict(X_input)[0])

    # Archetype classification
    scaler, pca, kmeans = get_archetype_pipeline()
    if num_skills_val > 0:
        scaled_skills = scaler.transform(skills_arr)
        pca_coords = pca.transform(scaled_skills)
        cluster_id = int(kmeans.predict(pca_coords)[0])
        archetype_info = ARCHETYPE_LOOKUP.get(cluster_id, ARCHETYPE_LOOKUP[0])
        archetype_available = True
    else:
        cluster_id = -1
        archetype_available = False
        archetype_info = {
            "code": "ZERO_SKILL",
            "name": "Archetype Unavailable (Zero Skills)",
            "desc": "The learned archetype taxonomy is defined for skill-bearing job postings. Add at least one technical skill to receive an archetype classification.",
            "color": "#64748B",
            "typical_mae": 37194.0,
            "rel_error": 22.16,
        }

    delta_baseline = pred_val - COHORT_BASELINE
    pct_baseline = (delta_baseline / COHORT_BASELINE) * 100.0

    return {
        "predicted_salary": round(pred_val, 2),
        "predicted_salary_display": f"${pred_val:,.0f}",
        "baseline_salary": COHORT_BASELINE,
        "delta_vs_baseline": round(delta_baseline, 2),
        "pct_vs_baseline": round(pct_baseline, 1),
        "cluster_id": cluster_id,
        "archetype_available": archetype_available,
        "archetype": archetype_info,
        "num_skills": len(selected_skills),
        "input_summary": {
            "role_family": role_family,
            "seniority": seniority,
            "city_clean": city_clean,
            "is_remote": is_remote,
            "selected_skills": selected_skills,
        },
    }
