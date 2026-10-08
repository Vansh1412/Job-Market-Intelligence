"""
Archetypes API Router — Latent Clusters, Sizes, Salary Profiles, and Skill Lift
"""

import pandas as pd
from fastapi import APIRouter
from src.backend.data_service import (
    get_archetype_dict_df,
    get_cluster_sizes_df,
    get_cluster_salary_df,
    get_cluster_skill_lift_df,
    get_cluster_roles_df,
    get_cluster_seniority_df,
)
from src.backend.inference_service import ARCHETYPE_LOOKUP

router = APIRouter(prefix="/api/archetypes", tags=["Archetypes"])


@router.get("/list")
def get_archetypes_list():
    df_sizes = get_cluster_sizes_df()
    df_sal = get_cluster_salary_df()
    df_dict = get_archetype_dict_df()

    col_size_id = "Cluster_ID" if "Cluster_ID" in df_sizes.columns else "Cluster"
    col_sal_id = "Cluster_ID" if "Cluster_ID" in df_sal.columns else "Cluster"

    archetypes = []
    for cid in range(7):
        meta = ARCHETYPE_LOOKUP.get(cid, {})
        code = meta.get("code", f"CLUSTER_{cid}")
        name = meta.get("name", "")
        desc = meta.get("desc", "")
        color = meta.get("color", "#6366F1")
        typ_mae = meta.get("typical_mae", 35000.0)
        rel_err = meta.get("rel_error", 20.0)

        # Size data
        size_row = df_sizes[df_sizes[col_size_id] == cid] if col_size_id in df_sizes.columns else pd.DataFrame()
        count = int(size_row["Postings_Count"].values[0]) if ("Postings_Count" in size_row.columns and len(size_row) > 0) else (int(size_row["Count"].values[0]) if ("Count" in size_row.columns and len(size_row) > 0) else 0)
        share_cols = [c for c in size_row.columns if "Share" in c]
        if share_cols and len(size_row) > 0:
            share_pct = round(float(size_row[share_cols[0]].values[0]), 2)
        elif "Corpus_Percentage" in size_row.columns and len(size_row) > 0:
            share_pct = round(float(size_row["Corpus_Percentage"].values[0]), 2)
        else:
            share_pct = 0.0

        # Salary data
        sal_row = df_sal[df_sal[col_sal_id] == cid] if col_sal_id in df_sal.columns else pd.DataFrame()
        med_sal = float(sal_row["Median_Salary"].values[0]) if (len(sal_row) > 0 and "Median_Salary" in sal_row.columns) else 180000.0

        archetypes.append({
            "id": cid,
            "code": code,
            "name": name,
            "description": desc,
            "color": color,
            "count": count,
            "share_pct": share_pct,
            "median_salary": med_sal,
            "typical_mae": typ_mae,
            "rel_error": rel_err,
        })

    return archetypes


@router.get("/skill-lifts/{cluster_id}")
def get_archetype_skill_lift(cluster_id: int):
    df_lift = get_cluster_skill_lift_df()
    # Filter or return top lift skills for this cluster
    records = df_lift.to_dict(orient="records")
    return {"cluster_id": cluster_id, "lifts": records}


@router.get("/role-profiles/{cluster_id}")
def get_archetype_role_profile(cluster_id: int):
    df_roles = get_cluster_roles_df()
    if "Cluster" in df_roles.columns:
        filtered = df_roles[df_roles["Cluster"] == cluster_id]
        return filtered.to_dict(orient="records")
    return df_roles.to_dict(orient="records")


@router.get("/all-skill-lifts")
def get_all_skill_lifts():
    df_lift = get_cluster_skill_lift_df()
    return df_lift.to_dict(orient="records")
