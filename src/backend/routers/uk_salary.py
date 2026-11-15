from __future__ import annotations

import json
import logging
from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.backend.data_catalog.registry import get_source
from src.backend.schemas.data import ReuseReviewStatus, ValidationStatus
from src.backend.schemas.uk_salary import (
    UKOccupationDetail,
    UKOccupationPage,
    UKAPIErrorEnvelope,
    UKRegionComparison,
    UKRegionOccupationPage,
    UKSalaryMetadata,
    UKValueStatus,
)
from src.backend.services.uk_salary_service import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MANIFEST_PATH,
    PUBLICATION_APPROVED_MODE,
    SOURCE_ID,
    SOURCE_REFERENCE,
    UKSalaryNotFound,
    UKSalaryServiceError,
    approved_dataset_checksum_matches,
    get_uk_salary_service,
    has_valid_publication_approval,
)

logger = logging.getLogger("jobintel.uk_salary_api")
router = APIRouter(prefix="/v1/markets/UK/salary", tags=["UK Descriptive Salary Intelligence"])
SERVICE_UNAVAILABLE_RESPONSE = {503: {"model": UKAPIErrorEnvelope}}


def require_uk_publication() -> None:
    """Fail closed unless both the catalog and manifest explicitly allow publication."""
    try:
        source = get_source(SOURCE_ID)
    except Exception as exc:
        logger.error("UK publication check failed; code=uk_source_unregistered")
        raise HTTPException(
            status_code=503,
            detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
        ) from exc

    # Governance Policy Layer: Assert authoritative fail-closed evaluation
    from src.backend.governance.service import get_governance_engine
    engine = get_governance_engine()
    if not engine.revocation_registry.is_healthy:
        logger.warning("UK publication check failed: revocation registry degraded (%s)", engine.revocation_registry.status)
        raise _not_published()

    revocation = engine.revocation_registry.check_revocation(source_id=SOURCE_ID)
    if revocation:
        logger.warning("UK Salary publication blocked by revocation: scope=%s reason=%s", revocation.scope, revocation.reason_code)
        raise _not_published()

    if source.reuse_review_status != ReuseReviewStatus.APPROVED:
        from src.backend.governance.service import verify_uk_salary_governance
        verify_uk_salary_governance()

    try:
        live_source_id = source.source_id
        live_catalog_reference = str(source.source_reference) if source.source_reference is not None else None
        live_reuse_status = source.reuse_review_status
        live_validation_status = source.validation_status
        live_geography = tuple(source.geographic_coverage)
        live_reference_period = source.reference_period
    except Exception:
        logger.error("UK publication check failed; code=uk_catalog_metadata_invalid")
        raise HTTPException(
            status_code=503,
            detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
        ) from None

    try:
        with DEFAULT_MANIFEST_PATH.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
    except (OSError, json.JSONDecodeError, UnicodeError, TypeError):
        if source.reuse_review_status != ReuseReviewStatus.APPROVED:
            raise _not_published()
        logger.error("UK publication check failed; code=uk_manifest_unavailable")
        raise HTTPException(
            status_code=503,
            detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
        )

    if not isinstance(manifest, dict):
        logger.error("UK publication check failed; code=uk_manifest_invalid")
        raise HTTPException(
            status_code=503,
            detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
        )

    provenance = manifest.get("data_provenance")
    if not isinstance(provenance, dict):
        raise _not_published()
    manifest_geography = manifest.get("geographic_coverage")
    if not isinstance(manifest_geography, list) or any(not isinstance(region, str) for region in manifest_geography):
        raise _not_published()

    permitted = (
        live_source_id == SOURCE_ID
        and live_reuse_status == ReuseReviewStatus.APPROVED
        and live_validation_status == ValidationStatus.VALIDATED
        and live_catalog_reference == SOURCE_REFERENCE
        and live_geography == tuple(manifest_geography)
        and live_reference_period == provenance.get("reference_period")
        and manifest.get("source_id") == SOURCE_ID
        and manifest.get("processing_mode") == PUBLICATION_APPROVED_MODE
        and manifest.get("source_reference") == SOURCE_REFERENCE
        and manifest.get("catalog_source_reference") == live_catalog_reference
        and manifest.get("source_reference_matches_catalog") is True
        and has_valid_publication_approval(manifest)
    )
    if not permitted:
        raise _not_published()
    if not approved_dataset_checksum_matches(manifest, DEFAULT_DATASET_PATH):
        logger.error("UK publication check failed; code=uk_approved_dataset_checksum_invalid")
        raise HTTPException(
            status_code=503,
            detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
        )


def _not_published() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "code": "UK_DATA_NOT_PUBLISHED",
            "message": "UK salary analytics are not currently published.",
        },
    )


def _unavailable(exc: UKSalaryServiceError) -> NoReturn:
    logger.error("UK salary service unavailable; code=%s", exc.code)
    raise HTTPException(
        status_code=503,
        detail={"code": "UK_DATA_UNAVAILABLE", "message": "UK salary data is currently unavailable."},
    ) from exc


def _not_found(exc: UKSalaryNotFound) -> NoReturn:
    label = "Occupation" if exc.code == "occupation_not_found" else "Region"
    raise HTTPException(status_code=404, detail=f"{label} not found") from exc


def _get_service():
    try:
        return get_uk_salary_service()
    except UKSalaryServiceError as exc:
        _unavailable(exc)


@router.get("/occupations", response_model=UKOccupationPage, responses=SERVICE_UNAVAILABLE_RESPONSE)
def list_occupations(
    _: None = Depends(require_uk_publication),
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    page: Annotated[int, Query(ge=1, le=10000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> UKOccupationPage:
    if q is not None and not q.strip():
        raise HTTPException(status_code=422, detail="Search query must contain a visible character")
    return _get_service().list_occupations(q, page, page_size)


@router.get("/occupations/{soc_code}", response_model=UKOccupationDetail, responses=SERVICE_UNAVAILABLE_RESPONSE)
def get_occupation(
    soc_code: Annotated[str, Path(pattern=r"^[0-9]{4}$")],
    _: None = Depends(require_uk_publication),
) -> UKOccupationDetail:
    try:
        return _get_service().get_occupation(soc_code)
    except UKSalaryNotFound as exc:
        _not_found(exc)


@router.get("/occupations/{soc_code}/regions", response_model=UKRegionComparison, responses=SERVICE_UNAVAILABLE_RESPONSE)
def compare_occupation_regions(
    soc_code: Annotated[str, Path(pattern=r"^[0-9]{4}$")],
    _: None = Depends(require_uk_publication),
) -> UKRegionComparison:
    try:
        return _get_service().compare_regions(soc_code)
    except UKSalaryNotFound as exc:
        _not_found(exc)


@router.get("/regions/{region}/occupations", response_model=UKRegionOccupationPage, responses=SERVICE_UNAVAILABLE_RESPONSE)
def list_region_occupations(
    region: Annotated[str, Path(pattern=r"^[A-Za-z][A-Za-z ]{1,79}$")],
    _: None = Depends(require_uk_publication),
    value_status: UKValueStatus = UKValueStatus.REPORTED,
    page: Annotated[int, Query(ge=1, le=10000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> UKRegionOccupationPage:
    try:
        return _get_service().list_region_occupations(region, value_status, page, page_size)
    except UKSalaryNotFound as exc:
        _not_found(exc)


@router.get("/metadata", response_model=UKSalaryMetadata, responses=SERVICE_UNAVAILABLE_RESPONSE)
def get_uk_salary_metadata(
    _: None = Depends(require_uk_publication),
) -> UKSalaryMetadata:
    return _get_service().metadata()
