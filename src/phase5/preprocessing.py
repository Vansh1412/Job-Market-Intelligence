"""
Phase 5: Preprocessing and Transformers
=======================================
INT234 Predictive Analytics — Job Market Intelligence
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator, TransformerMixin

RANDOM_STATE = 42
N_COMPONENTS_PCA = 15
N_CLUSTERS_KMEANS = 7


class MetadataTransformer(BaseEstimator, TransformerMixin):
    """
    Transforms tabular metadata predictors:
    - One-hot encodes 'seniority', 'role_family', 'city_clean'
    - Converts 'is_remote' to binary integer
    - Keeps 'num_skills' as numeric
    """
    def __init__(self):
        self.cat_cols = ["seniority", "role_family", "city_clean"]
        self.ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.is_fitted = False
        self.feature_names_out_ = []

    def fit(self, X, y=None):
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        self.ohe.fit(X_df[self.cat_cols])
        self.is_fitted = True

        ohe_features = self.ohe.get_feature_names_out(self.cat_cols).tolist()
        self.feature_names_out_ = ohe_features + ["is_remote", "num_skills"]
        return self

    def transform(self, X):
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        ohe_vals = self.ohe.transform(X_df[self.cat_cols])
        is_remote_vals = X_df["is_remote"].astype(float).values.reshape(-1, 1)
        num_skills_vals = X_df["num_skills"].astype(float).values.reshape(-1, 1)

        return np.hstack([ohe_vals, is_remote_vals, num_skills_vals])

    def get_feature_names_out(self):
        return self.feature_names_out_


class FoldSafeSkillPCA(BaseEstimator, TransformerMixin):
    """
    PCA transformation on the 82 technical skills fitted STRICTLY on training fold.
    Uses Phase-4.2 certified Centered Covariance PCA (with_mean=True, with_std=False).
    """
    def __init__(self, n_components=N_COMPONENTS_PCA, random_state=RANDOM_STATE):
        self.n_components = n_components
        self.random_state = random_state
        self.scaler = StandardScaler(with_mean=True, with_std=False)
        self.pca = PCA(n_components=n_components, random_state=random_state)
        self.is_fitted = False

    def fit(self, X_skills, y=None):
        X_skills_arr = np.asarray(X_skills, dtype=np.float32)
        X_centered = self.scaler.fit_transform(X_skills_arr)
        self.pca.fit(X_centered)
        self.is_fitted = True
        return self

    def transform(self, X_skills):
        X_skills_arr = np.asarray(X_skills, dtype=np.float32)
        X_centered = self.scaler.transform(X_skills_arr)
        return self.pca.transform(X_centered)

    def get_feature_names_out(self):
        return [f"PC{i+1}" for i in range(self.n_components)]


class FoldSafeArchetypeTransformer(BaseEstimator, TransformerMixin):
    """
    Fold-safe K-Means archetype clusterer fitted STRICTLY on training PCA coordinates.
    Generates one-hot encoded cluster indicators (7 categories).
    Out-of-sample points are assigned using nearest training centroids.
    """
    def __init__(self, n_clusters=N_CLUSTERS_KMEANS, random_state=RANDOM_STATE):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.is_fitted = False

    def fit(self, X_pca, y=None):
        self.kmeans.fit(X_pca)
        self.is_fitted = True
        return self

    def transform(self, X_pca):
        cluster_labels = self.kmeans.predict(X_pca)
        # One-hot encode into 7 indicator columns
        ohe = np.zeros((len(cluster_labels), self.n_clusters), dtype=np.float32)
        for i, c in enumerate(cluster_labels):
            ohe[i, c] = 1.0
        return ohe

    def predict_cluster_labels(self, X_pca):
        return self.kmeans.predict(X_pca)

    def get_feature_names_out(self):
        archetype_names = [
            "arch_0_FOUND_TECH",
            "arch_1_DEVOPS_PLAT",
            "arch_2_WEB_FRONT",
            "arch_3_CLOUD_ARCH",
            "arch_4_DATA_BI",
            "arch_5_AI_ML",
            "arch_6_SYS_ENG",
        ]
        return archetype_names[:self.n_clusters]
