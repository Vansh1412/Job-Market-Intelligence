"""
Model Performance & Observability API Router — Candidate Benchmarks & Feature Sets
"""

from fastapi import APIRouter
from src.backend.data_service import (
    get_model_comparison_df,
    get_test_results_df,
    get_feature_importance_df,
    get_permutation_importance_df,
)

router = APIRouter(prefix="/api/models", tags=["Model Performance"])


@router.get("/benchmarks")
def get_benchmarks():
    df_comp = get_model_comparison_df()
    df_test = get_test_results_df()
    return {
        "cv_comparison": df_comp.to_dict(orient="records"),
        "test_results": df_test.to_dict(orient="records"),
        "best_model": {
            "name": "XGBoost Regressor (Optuna Tuned)",
            "test_mae": 36381.0,
            "test_rmse": 51082.0,
            "test_r2": 0.4233,
            "baseline_mae": 50800.0,
            "improvement_pct": 28.4,
            "unexplained_variance_pct": 57.67,
        },
    }


@router.get("/feature-sets")
def get_feature_sets():
    return [
        {
            "id": "Set A",
            "name": "Feature Set A (Explicit)",
            "features_count": 123,
            "mae": 36381.0,
            "r2": 0.4233,
            "composition": "Metadata (Seniority, Role Family, City, Remote) + 82 explicit binary technical skills.",
            "color": "#8B5CF6",
            "is_best": True,
            "delta_vs_a": "Baseline",
        },
        {
            "id": "Set B",
            "name": "Feature Set B (PCA Compressed)",
            "features_count": 56,
            "mae": 37842.0,
            "r2": 0.3814,
            "composition": "Metadata + 15 continuous Principal Components. Compression discards 43.95% variance.",
            "color": "#06B6D4",
            "is_best": False,
            "delta_vs_a": "+$1,461 MAE (+4.0%)",
        },
        {
            "id": "Set C",
            "name": "Feature Set C (Archetype Augmented)",
            "features_count": 130,
            "mae": 36425.0,
            "r2": 0.4255,
            "composition": "Feature Set A + 7 one-hot archetype cluster indicators. Negligible delta (+0.12%).",
            "color": "#10B981",
            "is_best": False,
            "delta_vs_a": "+$44.20 MAE (+0.12%)",
        },
    ]


@router.get("/feature-importance")
def get_feature_importance():
    df_feat = get_feature_importance_df()
    if "Importance" in df_feat.columns:
        df_feat = df_feat.sort_values(by="Importance", ascending=False).head(20)
    return df_feat.to_dict(orient="records")
