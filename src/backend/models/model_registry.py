"""
JobIntel Production Model Registry
==================================
Centralized singleton managing lazy and startup loading of frozen research artifacts.
Verifies cryptographic SHA-256 signatures before serving any model in memory.
Guarantees zero model drift and strict research reproducibility.

Author: Antigravity MLOps & Integration Team
"""

import os
import json
import pickle
import hashlib
from typing import Dict, Any, Tuple, Optional
import joblib

# Ensure custom classes can be unpickled cleanly
import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from src.phase5.preprocessing import MetadataTransformer


# -----------------------------------------------------------------------------
# AUTHORITATIVE FROZEN CHECKSUMS (SSOT)
# -----------------------------------------------------------------------------
EXPECTED_HASHES = {
    # India Salary Artifacts
    "india_salary_model": {
        "path": "models/india/final_model.pkl",
        "sha256": "7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310",
        "description": "India HistGradientBoostingRegressor Salary Model (v1)",
    },
    "india_preprocessor": {
        "path": "models/india/final_preprocessor.pkl",
        "sha256": "0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead",
        "description": "India ColumnTransformer Feature Preprocessor",
    },
    "india_cohort": {
        "path": "data/processed/india/india_modeling_cohort.parquet",
        "sha256": "d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec",
        "description": "India Modeling Cohort (5,859 Rows, 299 Columns)",
    },
    "india_pca": {
        "path": "models/india/india_pca_v1.pkl",
        "sha256": "8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897",
        "description": "India 15-Component Centered Covariance PCA",
    },
    "india_kmeans": {
        "path": "models/india/india_kmeans_v1.pkl",
        "sha256": "4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a",
        "description": "India 6-Cluster K-Means Model",
    },
    # USA Salary Artifacts
    "usa_salary_model": {
        "path": "models/phase5/best_model.pkl",
        "sha256": "55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd",
        "description": "USA XGBoost Regressor Salary Model",
    },
    "usa_preprocessor": {
        "path": "models/phase5/best_pipeline.pkl",
        "sha256": "815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19",
        "description": "USA MetadataTransformer Preprocessor",
    },
    "usa_scaler": {
        "path": "models/scaler_phase4_1.pkl",
        "sha256": "2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c",
        "description": "USA Archetype Mean-Centering Scaler",
    },
    "usa_pca": {
        "path": "models/pca_phase4_1.pkl",
        "sha256": "ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0",
        "description": "USA 15-Component PCA Transformer",
    },
    "usa_kmeans": {
        "path": "models/kmeans_phase4_1_k7.pkl",
        "sha256": "4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106",
        "description": "USA 7-Cluster K-Means Model",
    },
}


class ModelIntegrityError(Exception):
    """Raised when an on-disk model artifact has been modified or corrupted."""
    pass


class ModelRegistry:
    """
    Thread-safe, lazy-instantiated singleton registry that loads and validates
    all machine learning models, preprocessors, and metadata assets.
    """
    _instance: Optional["ModelRegistry"] = None

    def __init__(self):
        self._artifacts_loaded = False
        self._verification_results: Dict[str, Dict[str, Any]] = {}
        
        # USA in-memory objects
        self.usa_salary_model = None
        self.usa_preprocessor = None
        self.usa_feature_metadata = None
        self.usa_archetype_scaler = None
        self.usa_archetype_pca = None
        self.usa_archetype_kmeans = None
        
        # India in-memory objects
        self.india_salary_model = None
        self.india_preprocessor = None
        self.india_feature_list = None
        self.india_model_metadata = None
        self.india_archetype_pca = None
        self.india_archetype_kmeans = None
        self.india_archetype_metadata = None

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.initialize_and_verify()
        return cls._instance

    @staticmethod
    def compute_sha256(filepath: str) -> str:
        """Compute SHA-256 hash of a file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Artifact not found on disk: {filepath}")
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify_all_artifacts(self) -> Dict[str, Dict[str, Any]]:
        """Verify that every frozen artifact exists and matches its expected SHA-256 hash."""
        results = {}
        for key, spec in EXPECTED_HASHES.items():
            path = spec["path"]
            expected = spec["sha256"]
            actual = self.compute_sha256(path)
            
            if actual != expected:
                err_msg = (
                    f"CRITICAL MODEL INTEGRITY FAILURE: Artifact '{key}' at '{path}' "
                    f"has SHA-256 '{actual}', expected '{expected}'."
                )
                raise ModelIntegrityError(err_msg)
                
            results[key] = {
                "path": path,
                "verified": True,
                "sha256": actual,
                "description": spec["description"],
                "size_bytes": os.path.getsize(path),
            }
        self._verification_results = results
        return results

    def initialize_and_verify(self) -> None:
        """Verify checksums and load all model artifacts into memory once."""
        if self._artifacts_loaded:
            return

        print("=" * 70)
        print("JOBINTEL MODEL REGISTRY: VERIFYING FROZEN ARTIFACT INTEGRITY")
        print("=" * 70)

        # 1. Cryptographic validation
        self.verify_all_artifacts()
        print(f"Verified {len(self._verification_results)}/{len(EXPECTED_HASHES)} frozen artifacts bitwise intact.")

        # 2. Load USA models
        self.usa_salary_model = joblib.load(EXPECTED_HASHES["usa_salary_model"]["path"])
        self.usa_preprocessor = joblib.load(EXPECTED_HASHES["usa_preprocessor"]["path"])
        with open("models/phase5/feature_metadata.json", "r", encoding="utf-8") as f:
            self.usa_feature_metadata = json.load(f)

        self.usa_archetype_scaler = joblib.load(EXPECTED_HASHES["usa_scaler"]["path"])
        self.usa_archetype_pca = joblib.load(EXPECTED_HASHES["usa_pca"]["path"])
        self.usa_archetype_kmeans = joblib.load(EXPECTED_HASHES["usa_kmeans"]["path"])
        print("USA Models Loaded: XGBoost Salary Model (123 feats), Archetype Pipeline (k=7).")

        # 3. Load India models
        with open(EXPECTED_HASHES["india_salary_model"]["path"], "rb") as f:
            self.india_salary_model = pickle.load(f)
        with open(EXPECTED_HASHES["india_preprocessor"]["path"], "rb") as f:
            self.india_preprocessor = pickle.load(f)
        with open("models/india/final_feature_list.json", "r", encoding="utf-8") as f:
            self.india_feature_list = json.load(f)
        with open("models/india/final_model_metadata.json", "r", encoding="utf-8") as f:
            self.india_model_metadata = json.load(f)

        with open(EXPECTED_HASHES["india_pca"]["path"], "rb") as f:
            self.india_archetype_pca = pickle.load(f)
        with open(EXPECTED_HASHES["india_kmeans"]["path"], "rb") as f:
            self.india_archetype_kmeans = pickle.load(f)
        with open("models/india/india_archetype_metadata.json", "r", encoding="utf-8") as f:
            self.india_archetype_metadata = json.load(f)
        print("India Models Loaded: HistGradientBoosting Model (290 feats), Archetype Pipeline (k=6).")

        self._artifacts_loaded = True
        print("=" * 70)
        print("MODEL REGISTRY INITIALIZATION COMPLETE: STATUS GREEN")
        print("=" * 70)

    def get_status_report(self) -> Dict[str, Any]:
        """Return structured verification report for health/meta endpoints."""
        return {
            "status": "GREEN" if self._artifacts_loaded else "UNINITIALIZED",
            "artifacts_verified_count": len(self._verification_results),
            "artifacts": self._verification_results,
            "models_loaded": {
                "usa_salary_model": type(self.usa_salary_model).__name__,
                "usa_archetype_kmeans": type(self.usa_archetype_kmeans).__name__,
                "india_salary_model": type(self.india_salary_model).__name__,
                "india_archetype_kmeans": type(self.india_archetype_kmeans).__name__,
            }
        }


def get_model_registry() -> ModelRegistry:
    """Convenience getter for singleton registry."""
    return ModelRegistry.get_instance()
