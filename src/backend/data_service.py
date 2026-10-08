"""
JobIntel Backend Data Service — Zero Streamlit Dependencies
Loads frozen research artifacts and tables using functools.lru_cache.
"""

import os
import json
from functools import lru_cache
import pandas as pd
import joblib

import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from src.phase5.preprocessing import MetadataTransformer

TABLES_P3 = "reports/tables/phase3"
TABLES_P4 = "reports/tables/phase4_1"
TABLES_P5 = "reports/tables/phase5"
MODELS_P5 = "models/phase5"


# ── Metadata & Artifacts ────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_feature_metadata() -> dict:
    path = os.path.join(MODELS_P5, "feature_metadata.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_salary_model():
    return joblib.load(os.path.join(MODELS_P5, "best_model.pkl"))


@lru_cache(maxsize=1)
def get_metadata_pipeline():
    return joblib.load(os.path.join(MODELS_P5, "best_pipeline.pkl"))


@lru_cache(maxsize=1)
def get_archetype_pipeline():
    scaler = joblib.load("models/scaler_phase4_1.pkl")
    pca = joblib.load("models/pca_phase4_1.pkl")
    kmeans = joblib.load("models/kmeans_phase4_1_k7.pkl")
    return scaler, pca, kmeans


# ── Phase 3: Exploratory & Funnel Tables ───────────────────────────────────────
@lru_cache(maxsize=1)
def get_funnel_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "dataset_selection_funnel.csv"))


@lru_cache(maxsize=1)
def get_salary_summary_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "salary_summary.csv"))


@lru_cache(maxsize=1)
def get_salary_by_role_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "salary_by_role_family.csv"))


@lru_cache(maxsize=1)
def get_salary_by_seniority_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "salary_by_seniority.csv"))


@lru_cache(maxsize=1)
def get_salary_by_location_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "location_salary_summary.csv"))


@lru_cache(maxsize=1)
def get_skill_frequency_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "skill_frequency.csv"))


@lru_cache(maxsize=1)
def get_skill_salary_association_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P3, "skill_salary_association.csv"))


@lru_cache(maxsize=1)
def get_skill_cooccurrence_df() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(TABLES_P3, "skill_cooccurrence.csv"))
    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Skill"})
    return df


# ── Phase 4.1: Archetype Discovery Tables ─────────────────────────────────────
@lru_cache(maxsize=1)
def get_archetype_dict_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "archetype_dictionary.csv"))


@lru_cache(maxsize=1)
def get_cluster_sizes_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "cluster_sizes.csv"))


@lru_cache(maxsize=1)
def get_cluster_salary_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "cluster_salary_profile.csv"))


@lru_cache(maxsize=1)
def get_cluster_skill_lift_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "cluster_skill_lift.csv"))


@lru_cache(maxsize=1)
def get_cluster_roles_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "cluster_role_family_profile.csv"))


@lru_cache(maxsize=1)
def get_cluster_seniority_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "cluster_seniority_profile.csv"))


@lru_cache(maxsize=1)
def get_kmeans_metrics_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "kmeans_metrics.csv"))


@lru_cache(maxsize=1)
def get_pca_variance_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P4, "pca_explained_variance.csv"))


# ── Phase 5: Supervised Evaluation & Error Analysis Tables ─────────────────────
@lru_cache(maxsize=1)
def get_model_comparison_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_model_comparison.csv"))


@lru_cache(maxsize=1)
def get_test_results_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_test_results.csv"))


@lru_cache(maxsize=1)
def get_feature_importance_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_feature_importance.csv"))


@lru_cache(maxsize=1)
def get_permutation_importance_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_permutation_importance.csv"))


@lru_cache(maxsize=1)
def get_archetype_errors_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_archetype_errors.csv"))


@lru_cache(maxsize=1)
def get_bias_variance_df() -> pd.DataFrame:
    return pd.read_csv(os.path.join(TABLES_P5, "phase5_bias_variance.csv"))
