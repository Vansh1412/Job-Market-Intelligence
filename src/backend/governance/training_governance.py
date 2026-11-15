from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Final, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.backend.governance.schemas import (
    GovernanceEvaluationResult,
    PermissionState,
)


class TrainingAuthorization(BaseModel):
    """Formal executive authorization required before any ML model training may commence."""
    model_config = ConfigDict(frozen=True)

    authorization_id: str = Field(min_length=6, max_length=120)
    target_model_id: str = Field(min_length=3, max_length=120)
    approved_source_ids: tuple[str, ...] = Field(min_length=1)
    approved_dataset_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    unencumbered_license_verified: bool
    commercial_ai_rights_granted: bool
    authorizing_officer: str = Field(min_length=2, max_length=100)
    authorized_at: datetime
    training_justification: str = Field(min_length=10, max_length=400)

    @field_validator("approved_dataset_sha256")
    @classmethod
    def normalize_hash(cls, v: str) -> str:
        return v.upper()

    @field_validator("authorized_at")
    @classmethod
    def authorized_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("authorized_at must be timezone-aware")
        return v


class TrainingRunMetadata(BaseModel):
    """Audit metadata emitted by an authorized training pipeline execution."""
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(min_length=8, max_length=120)
    authorization_id: str = Field(min_length=6, max_length=120)
    git_commit: str = Field(min_length=7, max_length=40)
    input_dataset_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    output_model_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    algorithm_name: str
    started_at: datetime
    completed_at: datetime
    metrics: dict[str, float] = Field(default_factory=dict)

    @field_validator("input_dataset_sha256", "output_model_sha256")
    @classmethod
    def normalize_run_hashes(cls, v: str) -> str:
        return v.upper()

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("run timestamps must be timezone-aware")
        return v


# Quarantined raw sources subject to permanent zero-retraining governance rule
QUARANTINED_RAW_SOURCES: Final[frozenset[str]] = frozenset({
    "in.jobintel.market-data",
    "indian-job-market-dataset-2025.xlsx",
})

# Sources requiring explicit commercial AI / Tier 2 upgrade before any training
COMMERCIAL_TIER_RESTRICTED_SOURCES: Final[frozenset[str]] = frozenset({
    "us.jobintel.market-data",
    "dataset_a",
})


class TrainingGovernanceGate:
    """Authoritative gatekeeper evaluating and authorizing model training runs."""

    def evaluate_training_request(
        self,
        source_id: str,
        dataset_sha256: str,
        authorization: TrainingAuthorization | None = None,
    ) -> GovernanceEvaluationResult:
        """
        Evaluate whether an attempted model training execution is legally and operationally permissible.
        """
        source_id_lower = source_id.lower()
        norm_hash = dataset_sha256.upper()
        audit_hash = hashlib.sha256(f"train:{source_id}:{norm_hash}".encode()).hexdigest()[:16]
        audit_ref = f"trn-audit-{audit_hash}"

        # 1. Enforce permanent zero-retraining quarantine on unverified India data
        if any(q in source_id_lower for q in QUARANTINED_RAW_SOURCES):
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_ZERO_RETRAINING_RULE",
                source_id=source_id,
                audit_ref=audit_ref,
                caveats=("Source is permanently quarantined under the Zero-Retraining Governance Rule.",),
            )

        # 2. Check for missing executive authorization
        if authorization is None:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_TRAINING_UNAUTHORIZED",
                source_id=source_id,
                audit_ref=audit_ref,
                caveats=("No approved TrainingAuthorization record supplied.",),
            )

        # 3. Enforce commercial AI / Tier 2 grant on DataForge
        if any(c in source_id_lower for c in COMMERCIAL_TIER_RESTRICTED_SOURCES):
            if not authorization.commercial_ai_rights_granted or not authorization.unencumbered_license_verified:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_TIER2_LICENSE_REQUIRED",
                    source_id=source_id,
                    audit_ref=audit_ref,
                    caveats=("DataForge Dataset A requires verified Tier 2 Commercial AI rights.",),
                )

        # 4. Enforce exact dataset hash binding
        if norm_hash != authorization.approved_dataset_sha256:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_CHECKSUM_MISMATCH",
                source_id=source_id,
                audit_ref=audit_ref,
                caveats=("Training dataset SHA-256 does not match approved authorization hash.",),
            )

        # 5. Authorization valid
        return GovernanceEvaluationResult(
            allowed=True,
            decision_status=PermissionState.APPROVED,
            reason_code="GOV_ALLOWED",
            source_id=source_id,
            audit_ref=audit_ref,
            caveats=("Model training authorized under formal executive sign-off.",),
        )


def verify_ci_training_compliance(attempted_sources: list[str]) -> bool:
    """
    CI validation routine asserting that automated test or build runs do not attempt
    to train or fit models using quarantined raw sources.
    """
    gate = TrainingGovernanceGate()
    for source in attempted_sources:
        result = gate.evaluate_training_request(source, "0000000000000000000000000000000000000000000000000000000000000000")
        if not result.allowed and result.reason_code == "GOV_DENIED_ZERO_RETRAINING_RULE":
            return False
    return True

