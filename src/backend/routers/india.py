"""
JobIntel India API Router
=========================
REST contracts for Indian job market live inference, archetype classification, and market analytics.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from src.backend.services.india_service import IndiaService
from src.backend.services.archetype_service import ArchetypeService
from src.backend.services.market_service import MarketService

router = APIRouter(prefix="/india", tags=["India Job Market"])


class IndiaPredictionRequest(BaseModel):
    normalized_role: str = Field(..., max_length=120, description="Role category, e.g., 'Data Engineer'")
    experience_midpoint_years: float = Field(..., ge=0, le=35, description="Years of experience midpoint, e.g., 5.0")
    experience_range_years: float = Field(2.0, ge=0, le=15, description="Experience span, e.g., 2.0")
    city_grouped: str = Field(..., max_length=120, description="Grouped city metro name, e.g., 'Bengaluru'")
    work_mode: str = Field("Hybrid", max_length=60, description="Work mode: 'Hybrid', 'Onsite', or 'Remote'")
    selected_skills: List[str] = Field(
        default_factory=list,
        max_length=60,
        description="List of selected technical skill tokens, e.g., ['skill_spark', 'skill_scala']"
    )


class IndiaArchetypeRequest(BaseModel):
    selected_skills: List[str] = Field(
        default_factory=list,
        max_length=60,
        description="List of technical skills to classify into India archetype"
    )


@router.get("/options")
def get_india_options():
    """Retrieve categorical options, cities, experience tiers, and 284 technical skills for India."""
    try:
        return IndiaService.get_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
def predict_india_salary(req: IndiaPredictionRequest):
    """Execute live India salary prediction using frozen HistGradientBoostingRegressor model."""
    try:
        result = IndiaService.predict(
            normalized_role=req.normalized_role,
            experience_midpoint_years=req.experience_midpoint_years,
            experience_range_years=req.experience_range_years,
            city_grouped=req.city_grouped,
            work_mode=req.work_mode,
            selected_skills=req.selected_skills,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/archetype")
def classify_india_archetype(req: IndiaArchetypeRequest):
    """Classify a list of skills into the 6 India archetypes via frozen PCA and K-Means."""
    try:
        _, skills_arr, matched_count = IndiaService.build_feature_dataframe(
            normalized_role="Software Engineer",
            experience_midpoint_years=4.0,
            experience_range_years=2.0,
            city_grouped="Bengaluru",
            work_mode="Hybrid",
            selected_skills=req.selected_skills,
        )
        return ArchetypeService.classify_india_skills(skills_arr, matched_count)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/market-summary")
def get_india_market_summary(
    role: Optional[str] = None,
    experience: Optional[str] = None,
    location: Optional[str] = None,
    skill: Optional[str] = None,
):
    """Retrieve India tech market statistics and distributions with optional cross-filtering."""
    try:
        return MarketService.get_india_market_summary(
            role=role,
            experience=experience,
            location=location,
            skill=skill,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/archetypes")
def get_india_archetypes():
    """List all 6 empirical India archetypes with salary profiles, key skills, and holdout error metrics."""
    try:
        return ArchetypeService.get_india_archetypes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills")
def get_india_skills():
    """Retrieve India technical skills with frequency, prevalence, observed salary differences, and co-occurrences."""
    try:
        return IndiaService.get_skills_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills/{skill_name}")
def get_india_skill_detail(skill_name: str):
    """Retrieve detailed empirical profile for a specific India skill."""
    try:
        detail = IndiaService.get_skill_detail(skill_name)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

