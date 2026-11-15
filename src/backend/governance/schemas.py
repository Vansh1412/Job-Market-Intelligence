from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PermissionState(StrEnum):
    """Explicit, auditable states for data access and operation permissions."""
    UNKNOWN = "UNKNOWN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class GovernanceOperation(StrEnum):
    """The eight orthogonal, purpose-specific governance operations."""
    INTERNAL_ANALYTICS = "INTERNAL_ANALYTICS"
    PUBLIC_AGGREGATE_DISPLAY = "PUBLIC_AGGREGATE_DISPLAY"
    COMMERCIAL_AGGREGATE_DISPLAY = "COMMERCIAL_AGGREGATE_DISPLAY"
    REDISTRIBUTION_RAW = "REDISTRIBUTION_RAW"
    ML_TRAINING = "ML_TRAINING"
    INTERNAL_MODEL_INFERENCE = "INTERNAL_MODEL_INFERENCE"
    PUBLIC_MODEL_INFERENCE = "PUBLIC_MODEL_INFERENCE"
    COMMERCIAL_MODEL_INFERENCE = "COMMERCIAL_MODEL_INFERENCE"


class CommercialStatus(StrEnum):
    """Commercial exploitation status under governing terms."""
    NON_COMMERCIAL_ONLY = "NON_COMMERCIAL_ONLY"
    COMMERCIAL_ALLOWED = "COMMERCIAL_ALLOWED"
    COMMERCIAL_RESTRICTED = "COMMERCIAL_RESTRICTED"
    INTERNAL_ONLY = "INTERNAL_ONLY"


class TargetAudience(StrEnum):
    """Authorized consumer audience."""
    INTERNAL_RESEARCH = "INTERNAL_RESEARCH"
    PUBLIC_UNAUTHENTICATED = "PUBLIC_UNAUTHENTICATED"
    AUTHENTICATED_USERS = "AUTHENTICATED_USERS"
    PAID_COMMERCIAL = "PAID_COMMERCIAL"


class RevocationScope(StrEnum):
    """Hierarchical scope at which a revocation applies."""
    SOURCE = "SOURCE"
    DATASET = "DATASET"
    RELEASE = "RELEASE"
    APPROVAL = "APPROVAL"
    MODEL = "MODEL"


class LifecycleState(StrEnum):
    """Canonical 10-state lifecycle governing datasets and releases."""
    SOURCE_REGISTERED = "SOURCE_REGISTERED"
    REUSE_REVIEW_REQUIRED = "REUSE_REVIEW_REQUIRED"
    REUSE_APPROVED = "REUSE_APPROVED"
    DATA_ACQUIRED = "DATA_ACQUIRED"
    DATA_VALIDATED = "DATA_VALIDATED"
    USE_APPROVED = "USE_APPROVED"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SHA256_HEX_PATTERN = re.compile(r"^[A-Fa-f0-9]{64}$")
_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,95}$")


def _validate_tz_aware(dt: datetime | None, field_name: str) -> datetime | None:
    if dt is not None and dt.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware UTC datetime")
    return dt


# ---------------------------------------------------------------------------
# 1. Source Identity
# ---------------------------------------------------------------------------

class SourceIdentity(BaseModel):
    """Immutable declaration of a data source and its legal governance envelope."""
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    source_name: str = Field(min_length=2, max_length=160)
    publisher_name: str = Field(min_length=2, max_length=160)
    canonical_publication_url: AnyHttpUrl | None = None
    acquisition_url: AnyHttpUrl | None = None
    artifact_download_url: AnyHttpUrl | None = None
    license_name: str = Field(min_length=2, max_length=120)
    license_version: str = Field(min_length=1, max_length=40)
    license_url: AnyHttpUrl | None = None
    default_permission_state: PermissionState = PermissionState.REVIEW_REQUIRED
    registered_at: datetime

    @field_validator("registered_at")
    @classmethod
    def registered_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("registered_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 2. Artifact Integrity
# ---------------------------------------------------------------------------

class ArtifactIntegrity(BaseModel):
    """Cryptographic integrity fingerprint of a physical file."""
    model_config = ConfigDict(frozen=True)

    artifact_id: str = Field(min_length=3, max_length=120)
    file_name: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(gt=0)
    sha256_hex: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    verified_at: datetime

    @field_validator("sha256_hex")
    @classmethod
    def normalize_sha256(cls, v: str) -> str:
        return v.upper()

    @field_validator("verified_at")
    @classmethod
    def verified_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("verified_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 3. Dataset Release
# ---------------------------------------------------------------------------

class DatasetRelease(BaseModel):
    """Formal, version-bound release of a processed dataset."""
    model_config = ConfigDict(frozen=True)

    release_id: str = Field(min_length=4, max_length=120)
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    dataset_version: str = Field(min_length=1, max_length=40)
    primary_artifact: ArtifactIntegrity
    reference_period: str = Field(min_length=4, max_length=60)
    geographic_coverage: tuple[str, ...] = Field(min_length=1)
    record_count: int = Field(ge=0)
    lifecycle_state: LifecycleState = LifecycleState.DATA_VALIDATED
    dataset_id: str | None = Field(default=None, max_length=120)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def created_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 4. Provenance Record
# ---------------------------------------------------------------------------

class ProvenanceRecord(BaseModel):
    """End-to-end lineage binding an output artifact to its origin and execution."""
    model_config = ConfigDict(frozen=True)

    provenance_id: str = Field(min_length=4, max_length=120)
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    dataset_release_id: str = Field(min_length=4, max_length=120)
    pipeline_module: str = Field(min_length=2, max_length=160)
    pipeline_version: str = Field(min_length=1, max_length=60)
    upstream_archive_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    output_artifact_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    canonical_source_url: AnyHttpUrl | None = None
    ingested_at: datetime
    quality_summary: dict[str, int] = Field(default_factory=dict)

    @field_validator("upstream_archive_sha256", "output_artifact_sha256")
    @classmethod
    def normalize_hashes(cls, v: str) -> str:
        return v.upper()

    @field_validator("ingested_at")
    @classmethod
    def ingested_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("ingested_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 5. Permission Decision
# ---------------------------------------------------------------------------

class PermissionDecision(BaseModel):
    """Granular permission decision for a specific operation and scope."""
    model_config = ConfigDict(frozen=True)

    operation: GovernanceOperation
    state: PermissionState
    reason_code: str = Field(min_length=3, max_length=80)
    mandatory_caveats: tuple[str, ...] = ()
    evaluated_at: datetime

    @field_validator("evaluated_at")
    @classmethod
    def evaluated_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("evaluated_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 6. Approval Record
# ---------------------------------------------------------------------------

class ApprovalRecord(BaseModel):
    """Version-bound dual-custody approval authorizing a specific dataset operation."""
    model_config = ConfigDict(frozen=True)

    approval_id: str = Field(min_length=4, max_length=120)
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    dataset_release_id: str = Field(min_length=4, max_length=120)
    dataset_version: str = Field(min_length=1, max_length=40)
    artifact_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    license_version: str = Field(min_length=1, max_length=40)
    intended_operation: GovernanceOperation
    geography: tuple[str, ...] = Field(min_length=1)
    reference_period: str = Field(min_length=4, max_length=60)
    audience: TargetAudience
    commercial_status: CommercialStatus
    approval_evidence: str = Field(min_length=3, max_length=255)
    approved_by: str = Field(min_length=2, max_length=100)
    approved_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True

    @field_validator("artifact_sha256")
    @classmethod
    def normalize_artifact_sha256(cls, v: str) -> str:
        return v.upper()

    @field_validator("approved_at", "expires_at")
    @classmethod
    def approval_timestamps_tz_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.utcoffset() is None:
            raise ValueError("approval timestamps must be timezone-aware")
        return v

    @model_validator(mode="after")
    def expiry_after_approval(self) -> "ApprovalRecord":
        if self.expires_at is not None and self.expires_at <= self.approved_at:
            raise ValueError("expires_at must be strictly after approved_at")
        return self


# ---------------------------------------------------------------------------
# 7. Revocation Record
# ---------------------------------------------------------------------------

class RevocationRecord(BaseModel):
    """Terminal or immediate kill-switch record invalidating approvals/releases."""
    model_config = ConfigDict(frozen=True)

    revocation_id: str = Field(min_length=4, max_length=120)
    scope: RevocationScope
    target_identifier: str = Field(min_length=2, max_length=120, description="source_id, release_id, approval_id, or model_id")
    reason_code: str = Field(min_length=3, max_length=80)
    description: str = Field(min_length=5, max_length=400)
    revoked_by: str = Field(min_length=2, max_length=100)
    revoked_at: datetime
    expires_at: datetime | None = Field(default=None, description="Optional timestamp after which temporary revocation expires")

    @field_validator("revoked_at")
    @classmethod
    def revoked_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("revoked_at must be timezone-aware")
        return v

    @field_validator("expires_at")
    @classmethod
    def expires_at_is_tz_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.utcoffset() is None:
            raise ValueError("expires_at must be timezone-aware")
        return v


class RevocationConfigurationManifest(BaseModel):
    """Authoritative version-controlled manifest defining persisted revocations."""
    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(default="1.0.0", min_length=1, max_length=20)
    description: str = Field(min_length=5, max_length=255)
    updated_at: datetime
    revocations: tuple[RevocationRecord, ...] = ()

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        if v != "1.0.0":
            raise ValueError(f"Unsupported revocation manifest schema version: '{v}'. Only '1.0.0' is supported.")
        return v

    @field_validator("updated_at")
    @classmethod
    def updated_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("updated_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 8. Model Lineage Record
# ---------------------------------------------------------------------------

class ModelLineageRecord(BaseModel):
    """Cryptographic and governance lineage binding an ML model to its training data."""
    model_config = ConfigDict(frozen=True)

    model_id: str = Field(min_length=3, max_length=120)
    market_id: Literal["IN", "US", "UK", "AU", "SG"]
    algorithm_name: str = Field(min_length=2, max_length=100)
    model_artifact_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    preprocessor_artifact_sha256: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    training_data_source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    training_data_hash: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    license_tier: str = Field(min_length=2, max_length=80)
    trained_at: datetime
    zero_retraining_certified: bool = True
    inference_rights_status: PermissionState = PermissionState.APPROVED

    @field_validator("model_artifact_sha256", "preprocessor_artifact_sha256", "training_data_hash")
    @classmethod
    def normalize_model_hashes(cls, v: str) -> str:
        return v.upper()

    @field_validator("trained_at")
    @classmethod
    def trained_at_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("trained_at must be timezone-aware")
        return v


# ---------------------------------------------------------------------------
# 9. Governance Evaluation Result
# ---------------------------------------------------------------------------

class GovernanceEvaluationResult(BaseModel):
    """Publicly safe, auditable outcome of a policy engine evaluation."""
    model_config = ConfigDict(frozen=True)

    allowed: bool
    decision_status: PermissionState
    reason_code: str = Field(min_length=3, max_length=80)
    source_id: str
    dataset_release_id: str | None = None
    policy_version: str = Field(default="2.0.0")
    audit_ref: str = Field(min_length=8, max_length=64)
    caveats: tuple[str, ...] = ()

    @model_validator(mode="after")
    def sanitization_guard(self) -> "GovernanceEvaluationResult":
        # Disallow filesystem paths or raw coordinate leaks in reason_code or caveats
        forbidden_substrings = (r":\\", r":/", "/data/raw", "/data/processed", "password", "token", "secret")
        text_to_check = f"{self.reason_code} {' '.join(self.caveats)}".lower()
        for forbidden in forbidden_substrings:
            if forbidden.lower() in text_to_check:
                raise ValueError(f"Information leakage detected: {forbidden} cannot appear in public evaluation result")
        return self


# ---------------------------------------------------------------------------
# 10. Governance Audit Event
# ---------------------------------------------------------------------------

class GovernanceAuditEvent(BaseModel):
    """Immutable audit record emitted upon any policy decision or lifecycle transition."""
    model_config = ConfigDict(frozen=True)

    event_id: str = Field(min_length=8, max_length=64)
    timestamp: datetime
    event_type: Literal["POLICY_EVALUATION", "LIFECYCLE_TRANSITION", "REVOCATION_RECORDED", "CACHE_INVALIDATED"]
    source_id: str
    operation: GovernanceOperation | None = None
    outcome: Literal["ALLOWED", "DENIED", "TRANSITIONED", "REVOKED"]
    reason_code: str
    audit_ref: str

    @field_validator("timestamp")
    @classmethod
    def timestamp_is_tz_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return v

