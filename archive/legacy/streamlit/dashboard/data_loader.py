"""
JobIntel Cached Data Loader Module
Loads frozen CSV tables and JSON metadata using @st.cache_data for zero-latency UI.
"""

import os
import json
import pandas as pd
import streamlit as st

TABLES_P3 = "reports/tables/phase3"
TABLES_P4 = "reports/tables/phase4_1"
TABLES_P5 = "reports/tables/phase5"
MODELS_P5 = "models/phase5"


# -------------------------------------------------------------
# PHASE 3: EXPLORATORY & SUMMARY TABLES
# -------------------------------------------------------------

@st.cache_data
def load_funnel_data() -> pd.DataFrame:
    """Loads dataset selection and attrition funnel."""
    path = os.path.join(TABLES_P3, "dataset_selection_funnel.csv")
    return pd.read_csv(path)


@st.cache_data
def load_salary_summary() -> pd.DataFrame:
    """Loads overall salary distribution moments."""
    path = os.path.join(TABLES_P3, "salary_summary.csv")
    return pd.read_csv(path)


@st.cache_data
def load_salary_by_role() -> pd.DataFrame:
    """Loads salary distribution disaggregated by 18 role families."""
    path = os.path.join(TABLES_P3, "salary_by_role_family.csv")
    return pd.read_csv(path)


@st.cache_data
def load_salary_by_seniority() -> pd.DataFrame:
    """Loads salary distribution across the 5 seniority tiers."""
    path = os.path.join(TABLES_P3, "salary_by_seniority.csv")
    return pd.read_csv(path)


@st.cache_data
def load_salary_by_location() -> pd.DataFrame:
    """Loads salary distribution across 16 metropolitan regions."""
    path = os.path.join(TABLES_P3, "location_salary_summary.csv")
    return pd.read_csv(path)


@st.cache_data
def load_skill_frequency() -> pd.DataFrame:
    """Loads 82 technical skills frequencies and corpus prevalence."""
    path = os.path.join(TABLES_P3, "skill_frequency.csv")
    return pd.read_csv(path)


@st.cache_data
def load_skill_salary_association() -> pd.DataFrame:
    """Loads observed salary statistics conditional on skill presence."""
    path = os.path.join(TABLES_P3, "skill_salary_association.csv")
    return pd.read_csv(path)


@st.cache_data
def load_skill_cooccurrence() -> pd.DataFrame:
    """Loads co-occurrence matrix for top 25 skills."""
    path = os.path.join(TABLES_P3, "skill_cooccurrence.csv")
    df = pd.read_csv(path)
    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Skill"}).set_index("Skill")
    return df


@st.cache_data
def load_skill_pairs() -> pd.DataFrame:
    """Loads pairwise skill combination salary statistics."""
    path = os.path.join(TABLES_P3, "skill_pair_analysis.csv")
    return pd.read_csv(path)


# -------------------------------------------------------------
# PHASE 4.1: ARCHETYPE DISCOVERY TABLES
# -------------------------------------------------------------

@st.cache_data
def load_archetype_dict() -> pd.DataFrame:
    """Loads canonical archetype descriptions and key skills."""
    path = os.path.join(TABLES_P4, "archetype_dictionary.csv")
    return pd.read_csv(path)


@st.cache_data
def load_cluster_sizes() -> pd.DataFrame:
    """Loads cluster size counts and percentage shares."""
    path = os.path.join(TABLES_P4, "cluster_sizes.csv")
    return pd.read_csv(path)


@st.cache_data
def load_cluster_salary() -> pd.DataFrame:
    """Loads cluster salary distribution profiles."""
    path = os.path.join(TABLES_P4, "cluster_salary_profile.csv")
    return pd.read_csv(path)


@st.cache_data
def load_cluster_skills() -> pd.DataFrame:
    """Loads skill prevalence and lift across the 7 archetypes."""
    path = os.path.join(TABLES_P4, "cluster_skill_lift.csv")
    return pd.read_csv(path)


@st.cache_data
def load_cluster_roles() -> pd.DataFrame:
    """Loads role family composition by archetype."""
    path = os.path.join(TABLES_P4, "cluster_role_family_profile.csv")
    return pd.read_csv(path)


@st.cache_data
def load_cluster_seniority() -> pd.DataFrame:
    """Loads seniority tier distribution by archetype."""
    path = os.path.join(TABLES_P4, "cluster_seniority_profile.csv")
    return pd.read_csv(path)


@st.cache_data
def load_kmeans_metrics() -> pd.DataFrame:
    """Loads k selection metrics (k=2 through k=10)."""
    path = os.path.join(TABLES_P4, "kmeans_metrics.csv")
    return pd.read_csv(path)


@st.cache_data
def load_pca_variance() -> pd.DataFrame:
    """Loads PCA explained variance for 15 retained components."""
    path = os.path.join(TABLES_P4, "pca_explained_variance.csv")
    return pd.read_csv(path)


# -------------------------------------------------------------
# PHASE 5: MODEL EVALUATION & ERROR TABLES
# -------------------------------------------------------------

@st.cache_data
def load_model_comparison() -> pd.DataFrame:
    """Loads 5-fold CV model benchmark results."""
    path = os.path.join(TABLES_P5, "phase5_model_comparison.csv")
    return pd.read_csv(path)


@st.cache_data
def load_test_results() -> pd.DataFrame:
    """Loads holdout test evaluation across candidate models."""
    path = os.path.join(TABLES_P5, "phase5_test_results.csv")
    return pd.read_csv(path)


@st.cache_data
def load_feature_importance() -> pd.DataFrame:
    """Loads XGBoost Gini / split feature importance."""
    path = os.path.join(TABLES_P5, "phase5_feature_importance.csv")
    return pd.read_csv(path)


@st.cache_data
def load_permutation_importance() -> pd.DataFrame:
    """Loads holdout test permutation feature importance."""
    path = os.path.join(TABLES_P5, "phase5_permutation_importance.csv")
    return pd.read_csv(path)


@st.cache_data
def load_archetype_errors() -> pd.DataFrame:
    """Loads archetype-level holdout test error disaggregation (RQ3)."""
    path = os.path.join(TABLES_P5, "phase5_archetype_errors.csv")
    return pd.read_csv(path)


@st.cache_data
def load_bias_variance() -> pd.DataFrame:
    """Loads train vs test generalization gap metrics."""
    path = os.path.join(TABLES_P5, "phase5_bias_variance.csv")
    return pd.read_csv(path)


@st.cache_data
def load_feature_metadata() -> dict:
    """Loads full feature metadata schema and Kruskal-Wallis stats."""
    path = os.path.join(MODELS_P5, "feature_metadata.json")
    with open(path, "r") as f:
        return json.load(f)
