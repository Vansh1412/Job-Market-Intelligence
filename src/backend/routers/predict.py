"""
Predictor API Router — Real-Time Inference, Archetype Mapping, and Input Options
"""

from typing import List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from src.backend.data_service import (
    get_feature_metadata,
    get_salary_by_role_df,
    get_salary_by_seniority_df,
    get_salary_by_location_df,
    get_skill_frequency_df,
)
from src.backend.inference_service import predict_job_profile

router = APIRouter(prefix="/predict", tags=["Prediction"])


class PredictionRequest(BaseModel):
    role_family: str = Field(..., json_schema_extra={"example": "ML / AI Engineer"})
    seniority: str = Field(..., json_schema_extra={"example": "Senior"})
    city_clean: str = Field(..., json_schema_extra={"example": "San Francisco"})
    is_remote: bool = Field(True, json_schema_extra={"example": True})
    selected_skills: List[str] = Field(default_factory=list, json_schema_extra={"example": ["python", "pytorch", "machine_learning"]})


@router.get("/options")
def get_prediction_options():
    df_roles = get_salary_by_role_df()
    df_sen = get_salary_by_seniority_df()
    df_loc = get_salary_by_location_df()
    df_skills = get_skill_frequency_df()

    roles = df_roles["Role_Family"].tolist() if "Role_Family" in df_roles.columns else []
    tier_order = ["Entry-level", "Mid-level", "Senior", "Lead / Principal", "Executive / Director"]
    cities = df_loc["City"].tolist() if "City" in df_loc.columns else []
    
    # Categorized skill list
    from src.backend.routers.skills import categorize_skill, CATEGORY_COLORS
    skill_items = []
    for _, r in df_skills.iterrows():
        s_name = str(r.get("Skill", ""))
        cat = categorize_skill(s_name)
        skill_items.append({
            "name": s_name,
            "category": cat,
            "color": CATEGORY_COLORS.get(cat, "#64748B"),
            "postings": int(r.get("Postings", 0)),
        })

    # Sort skills alphabetically
    skill_items = sorted(skill_items, key=lambda x: x["name"])

    return {
        "roles": roles,
        "seniority_tiers": tier_order,
        "cities": cities,
        "skills": skill_items,
        "default_profile": {
            "role_family": "ML / AI Engineer",
            "seniority": "Senior",
            "city_clean": "San Francisco",
            "is_remote": True,
            "selected_skills": ["python", "pytorch", "machine_learning"],
        },
    }


@router.post("/estimate")
def estimate_salary(req: PredictionRequest):
    try:
        result = predict_job_profile(
            role_family=req.role_family,
            seniority=req.seniority,
            city_clean=req.city_clean,
            is_remote=req.is_remote,
            selected_skills=req.selected_skills,
        )

        # Build simulated distribution reference points based on frozen corpus moments
        # Median: $180,413, Q1: $140,000, Q3: $225,000, P10: $95,000, P90: $275,000
        pred_val = result["predicted_salary"]
        distribution_points = [
            {"label": "10th Pct", "salary": 95000},
            {"label": "25th Pct (Q1)", "salary": 140000},
            {"label": "Median", "salary": 180413},
            {"label": "75th Pct (Q3)", "salary": 225000},
            {"label": "90th Pct", "salary": 275000},
            {"label": "Your Estimate", "salary": pred_val, "is_user": True},
        ]
        distribution_points = sorted(distribution_points, key=lambda x: x["salary"])
        result["distribution_context"] = distribution_points

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
