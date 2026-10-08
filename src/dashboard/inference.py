"""
JobIntel Inference Engine
Handles live user input validation, feature matrix alignment,
and real-time salary prediction & archetype classification.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

from src.dashboard.model_loader import (
    load_salary_model,
    load_metadata_pipeline,
    load_archetype_pipeline,
)
from src.dashboard.data_loader import load_feature_metadata

# Archetype metadata lookup
ARCHETYPE_LOOKUP = {
    0: {
        "code": "FOUND_TECH",
        "name": "Foundational & Broad Technical Roles",
        "desc": "A heterogeneous residual cluster dominated by low-skill-count postings and foundational IT/software roles.",
        "typical_mae": 37194.0,
        "rel_error": 22.16,
    },
    1: {
        "code": "DEVOPS_PLAT",
        "name": "DevOps & Cloud Infrastructure Engineering",
        "desc": "Specialized platform, container orchestration, and CI/CD infrastructure roles.",
        "typical_mae": 37887.0,
        "rel_error": 19.38,
    },
    2: {
        "code": "WEB_FRONT",
        "name": "Frontend & Modern Web Application Engineering",
        "desc": "Client-side interfaces, responsive frameworks, and full-stack web application development.",
        "typical_mae": 33932.0,
        "rel_error": 20.20,
    },
    3: {
        "code": "CLOUD_ARCH",
        "name": "Multi-Cloud & Enterprise Cloud Architecture",
        "desc": "Enterprise cloud engineering across AWS, Azure, and distributed architectures.",
        "typical_mae": 46098.0,
        "rel_error": 20.69,
    },
    4: {
        "code": "DATA_BI",
        "name": "Data Engineering & Business Analytics",
        "desc": "Data warehousing, ETL pipelines, SQL analytics, and BI reporting systems.",
        "typical_mae": 36142.0,
        "rel_error": 21.65,
    },
    5: {
        "code": "AI_ML",
        "name": "AI / Machine Learning & LLM Engineering",
        "desc": "Deep learning, predictive modeling, NLP, and modern generative AI frameworks.",
        "typical_mae": 27002.0,
        "rel_error": 14.42,
    },
    6: {
        "code": "SYS_ENG",
        "name": "Systems & Core Backend Engineering",
        "desc": "Low-level systems programming, embedded firmware, Linux kernel, and C/C++ backend engines.",
        "typical_mae": 34850.0,
        "rel_error": 20.37,
    },
}


def predict_salary_and_archetype(
    role_family: str,
    seniority: str,
    city_clean: str,
    is_remote: bool,
    selected_skills: List[str],
) -> Dict[str, Any]:
    """
    Executes live XGBoost inference and real-time archetype classification.

    Parameters:
        role_family: 1 of 18 standardized role families
        seniority: 1 of 5 seniority tiers
        city_clean: 1 of 16 cleaned metropolitan regions
        is_remote: Boolean remote work flag
        selected_skills: List of selected technical skill names (without 'skill_' prefix)

    Returns:
        Dictionary containing predicted salary, archetype details, and feature diagnostics.
    """
    meta_info = load_feature_metadata()
    tech_skills = meta_info["tech_skills"]  # 82 columns with 'skill_' prefix
    expected_features = meta_info["feature_names"]  # exactly 123 columns

    # 1. Prepare raw inputs DataFrame
    num_skills_val = float(len(selected_skills))
    row_meta = {
        "seniority": [seniority],
        "role_family": [role_family],
        "city_clean": [city_clean],
        "is_remote": [1.0 if is_remote else 0.0],
        "num_skills": [num_skills_val],
    }
    df_meta = pd.DataFrame(row_meta)

    # 2. Prepare 82 binary skills
    selected_set = {f"skill_{s.lower().replace(' ', '_').replace('-', '_')}" for s in selected_skills}
    # Also support direct matching if already prefixed
    selected_set.update({s.lower() for s in selected_skills})

    row_skills = {}
    skills_arr = np.zeros((1, len(tech_skills)), dtype=np.float32)
    for idx, skill_col in enumerate(tech_skills):
        is_present = 1.0 if skill_col in selected_set else 0.0
        row_skills[skill_col] = [is_present]
        skills_arr[0, idx] = is_present

    df_skills = pd.DataFrame(row_skills)

    # 3. Transform metadata using frozen pipeline
    pipeline = load_metadata_pipeline()
    meta_transformed = pipeline.transform(df_meta[meta_info["metadata_cols"]])

    # 4. Horizontally stack features
    X_input = np.hstack([meta_transformed, skills_arr])

    # 5. Validate feature alignment
    if X_input.shape[1] != len(expected_features):
        raise ValueError(
            f"Feature count mismatch: Expected {len(expected_features)}, got {X_input.shape[1]}"
        )

    # 6. Execute live XGBoost prediction
    model = load_salary_model()
    pred_val = float(model.predict(X_input)[0])

    # 7. Real-time Archetype Classification
    scaler, pca, kmeans = load_archetype_pipeline()
    if num_skills_val > 0:
        scaled_skills = scaler.transform(skills_arr)
        pca_coords = pca.transform(scaled_skills)
        cluster_id = int(kmeans.predict(pca_coords)[0])
        archetype_info = ARCHETYPE_LOOKUP.get(cluster_id, ARCHETYPE_LOOKUP[0])
    else:
        cluster_id = 0
        archetype_info = {
            "code": "ZERO_SKILL",
            "name": "Zero-Skill Posting (Unassigned)",
            "desc": "No technical skills selected. Phase 4 explicitly quarantined zero-skill postings from archetype discovery.",
            "typical_mae": 37194.0,
            "rel_error": 22.16,
        }

    return {
        "predicted_salary": pred_val,
        "cluster_id": cluster_id,
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
