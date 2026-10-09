"""
Archetype Error Analysis (RQ3) API Router — Statistical Tests & Error Disaggregation
"""

from fastapi import APIRouter
from src.backend.data_service import get_archetype_errors_df
from src.backend.inference_service import ARCHETYPE_LOOKUP

router = APIRouter(prefix="/error-analysis", tags=["Error Analysis"])


@router.get("/archetype-breakdown")
def get_archetype_error_breakdown():
    df_err = get_archetype_errors_df().copy()
    if "MAE" in df_err.columns:
        df_err = df_err.sort_values(by="MAE", ascending=True)

    records = []
    for _, row in df_err.iterrows():
        cid = int(row.get("Archetype_ID", row.get("Cluster", 0)))
        meta = ARCHETYPE_LOOKUP.get(cid, {})
        records.append({
            "cluster_id": cid,
            "code": meta.get("code", f"C{cid}"),
            "name": meta.get("name", str(row.get("Archetype_Name", ""))),
            "color": meta.get("color", "#6366F1"),
            "mae": float(row.get("MAE", 35000.0)),
            "rmse": float(row.get("RMSE", 50000.0)),
            "r2": float(row.get("R2", 0.4)),
            "rel_error_pct": float(row.get("Relative_MAE_%", row.get("Rel_Error_Pct", 20.0))),
            "count": int(row.get("N", row.get("Count", 1000))),
        })
    return records


@router.get("/statistical-test")
def get_statistical_test():
    return {
        "test_name": "Kruskal-Wallis One-Way Nonparametric ANOVA",
        "statistic_h": 88.10,
        "degrees_of_freedom": 6,
        "p_value": 7.53e-17,
        "p_value_formatted": "7.53 × 10⁻¹⁷",
        "is_significant": True,
        "alpha": 0.001,
        "verdict": "Null hypothesis rejected: Absolute prediction error distributions differ significantly across the 7 archetypes.",
        "inferential_boundary": "Confirms statistical difference in error distributions across cohorts; does not imply causal wage effects or individual certainty bounds.",
    }


@router.get("/hypotheses")
def get_hypotheses():
    return [
        {
            "id": 1,
            "archetype": "AI_ML",
            "title": "Dense & Discriminating Stacks",
            "stat": "$27,002 MAE (Lowest)",
            "color": "#10B981",
            "summary": "AI_ML postings feature tightly coupled, highly specific competencies (machine_learning, python, pytorch, deep_learning). This density provides the supervised tree ensemble with strong, unambiguous predictive splits.",
        },
        {
            "id": 2,
            "archetype": "CLOUD_ARCH",
            "title": "Elevated Baseline & Scope Dispersion",
            "stat": "$46,098 MAE (Highest)",
            "color": "#F59E0B",
            "summary": "CLOUD_ARCH postings command the highest baseline scale ($220,000 median) with wide enterprise compensation dispersion (std: $66.5k). Absolute prediction residuals naturally scale with underlying midpoint magnitude.",
        },
        {
            "id": 3,
            "archetype": "FOUND_TECH",
            "title": "Residual Role Heterogeneity & Skill Sparsity",
            "stat": "22.16% Relative Error (Highest)",
            "color": "#F97316",
            "summary": "FOUND_TECH suffers the highest relative error because 85.31% of postings possess ≤2 skills. The sparse feature vectors provide minimal tree splitting information, forcing reliance on coarse structural priors.",
        },
    ]
