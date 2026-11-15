from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Final, Iterable
from pydantic import BaseModel, ConfigDict, Field

from src.backend.governance.schemas import (
    ApprovalRecord,
    CommercialStatus,
    DatasetRelease,
    GovernanceEvaluationResult,
    GovernanceOperation,
    LifecycleState,
    ModelLineageRecord,
    PermissionState,
    RevocationScope,
    SourceIdentity,
    TargetAudience,
)
from src.backend.governance.revocation import RevocationRegistry


class GovernanceEvaluationRequest(BaseModel):
    """Input payload submitted to the policy engine for authorization evaluation."""
    model_config = ConfigDict(frozen=True)

    source_id: str
    operation: GovernanceOperation
    dataset_id: str | None = None
    dataset_release_id: str | None = None
    artifact_sha256: str | None = None
    license_version: str | None = None
    geography: str | None = None
    audience: TargetAudience | None = None
    commercial_status: CommercialStatus | None = None
    model_id: str | None = None
    model_lineage: ModelLineageRecord | None = None
    required_conditions_met: bool = True


class GovernancePolicyEngine:
    """
    Authoritative, in-memory, fail-closed policy engine enforcing multi-market governance.
    Designed for zero external database dependencies and sub-millisecond evaluation.
    """

    POLICY_VERSION = "2.0.0"

    SERVING_OPERATIONS: Final[frozenset[GovernanceOperation]] = frozenset({
        GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        GovernanceOperation.COMMERCIAL_AGGREGATE_DISPLAY,
        GovernanceOperation.REDISTRIBUTION_RAW,
        GovernanceOperation.PUBLIC_MODEL_INFERENCE,
        GovernanceOperation.COMMERCIAL_MODEL_INFERENCE,
    })

    def __init__(
        self,
        sources: Iterable[SourceIdentity] = (),
        releases: Iterable[DatasetRelease] = (),
        approvals: Iterable[ApprovalRecord] = (),
        revocation_registry: RevocationRegistry | None = None,
    ) -> None:
        self._sources: dict[str, SourceIdentity] = {s.source_id: s for s in sources}
        self._releases: dict[str, DatasetRelease] = {r.release_id: r for r in releases}
        self._approvals_by_key: dict[tuple[str, str, GovernanceOperation], list[ApprovalRecord]] = {}
        for a in approvals:
            key = (a.source_id, a.dataset_release_id, a.intended_operation)
            self._approvals_by_key.setdefault(key, []).append(a)

        self._revocation_registry = revocation_registry if revocation_registry is not None else RevocationRegistry()

        # Automatically bind dataset and source hierarchy for registered releases
        for r in releases:
            self._revocation_registry.bind_hierarchy(
                release_id=r.release_id,
                dataset_id=r.dataset_id,
                source_id=r.source_id,
            )

    @property
    def revocation_registry(self) -> RevocationRegistry:
        return self._revocation_registry

    def invalidate_cache(self) -> None:
        """Invalidate in-memory policy cache."""
        self._revocation_registry.invalidate_cache()

    def _generate_audit_ref(self, req: GovernanceEvaluationRequest) -> str:
        entropy = f"{req.source_id}:{req.operation}:{req.dataset_release_id}:{datetime.now(timezone.utc).isoformat()}"
        digest = hashlib.sha256(entropy.encode()).hexdigest()[:16]
        return f"gov-eval-{digest}"

    def evaluate(self, request: GovernanceEvaluationRequest) -> GovernanceEvaluationResult:
        """
        Authoritatively evaluate an operation request against registered policy gates.
        Fails closed on any ambiguity, mismatch, expiration, or revocation.
        """
        audit_ref = self._generate_audit_ref(request)
        source_id = request.source_id
        release = self._releases.get(request.dataset_release_id) if request.dataset_release_id else None
        dataset_id = request.dataset_id or (release.dataset_id if release else None)

        # -------------------------------------------------------------------
        # Gate 1: Revocation Check (Hierarchical: Source -> Dataset -> Release -> Model)
        # -------------------------------------------------------------------
        if not self._revocation_registry.is_healthy:
            # Governed operations fail closed when revocation registry is degraded/unverified.
            # Preserve unaffected India/USA prediction availability where policy permits.
            if request.operation not in (
                GovernanceOperation.INTERNAL_MODEL_INFERENCE,
                GovernanceOperation.INTERNAL_ANALYTICS,
            ):
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_REVOCATION_REGISTRY_UNAVAILABLE",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=(
                        f"Revocation registry is degraded or unverified ({self._revocation_registry.status}). Governed operation denied.",
                    ),
                )

        revocation = self._revocation_registry.check_revocation(
            source_id=source_id,
            dataset_id=dataset_id,
            dataset_release_id=request.dataset_release_id,
            model_id=request.model_id,
        )
        if revocation:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.REVOKED,
                reason_code=f"GOV_DENIED_REVOKED_{revocation.scope.value}",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=(f"Revoked by {revocation.revoked_by}: {revocation.reason_code}",),
            )

        # -------------------------------------------------------------------
        # Gate 2: Source Registration Check
        # -------------------------------------------------------------------
        source = self._sources.get(source_id)
        if not source:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_UNKNOWN_SOURCE",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Source is not declared in the authoritative data catalog.",),
            )

        # Sources with REVIEW_REQUIRED or UNKNOWN cannot serve public or commercial data
        if source.default_permission_state in (PermissionState.REVIEW_REQUIRED, PermissionState.UNKNOWN):
            if request.operation in (
                GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
                GovernanceOperation.COMMERCIAL_AGGREGATE_DISPLAY,
                GovernanceOperation.REDISTRIBUTION_RAW,
                GovernanceOperation.PUBLIC_MODEL_INFERENCE,
                GovernanceOperation.COMMERCIAL_MODEL_INFERENCE,
            ):
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.REVIEW_REQUIRED,
                    reason_code="GOV_DENIED_UNREVIEWED_SOURCE",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Source legal reuse review is pending or unresolved.",),
                )

        # -------------------------------------------------------------------
        # Gate 3: Model Lineage Verification (for inference operations)
        # -------------------------------------------------------------------
        if request.operation in (
            GovernanceOperation.INTERNAL_MODEL_INFERENCE,
            GovernanceOperation.PUBLIC_MODEL_INFERENCE,
            GovernanceOperation.COMMERCIAL_MODEL_INFERENCE,
        ):
            if not request.model_id or not request.model_lineage:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_MODEL_LINEAGE_MISSING",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Model inference requires verified cryptographic training lineage.",),
                )

            lineage = request.model_lineage
            if lineage.model_id != request.model_id:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_MODEL_CHECKSUM_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Model identifier does not match declared lineage record.",),
                )

            # Commercial model inference requires commercial AI rights on training data
            if request.operation == GovernanceOperation.COMMERCIAL_MODEL_INFERENCE:
                if "Tier 1" in lineage.license_tier or lineage.inference_rights_status != PermissionState.APPROVED:
                    return GovernanceEvaluationResult(
                        allowed=False,
                        decision_status=PermissionState.DENIED,
                        reason_code="GOV_DENIED_COMMERCIAL_RESTRICTION",
                        source_id=source_id,
                        dataset_release_id=request.dataset_release_id,
                        policy_version=self.POLICY_VERSION,
                        audit_ref=audit_ref,
                        caveats=("Underlying model training data does not permit commercial AI deployment.",),
                    )

            # For model inference with verified lineage, authorize
            return GovernanceEvaluationResult(
                allowed=True,
                decision_status=PermissionState.APPROVED,
                reason_code="GOV_ALLOWED_RESEARCH_INFERENCE" if request.operation == GovernanceOperation.INTERNAL_MODEL_INFERENCE else "GOV_ALLOWED",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Model inference authorized under verified model lineage.",),
            )

        # -------------------------------------------------------------------
        # Gate 4: Dataset Release Integrity & Lifecycle State Check
        # -------------------------------------------------------------------
        if not request.dataset_release_id:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_RELEASE_REQUIRED",
                source_id=source_id,
                dataset_release_id=None,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Operation requires an explicit dataset release identifier.",),
            )

        if not release:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_RELEASE_NOT_FOUND",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Dataset release is not registered.",),
            )

        if release.lifecycle_state == LifecycleState.SUSPENDED:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_RELEASE_SUSPENDED",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Release is currently suspended pending quality revalidation.",),
            )

        if release.lifecycle_state == LifecycleState.REVOKED:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.REVOKED,
                reason_code="GOV_DENIED_RELEASE_REVOKED",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Release has been permanently revoked.",),
            )

        if release.lifecycle_state == LifecycleState.EXPIRED:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.EXPIRED,
                reason_code="GOV_DENIED_RELEASE_EXPIRED",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Release lifecycle validity has expired.",),
            )

        # Serving operations (display, redistribution, public/commercial inference) strictly require USE_APPROVED or PUBLISHED
        if request.operation in self.SERVING_OPERATIONS:
            if release.lifecycle_state not in (LifecycleState.USE_APPROVED, LifecycleState.PUBLISHED):
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_LIFECYCLE_NOT_SERVABLE",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=(
                        f"Serving operation '{request.operation.value}' requires USE_APPROVED or PUBLISHED lifecycle state "
                        f"(currently '{release.lifecycle_state.value}').",
                    ),
                )

        # Verify Exact Physical Artifact Checksum
        if request.artifact_sha256:
            if request.artifact_sha256.upper() != release.primary_artifact.sha256_hex.upper():
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_CHECKSUM_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Physical artifact SHA-256 does not match release manifest.",),
                )

        # -------------------------------------------------------------------
        # Gate 5: Approval Record & Scope Binding Evaluation
        # -------------------------------------------------------------------
        appr_key = (source_id, request.dataset_release_id, request.operation)
        approvals = self._approvals_by_key.get(appr_key, [])
        if not approvals:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_APPROVAL_MISSING",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("No valid ApprovalRecord found for source, release, and operation.",),
            )

        now = datetime.now(timezone.utc)
        valid_approval: ApprovalRecord | None = None
        has_revoked_approval = False
        revoked_approval_reason: str | None = None
        expired_count = 0
        version_mismatch_count = 0
        checksum_mismatch_count = 0

        for appr in approvals:
            if not appr.is_active:
                continue

            # Verify revocation at every applicable scope (Source, Dataset, Release, Approval, Model)
            appr_revocation = self._revocation_registry.check_revocation(
                source_id=source_id,
                dataset_id=dataset_id,
                dataset_release_id=request.dataset_release_id,
                approval_id=appr.approval_id,
                model_id=request.model_id,
            )
            if appr_revocation:
                if appr_revocation.scope == RevocationScope.APPROVAL:
                    has_revoked_approval = True
                    revoked_approval_reason = appr_revocation.reason_code
                    continue
                else:
                    # Broader scope revocation (source, dataset, release, model) overrides immediately
                    return GovernanceEvaluationResult(
                        allowed=False,
                        decision_status=PermissionState.REVOKED,
                        reason_code=f"GOV_DENIED_REVOKED_{appr_revocation.scope.value}",
                        source_id=source_id,
                        dataset_release_id=request.dataset_release_id,
                        policy_version=self.POLICY_VERSION,
                        audit_ref=audit_ref,
                        caveats=(f"Revoked by {appr_revocation.revoked_by}: {appr_revocation.reason_code}",),
                    )

            # Check expiration
            if appr.expires_at and appr.expires_at <= now:
                expired_count += 1
                continue

            # Check exact dataset version match
            if appr.dataset_version != release.dataset_version:
                version_mismatch_count += 1
                continue

            # Check exact artifact hash binding
            if appr.artifact_sha256 != release.primary_artifact.sha256_hex.upper():
                checksum_mismatch_count += 1
                continue

            # Check license version mismatch
            if request.license_version and request.license_version != appr.license_version:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_LICENSE_VERSION_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Requested license version does not match approved license terms.",),
                )

            # Check geography mismatch
            if request.geography and request.geography not in appr.geography:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_GEOGRAPHY_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=(f"Requested geography '{request.geography}' outside approved scope.",),
                )

            # Check audience mismatch
            if request.audience and request.audience != appr.audience:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_AUDIENCE_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Requested audience does not match approved audience tier.",),
                )

            # Check commercial status restriction
            if request.commercial_status == CommercialStatus.COMMERCIAL_ALLOWED and appr.commercial_status != CommercialStatus.COMMERCIAL_ALLOWED:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_COMMERCIAL_RESTRICTION",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Commercial use requested on non-commercially approved release.",),
                )

            valid_approval = appr
            break

        if not valid_approval:
            if has_revoked_approval:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.REVOKED,
                    reason_code="GOV_DENIED_APPROVAL_REVOKED",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=(f"Approval record has been explicitly revoked: {revoked_approval_reason}",),
                )
            if expired_count > 0:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.EXPIRED,
                    reason_code="GOV_DENIED_APPROVAL_EXPIRED",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Approval record temporal validity has expired.",),
                )
            if version_mismatch_count > 0:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_VERSION_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Approval was granted for a different dataset version.",),
                )
            if checksum_mismatch_count > 0:
                return GovernanceEvaluationResult(
                    allowed=False,
                    decision_status=PermissionState.DENIED,
                    reason_code="GOV_DENIED_CHECKSUM_MISMATCH",
                    source_id=source_id,
                    dataset_release_id=request.dataset_release_id,
                    policy_version=self.POLICY_VERSION,
                    audit_ref=audit_ref,
                    caveats=("Approval artifact hash does not match release artifact hash.",),
                )
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.DENIED,
                reason_code="GOV_DENIED_APPROVAL_INVALID",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Approval record is inactive or invalid.",),
            )

        # -------------------------------------------------------------------
        # Gate 6: Conditional Requirements
        # -------------------------------------------------------------------
        if not request.required_conditions_met:
            return GovernanceEvaluationResult(
                allowed=False,
                decision_status=PermissionState.CONDITIONAL,
                reason_code="GOV_DENIED_CONDITIONS_UNMET",
                source_id=source_id,
                dataset_release_id=request.dataset_release_id,
                policy_version=self.POLICY_VERSION,
                audit_ref=audit_ref,
                caveats=("Mandatory statutory caveats or suppression filters were not applied.",),
            )

        # -------------------------------------------------------------------
        # All Gates Cleared: Operation Authorized
        # -------------------------------------------------------------------
        return GovernanceEvaluationResult(
            allowed=True,
            decision_status=PermissionState.APPROVED,
            reason_code="GOV_ALLOWED",
            source_id=source_id,
            dataset_release_id=request.dataset_release_id,
            policy_version=self.POLICY_VERSION,
            audit_ref=audit_ref,
            caveats=("Operation fully authorized under valid approval record.",),
        )
