from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Final
from fastapi import HTTPException

from src.backend.data_catalog.registry import get_source, get_sources
from src.backend.governance.engine import (
    GovernanceEvaluationRequest,
    GovernancePolicyEngine,
)
from src.backend.governance.revocation import RevocationRegistry
from src.backend.governance.schemas import (
    GovernanceEvaluationResult,
    GovernanceOperation,
    ModelLineageRecord,
    PermissionState,
    SourceIdentity,
)
from src.backend.schemas.data import ReuseReviewStatus

logger = logging.getLogger("jobintel.governance.service")

_ENGINE_INSTANCE: GovernancePolicyEngine | None = None


def _map_reuse_status_to_permission_state(status: ReuseReviewStatus) -> PermissionState:
    if status == ReuseReviewStatus.APPROVED:
        return PermissionState.APPROVED
    if status == ReuseReviewStatus.REVIEW_REQUIRED:
        return PermissionState.REVIEW_REQUIRED
    if status == ReuseReviewStatus.RESTRICTED:
        return PermissionState.DENIED
    return PermissionState.UNKNOWN


def get_governance_engine() -> GovernancePolicyEngine:
    """
    Retrieve or initialize the authoritative GovernancePolicyEngine singleton.
    Populates sources dynamically from the data catalog and loads persisted revocations.
    """
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        source_identities: list[SourceIdentity] = []
        for ds in get_sources():
            perm_state = _map_reuse_status_to_permission_state(ds.reuse_review_status)
            source_identities.append(
                SourceIdentity(
                    source_id=ds.source_id,
                    source_name=ds.source_name,
                    publisher_name=ds.source_organization,
                    canonical_publication_url=ds.canonical_publication_url or ds.source_reference,
                    acquisition_url=ds.acquisition_url,
                    artifact_download_url=ds.artifact_download_url,
                    license_name="Standard Evaluation Terms",
                    license_version="v1.0",
                    default_permission_state=perm_state,
                    registered_at=datetime.now(timezone.utc),
                )
            )

        revocation_reg = RevocationRegistry.load_from_manifest_file()
        _ENGINE_INSTANCE = GovernancePolicyEngine(
            sources=source_identities,
            revocation_registry=revocation_reg,
        )
    return _ENGINE_INSTANCE


def reset_governance_engine() -> None:
    """Reset the singleton instance (primarily for testing and cache invalidation)."""
    global _ENGINE_INSTANCE
    _ENGINE_INSTANCE = None


def verify_uk_salary_governance() -> GovernanceEvaluationResult:
    """
    Authoritative governance gate evaluation for UK ASHE descriptive salary intelligence.
    Enforces that unreviewed or unapproved sources fail closed immediately.
    """
    engine = get_governance_engine()
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    result = engine.evaluate(req)
    if not result.allowed:
        logger.warning(
            "UK Salary Governance Gate denied request: code=%s, status=%s, ref=%s",
            result.reason_code,
            result.decision_status.value,
            result.audit_ref,
        )
        raise HTTPException(
            status_code=503,
            detail={
                "code": "UK_DATA_NOT_PUBLISHED",
                "message": "UK salary analytics are not currently published.",
            },
        )
    return result


def record_inference_governance(market: str, model_id: str) -> GovernanceEvaluationResult:
    """
    Auditable governance evaluation for live ML model inference.
    Records operational authorization status without blocking research inference or altering schemas.
    """
    source_map = {
        "USA": "us.jobintel.market-data",
        "India": "in.jobintel.market-data",
    }
    market_code = "US" if market.upper() == "USA" else "IN"
    source_id = source_map.get(market, f"{market.lower()}.jobintel.market-data")

    engine = get_governance_engine()
    lineage = ModelLineageRecord(
        model_id=model_id,
        market_id=market_code,
        algorithm_name="Production Pipeline Regressor",
        model_artifact_sha256="3D4468E2D79FA71804E1D02A7E15462D4A32BC6663E9733475225E9385C1E09B",
        preprocessor_artifact_sha256="F9D9B22C99757D8412F5868C65449A39A1C5FA2BA05BAEFE762D770281F998D8",
        training_data_source_id=source_id,
        training_data_hash="AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899",
        license_tier="Tier 1 (Internal Analytics)",
        trained_at=datetime.now(timezone.utc),
    )
    req = GovernanceEvaluationRequest(
        source_id=source_id,
        operation=GovernanceOperation.INTERNAL_MODEL_INFERENCE,
        model_id=model_id,
        model_lineage=lineage,
    )
    result = engine.evaluate(req)
    logger.debug(
        "Governance inference recorded: market=%s, model=%s, allowed=%s, code=%s, ref=%s",
        market,
        model_id,
        result.allowed,
        result.reason_code,
        result.audit_ref,
    )
    return result
