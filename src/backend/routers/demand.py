"""Demand Intelligence API Endpoints for JOBINTEL 2.0.

Provides REST interfaces for multi-market occupational demand observations,
time-series trends, regional distributions, cross-market comparability,
and skill gap analysis with strict provenance disclosures and licensing gates.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.backend.schemas.demand import (
    DemandComparisonResult,
    DemandMetricDefinition,
    DemandObservation,
    DemandTimeSeriesPoint,
    OccupationDemandProfile,
    RegionalDemandPoint,
    SkillDemandItem,
    SkillGapAnalysisRequest,
    SkillGapAnalysisResult,
)
from src.backend.schemas.market import MarketId
from src.backend.services.demand_service import DemandService, get_demand_service

logger = logging.getLogger("jobintel.demand_api")

router = APIRouter(prefix="/v1/demand", tags=["Global Job Demand Intelligence"])


@router.get("/markets")
def list_demand_markets(
    service: DemandService = Depends(get_demand_service),
) -> list[dict[str, Any]]:
    """Lists supported markets, licensing statuses, and demand intelligence coverage."""
    return service.get_markets_overview()


@router.get("/metrics", response_model=list[DemandMetricDefinition])
def list_demand_metrics(
    service: DemandService = Depends(get_demand_service),
) -> list[DemandMetricDefinition]:
    """Lists definitions, underlying constructs, and caveats for all demand metric types."""
    return service.get_metrics()


@router.get("/metrics/{metric_type}", response_model=DemandMetricDefinition)
def get_demand_metric(
    metric_type: Annotated[str, Path(description="Demand metric type identifier")],
    service: DemandService = Depends(get_demand_service),
) -> DemandMetricDefinition:
    """Retrieves definition and limitations for a specific demand metric type."""
    metric = service.get_metric(metric_type)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric type '{metric_type}' not found.")
    return metric


@router.get("/sources")
def list_demand_sources(
    service: DemandService = Depends(get_demand_service),
) -> list[dict[str, Any]]:
    """Lists official data sources, licensing terms, rights notices, and publication statuses."""
    return service.get_sources()


@router.get("/occupations", response_model=list[DemandObservation])
def list_demand_observations(
    market: Annotated[str | None, Query(description="Filter by 2-letter market code (US, AU, UK, SG, IN)")] = None,
    canonical_id: Annotated[str | None, Query(description="Filter by canonical occupation ID")] = None,
    metric_type: Annotated[str | None, Query(description="Filter by demand metric type")] = None,
    service: DemandService = Depends(get_demand_service),
) -> list[DemandObservation]:
    """Lists atomic demand observations with sanitized values enforcing licensing gates."""
    return service.list_observations(
        market_id=market,
        canonical_id=canonical_id,
        metric_type=metric_type,
        public_view=True,
    )


@router.get("/occupations/{occupation_id}", response_model=OccupationDemandProfile)
def get_occupation_demand(
    occupation_id: Annotated[str, Path(description="National occupation code or canonical ID")],
    market: Annotated[str, Query(description="Market identifier (US, AU, UK, SG, IN)")] = "US",
    service: DemandService = Depends(get_demand_service),
) -> OccupationDemandProfile:
    """Retrieves comprehensive demand intelligence profile for an occupation with full provenance metadata."""
    profile = service.get_occupation_demand_profile(
        market_id=market,
        occupation_id=occupation_id,
        public_view=True,
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Demand profile not found for occupation '{occupation_id}' in market '{market}'.",
        )
    return profile


@router.get("/occupations/{occupation_id}/trends")
def get_occupation_demand_trends(
    occupation_id: Annotated[str, Path(description="National occupation code or canonical ID")],
    market: Annotated[str, Query(description="Market identifier (US, AU, UK, SG, IN)")] = "US",
    service: DemandService = Depends(get_demand_service),
) -> dict[str, Any]:
    """Retrieves historical and projected time-series trend points with publication gate enforcement."""
    profile = service.get_occupation_demand_profile(
        market_id=market,
        occupation_id=occupation_id,
        public_view=True,
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Demand trends not found for occupation '{occupation_id}' in market '{market}'.",
        )
    return {
        "occupation_id": profile.occupation_id,
        "occupation_title": profile.occupation_title,
        "market_id": profile.market_id,
        "trend_direction": profile.trend_direction,
        "percentage_change": profile.trend_percentage_change,
        "time_series": profile.trend_time_series,
        "publication_gate_active": profile.publication_gate_active,
        "publication_gate_code": profile.publication_gate_code,
        "publication_gate_message": profile.publication_gate_message,
    }


@router.get("/occupations/{occupation_id}/regions", response_model=list[RegionalDemandPoint])
def get_occupation_regional_demand(
    occupation_id: Annotated[str, Path(description="National occupation code or canonical ID")],
    market: Annotated[str, Query(description="Market identifier (US, AU, UK, SG, IN)")] = "US",
    service: DemandService = Depends(get_demand_service),
) -> list[RegionalDemandPoint]:
    """Retrieves sub-national state, province, or regional demand breakdown with derivation disclosures."""
    profile = service.get_occupation_demand_profile(
        market_id=market,
        occupation_id=occupation_id,
        public_view=True,
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Regional demand not found for occupation '{occupation_id}' in market '{market}'.",
        )
    return profile.regional_distribution


@router.get("/occupations/{occupation_id}/skills", response_model=list[SkillDemandItem])
def get_occupation_demand_skills(
    occupation_id: Annotated[str, Path(description="National occupation code or canonical ID")],
    market: Annotated[str, Query(description="Market identifier (US, AU, UK, SG, IN)")] = "US",
    service: DemandService = Depends(get_demand_service),
) -> list[SkillDemandItem]:
    """Retrieves high-demand skills, tools, and competencies associated with the occupation."""
    profile = service.get_occupation_demand_profile(
        market_id=market,
        occupation_id=occupation_id,
        public_view=True,
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Skills demand not found for occupation '{occupation_id}' in market '{market}'.",
        )
    return profile.top_skills


@router.get("/compare", response_model=DemandComparisonResult)
def compare_demand(
    canonical_id: Annotated[str, Query(description="Canonical occupation concept ID (e.g. CAN_OCC_SOFTWARE_ENGINEER)")],
    market_a: Annotated[str, Query(description="First market code (US, AU, UK, SG, IN)")],
    market_b: Annotated[str, Query(description="Second market code (US, AU, UK, SG, IN)")],
    service: DemandService = Depends(get_demand_service),
) -> DemandComparisonResult:
    """Executes the 11-dimension comparability engine to evaluate demand data alignment between two markets."""
    return service.compare_demand(
        canonical_id=canonical_id,
        market_a=market_a,
        market_b=market_b,
    )


@router.post("/skills/gaps", response_model=SkillGapAnalysisResult)
def analyze_skill_gaps(
    request: SkillGapAnalysisRequest,
    service: DemandService = Depends(get_demand_service),
) -> SkillGapAnalysisResult:
    """Analyzes user-provided skills against market demand requirements with mathematical formula transparency."""
    return service.analyze_skill_gaps(request)
