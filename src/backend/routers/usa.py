"""
JobIntel USA API Router
=======================
REST contracts for USA live inference, archetype classification, and market analytics.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from src.backend.services.usa_service import USAService
from src.backend.services.archetype_service import ArchetypeService
from src.backend.services.market_service import MarketService

router = APIRouter(prefix="/api/usa", tags=["USA Job Market"])


class USAPredictionRequest(BaseModel):
    role_family: str = Field(..., max_length=120, description="Role family name, e.g., 'ML / AI Engineer'")
    seniority: str = Field(..., max_length=60, description="Seniority level, e.g., 'Senior' or 'Mid-level'")
    city_clean: str = Field(..., max_length=120, description="Clean metro name, e.g., 'San Francisco'")
    is_remote: bool = Field(True, description="Whether position allows remote work")
    selected_skills: List[str] = Field(
        default_factory=list,
        max_length=60,
        description="List of selected technical skill tokens, e.g., ['skill_python', 'skill_pytorch']"
    )


class USAArchetypeRequest(BaseModel):
    selected_skills: List[str] = Field(
        default_factory=list,
        max_length=60,
        description="List of selected skills to classify into USA archetype"
    )


@router.get("/options")
def get_usa_options():
    """Retrieve categorical options, cities, seniority tiers, and 82 technical skills for USA."""
    try:
        return USAService.get_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
def predict_usa_salary(req: USAPredictionRequest):
    """Execute live USA salary prediction using frozen XGBoost model."""
    try:
        result = USAService.predict(
            role_family=req.role_family,
            seniority=req.seniority,
            city_clean=req.city_clean,
            is_remote=req.is_remote,
            selected_skills=req.selected_skills,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/archetype")
def classify_usa_archetype(req: USAArchetypeRequest):
    """Classify a list of skills into the 7 USA archetypes via frozen PCA and K-Means."""
    try:
        # Build 82-dim skills array
        _, skills_arr = USAService.build_feature_vector(
            role_family="Software Engineer",
            seniority="Senior",
            city_clean="San Francisco",
            is_remote=True,
            selected_skills=req.selected_skills,
        )
        return ArchetypeService.classify_usa_skills(skills_arr, len(req.selected_skills))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/market-summary")
def get_usa_market_summary(
    role: Optional[str] = None,
    seniority: Optional[str] = None,
    location: Optional[str] = None,
    skill: Optional[str] = None,
):
    """Retrieve USA tech market statistics and distributions with optional cross-filtering."""
    try:
        return MarketService.get_usa_market_summary(
            role=role,
            seniority=seniority,
            location=location,
            skill=skill,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/archetypes")
def get_usa_archetypes():
    """List all 7 empirical USA archetypes with salary profiles and key skills."""
    try:
        return ArchetypeService.get_usa_archetypes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills")
def get_usa_skills():
    """Retrieve USA technical skills with frequency, lifts, and salary associations."""
    try:
        from src.backend.data_service import get_skill_frequency_df, get_skill_salary_association_df
        df_freq = get_skill_frequency_df()
        df_assoc = get_skill_salary_association_df()

        skills_list = []
        for _, r in df_freq.iterrows():
            s_name = str(r.get("Skill", ""))
            skills_list.append({
                "skill": s_name,
                "postings": int(r.get("Postings", 0)),
                "prevalence_pct": float(r.get("Prevalence_Pct", 0)),
            })
        return {
            "country": "USA",
            "skills": skills_list,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
