"""
JobIntel Cached Model Loader Module
Loads frozen ML pipelines and clustering models into memory using @st.cache_resource.
"""

import sys
import joblib
import streamlit as st

# Ensure repository root is on Python path so custom transformers unpickle cleanly
if "." not in sys.path:
    sys.path.insert(0, ".")

from src.phase5.preprocessing import MetadataTransformer


@st.cache_resource
def load_salary_model():
    """Loads the frozen winning XGBoost regressor."""
    model_path = "models/phase5/best_model.pkl"
    return joblib.load(model_path)


@st.cache_resource
def load_metadata_pipeline():
    """Loads the frozen MetadataTransformer for Feature Set A."""
    pipe_path = "models/phase5/best_pipeline.pkl"
    return joblib.load(pipe_path)


@st.cache_resource
def load_archetype_pipeline():
    """
    Loads frozen unsupervised components (Scaler, PCA, KMeans)
    for real-time skill-profile archetype assignment.
    """
    scaler = joblib.load("models/scaler_phase4_1.pkl")
    pca = joblib.load("models/pca_phase4_1.pkl")
    kmeans = joblib.load("models/kmeans_phase4_1_k7.pkl")
    return scaler, pca, kmeans
