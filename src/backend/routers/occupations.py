from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.backend.schemas.occupation import (
    CanonicalOccupation,
    ClassificationSystem,
    ConcordanceCoverageStats,
    CrossMarketComparisonResult,
    NationalOccupation,
    OccupationMapping,
    OccupationPage,
    TaskSimilarityPayload,
)
from src.backend.services.occupation_service import (
    CanonicalOccupationNotFoundError,
    ClassificationNotFoundError,
    OccupationNotFoundError,
    OccupationService,
    get_occupation_service,
)

logger = logging.getLogger("jobintel.occupations_api")

router = APIRouter(prefix="/v1/occupations", tags=["Global Occupation Intelligence"])


@router.get("/classifications", response_model=list[ClassificationSystem])
def list_classifications(
    market: Annotated[str | None, Query(description="Filter by 2-letter market code (IN, US, UK, AU, SG, INT)")] = None,
    service: OccupationService = Depends(get_occupation_service),
) -> list[ClassificationSystem]:
    """Lists official occupational classification systems supported by JOBINTEL."""
    return service.get_classifications(market_id=market)


@router.get("/classifications/{classification_id}", response_model=ClassificationSystem)
def retrieve_classification(
    classification_id: Annotated[str, Path(description="Classification identifier (e.g. UK_SOC_2020)")],
    service: OccupationService = Depends(get_occupation_service),
) -> ClassificationSystem:
    """Retrieves authoritative metadata for an official classification system."""
    try:
        return service.get_classification(classification_id)
    except ClassificationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/classifications/{classification_id}/occupations", response_model=OccupationPage)
def list_occupations_by_classification(
    classification_id: Annotated[str, Path(description="Classification identifier")],
    q: Annotated[str | None, Query(description="Optional search filter by title, code, or alias")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    service: OccupationService = Depends(get_occupation_service),
) -> OccupationPage:
    """Lists and paginates national occupations within a specified classification system."""
    try:
        service.get_classification(classification_id)
    except ClassificationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    items, total = service.get_occupations(
        classification_id=classification_id, query=q, page=page, page_size=page_size
    )
    has_next = (page * page_size) < total
    return OccupationPage(
        items=tuple(items),
        page=page,
        page_size=page_size,
        total_count=total,
        has_next=has_next,
    )


@router.get("/search", response_model=list[NationalOccupation])
def search_occupations(
    q: Annotated[str, Query(min_length=1, description="Search query string (code, title, or alias)")],
    market: Annotated[str | None, Query(description="Optional filter by market code")] = None,
    classification_id: Annotated[str | None, Query(description="Optional filter by classification ID")] = None,
    limit: Annotated[int, Query(ge=1, le=50, description="Maximum results to return")] = 20,
    service: OccupationService = Depends(get_occupation_service),
) -> list[NationalOccupation]:
    """Searches occupations across national systems with deterministic relevance scoring."""
    return service.search_occupations(
        query=q, market_id=market, classification_id=classification_id, limit=limit
    )


@router.get("/canonical", response_model=list[CanonicalOccupation])
def list_canonical_occupations(
    service: OccupationService = Depends(get_occupation_service),
) -> list[CanonicalOccupation]:
    """Lists harmonized canonical occupation concepts used for international interoperability."""
    return service.get_canonical_occupations()


@router.get("/canonical/{canonical_id}", response_model=CanonicalOccupation)
def retrieve_canonical_occupation(
    canonical_id: Annotated[str, Path(description="Canonical occupation ID (e.g. CAN_OCC_SOFTWARE_ENGINEER)")],
    service: OccupationService = Depends(get_occupation_service),
) -> CanonicalOccupation:
    """Retrieves definition and competencies for a canonical occupation concept."""
    try:
        return service.get_canonical_occupation(canonical_id)
    except CanonicalOccupationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/compare", response_model=CrossMarketComparisonResult)
def compare_across_markets(
    source_occupation_id: Annotated[str, Query(description="Source occupation ID (e.g. UK_SOC_2020:2134)")],
    target_market: Annotated[str | None, Query(description="Optional target market filter (e.g. US, AU, SG)")] = None,
    service: OccupationService = Depends(get_occupation_service),
) -> CrossMarketComparisonResult:
    """Compares a source occupation to supported equivalents across national jurisdictions with calibrated confidence and provenance."""
    try:
        return service.compare_across_markets(
            source_occupation_id=source_occupation_id, target_market=target_market
        )
    except OccupationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/coverage", response_model=ConcordanceCoverageStats)
def get_concordance_coverage(
    service: OccupationService = Depends(get_occupation_service),
) -> ConcordanceCoverageStats:
    """Retrieves authoritative concordance coverage, unmapped counts, and quality metrics."""
    return service.get_coverage_stats()


@router.get("/similarity", response_model=TaskSimilarityPayload)
def compute_task_similarity(
    source_id: Annotated[str, Query(description="Source occupation ID (e.g. UK_SOC_2020:2134)")],
    target_id: Annotated[str, Query(description="Target occupation ID (e.g. US_SOC_2018:15-1252)")],
    service: OccupationService = Depends(get_occupation_service),
) -> TaskSimilarityPayload:
    """Calculates unsupervised lexical task similarity (Jaccard and TF-IDF Cosine) between two occupations."""
    try:
        return service.compute_task_similarity(source_id=source_id, target_id=target_id)
    except OccupationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{occupation_id:path}/mappings", response_model=list[OccupationMapping])
def list_occupation_mappings(
    occupation_id: Annotated[str, Path(description="Source occupation identifier (e.g. UK_SOC_2020:2134)")],
    target_market: Annotated[str | None, Query(description="Optional target market filter")] = None,
    service: OccupationService = Depends(get_occupation_service),
) -> list[OccupationMapping]:
    """Retrieves all evidence-backed concordance mappings originating from an occupation."""
    try:
        service.get_occupation(occupation_id)
    except OccupationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return service.get_mappings(occupation_id=occupation_id, target_market=target_market)


@router.get("/{occupation_id:path}", response_model=NationalOccupation)
def retrieve_occupation(
    occupation_id: Annotated[str, Path(description="Fully-qualified occupation ID (e.g. UK_SOC_2020:2134)")],
    service: OccupationService = Depends(get_occupation_service),
) -> NationalOccupation:
    """Retrieves full official definition, duties, and metadata for a national occupation."""
    try:
        return service.get_occupation(occupation_id)
    except OccupationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
