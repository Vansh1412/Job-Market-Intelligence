from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import pytest
from pydantic import AnyHttpUrl, ValidationError

from src.backend.governance.schemas import (
    ApprovalRecord,
    ArtifactIntegrity,
    CommercialStatus,
    DatasetRelease,
    GovernanceEvaluationResult,
    GovernanceOperation,
    LifecycleState,
    ModelLineageRecord,
    PermissionState,
    RevocationRecord,
    RevocationScope,
    SourceIdentity,
    TargetAudience,
)
from src.backend.governance.lifecycle import (
    InvalidLifecycleTransitionError,
    get_allowed_transitions,
    is_recoverable_state,
    is_terminal_state,
    validate_lifecycle_transition,
)
from src.backend.governance.revocation import RevocationRegistry
from src.backend.governance.engine import (
    GovernanceEvaluationRequest,
    GovernancePolicyEngine,
)
from src.backend.governance.training_governance import (
    TrainingAuthorization,
    TrainingGovernanceGate,
    verify_ci_training_compliance,
)
from src.backend.data_catalog.registry import get_source


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_source_identity() -> SourceIdentity:
    return SourceIdentity(
        source_id="uk.ons.ashe",
        source_name="Annual Survey of Hours and Earnings",
        publisher_name="Office for National Statistics",
        canonical_publication_url=AnyHttpUrl("https://www.ons.gov.uk/datasets/regionbyoccupation4digitsocashetable15"),
        acquisition_url=AnyHttpUrl("https://www.ons.gov.uk/datasets/regionbyoccupation4digitsocashetable15"),
        artifact_download_url=AnyHttpUrl("https://www.ons.gov.uk/file?uri=/ashetable152025revised.zip"),
        license_name="Open Government Licence",
        license_version="v3.0",
        default_permission_state=PermissionState.REVIEW_REQUIRED,
        registered_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_artifact() -> ArtifactIntegrity:
    return ArtifactIntegrity(
        artifact_id="ashe-2025-csv",
        file_name="ashe_2025_full_time_annual_gross_median_gb.csv",
        size_bytes=1048576,
        sha256_hex="DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E",
        verified_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_release(sample_artifact: ArtifactIntegrity) -> DatasetRelease:
    return DatasetRelease(
        release_id="ashe-2025r-v1.0.2",
        source_id="uk.ons.ashe",
        dataset_version="2025-revised",
        primary_artifact=sample_artifact,
        reference_period="Tax year ending 5 April 2025",
        geographic_coverage=("London", "South East", "North West"),
        record_count=4532,
        lifecycle_state=LifecycleState.USE_APPROVED,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_approval() -> ApprovalRecord:
    now = datetime.now(timezone.utc)
    return ApprovalRecord(
        approval_id="appr-ashe-pub-001",
        source_id="uk.ons.ashe",
        dataset_release_id="ashe-2025r-v1.0.2",
        dataset_version="2025-revised",
        artifact_sha256="DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E",
        license_version="v3.0",
        intended_operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        geography=("London", "South East", "North West"),
        reference_period="Tax year ending 5 April 2025",
        audience=TargetAudience.PUBLIC_UNAUTHENTICATED,
        commercial_status=CommercialStatus.NON_COMMERCIAL_ONLY,
        approval_evidence="LEGAL-REVIEW-TICKET-2026-0941",
        approved_by="Data Governance Board",
        approved_at=now - timedelta(days=1),
        expires_at=now + timedelta(days=365),
        is_active=True,
    )


# ---------------------------------------------------------------------------
# Test Requirements A through T
# ---------------------------------------------------------------------------

def test_req_a_permission_state_validation():
    """Requirement A: Validate that PermissionState distinguishes all 7 mandated values."""
    expected = {"UNKNOWN", "REVIEW_REQUIRED", "APPROVED", "CONDITIONAL", "DENIED", "EXPIRED", "REVOKED"}
    actual = {s.value for s in PermissionState}
    assert actual == expected


def test_req_b_unknown_permissions_denied_by_default(sample_source_identity: SourceIdentity):
    """Requirement B: Unknown/unregistered sources are strictly denied by default."""
    engine = GovernancePolicyEngine(sources=(sample_source_identity,))
    req = GovernanceEvaluationRequest(
        source_id="unregistered.source.id",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="rel-123",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.DENIED
    assert res.reason_code == "GOV_DENIED_UNKNOWN_SOURCE"


def test_req_c_conditional_permissions_with_unmet_conditions(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement C: Conditional permission fails closed when mandatory conditions are unmet."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        artifact_sha256="DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E",
        required_conditions_met=False,  # Conditions NOT met
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.CONDITIONAL
    assert res.reason_code == "GOV_DENIED_CONDITIONS_UNMET"


def test_req_d_approval_bound_to_exact_dataset_hash(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement D: Approval fails closed if physical artifact hash diverges from approved hash."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        artifact_sha256="0000000000000000000000000000000000000000000000000000000000000000",  # Divergent hash
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_CHECKSUM_MISMATCH"


def test_req_e_approval_invalidated_by_changed_dataset_version(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement E: Approval is invalidated if dataset version changes."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    mismatched_release = sample_release.model_copy(update={"dataset_version": "2026-provisional"})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(mismatched_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_VERSION_MISMATCH"


def test_req_f_license_version_mismatch(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement F: Rejects operation if requested license version does not match approved terms."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        license_version="v2.0",  # Divergent from approved v3.0
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_LICENSE_VERSION_MISMATCH"


def test_req_g_geography_and_audience_mismatch(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement G: Operation denied if requested outside approved geography or audience tier."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
    )
    # Geography mismatch
    req_geo = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        geography="Scotland",  # Not in approved ("London", "South East", "North West")
    )
    res_geo = engine.evaluate(req_geo)
    assert not res_geo.allowed
    assert res_geo.reason_code == "GOV_DENIED_GEOGRAPHY_MISMATCH"

    # Audience mismatch
    req_aud = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        geography="London",
        audience=TargetAudience.PAID_COMMERCIAL,  # Approved is PUBLIC_UNAUTHENTICATED
    )
    res_aud = engine.evaluate(req_aud)
    assert not res_aud.allowed
    assert res_aud.reason_code == "GOV_DENIED_AUDIENCE_MISMATCH"


def test_req_h_commercial_use_without_commercial_permission(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement H: Commercial use denied if release is approved for non-commercial only."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
        commercial_status=CommercialStatus.COMMERCIAL_ALLOWED,  # Approval is NON_COMMERCIAL_ONLY
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_COMMERCIAL_RESTRICTION"


def test_req_i_expired_approval(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement I: Expired approval record fails closed with EXPIRED status."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    expired_approval = sample_approval.model_copy(update={
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)
    })
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(expired_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.EXPIRED
    assert res.reason_code == "GOV_DENIED_APPROVAL_EXPIRED"


def test_req_j_revoked_approval(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement J: Direct approval revocation blocks serving immediately."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_registry = RevocationRegistry()
    rev_registry.register(RevocationRecord(
        revocation_id="rev-001",
        scope=RevocationScope.APPROVAL,
        target_identifier="appr-ashe-pub-001",
        reason_code="DATA_QUALITY_AUDIT_FAILURE",
        description="Immediate revocation following sampling error discovery.",
        revoked_by="Governance Lead",
        revoked_at=datetime.now(timezone.utc),
    ))
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=rev_registry,
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    # Execute authoritative engine evaluation: revoked approval MUST cause engine denial
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_APPROVAL_REVOKED"
    assert "DATA_QUALITY_AUDIT_FAILURE" in res.caveats[0]


def test_req_k_source_wide_revocation(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement K: Source-wide revocation halts all releases and operations under that source."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_registry = RevocationRegistry()
    rev_registry.register(RevocationRecord(
        revocation_id="rev-source-wide",
        scope=RevocationScope.SOURCE,
        target_identifier="uk.ons.ashe",
        reason_code="LEGAL_TAKEDOWN_DEMAND",
        description="Formal cease and desist from rights holder.",
        revoked_by="Chief Compliance Officer",
        revoked_at=datetime.now(timezone.utc),
    ))
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=rev_registry,
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_SOURCE"


def test_req_l_release_specific_revocation(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement L: Release-level revocation blocks only the specific release."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_registry = RevocationRegistry()
    rev_registry.register(RevocationRecord(
        revocation_id="rev-rel-001",
        scope=RevocationScope.RELEASE,
        target_identifier="ashe-2025r-v1.0.2",
        reason_code="DATASET_CORRUPTION",
        description="Corrupted column headers detected.",
        revoked_by="Data Lead",
        revoked_at=datetime.now(timezone.utc),
    ))
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=rev_registry,
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_RELEASE"


def test_req_m_suspended_release(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement M: Suspended release blocks serving until revalidation."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    suspended_release = sample_release.model_copy(update={"lifecycle_state": LifecycleState.SUSPENDED})
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(suspended_release,),
        approvals=(sample_approval,),
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_RELEASE_SUSPENDED"


def test_req_n_model_lineage_missing_or_mismatched(sample_source_identity: SourceIdentity):
    """Requirement N: Model inference denied if model lineage is missing or violates zero-retraining."""
    us_source = SourceIdentity(
        source_id="us.jobintel.market-data",
        source_name="JobIntel US Market Data",
        publisher_name="JobIntel",
        license_name="Proprietary Tier 1",
        license_version="1.0",
        default_permission_state=PermissionState.APPROVED,
        registered_at=datetime.now(timezone.utc),
    )
    engine = GovernancePolicyEngine(sources=(sample_source_identity, us_source))
    
    # Missing lineage
    req_no_lin = GovernanceEvaluationRequest(
        source_id="us.jobintel.market-data",
        operation=GovernanceOperation.PUBLIC_MODEL_INFERENCE,
        model_id="us-salary-xgb",
        model_lineage=None,
    )
    res_no_lin = engine.evaluate(req_no_lin)
    assert not res_no_lin.allowed
    assert res_no_lin.reason_code == "GOV_DENIED_MODEL_LINEAGE_MISSING"

    # Lineage present, commercial inference on Tier 1 DataForge
    tier1_lineage = ModelLineageRecord(
        model_id="us-salary-xgb",
        market_id="US",
        algorithm_name="XGBRegressor",
        model_artifact_sha256="3D4468E2D79FA71804E1D02A7E15462D4A32BC6663E9733475225E9385C1E09B",
        preprocessor_artifact_sha256="F9D9B22C99757D8412F5868C65449A39A1C5FA2BA05BAEFE762D770281F998D8",
        training_data_source_id="us.jobintel.market-data",
        training_data_hash="AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899",
        license_tier="Tier 1 (Internal Analytics)",
        trained_at=datetime.now(timezone.utc),
        zero_retraining_certified=True,
    )
    req_comm = GovernanceEvaluationRequest(
        source_id="us.jobintel.market-data",
        operation=GovernanceOperation.COMMERCIAL_MODEL_INFERENCE,
        model_id="us-salary-xgb",
        model_lineage=tier1_lineage,
    )
    res_comm = engine.evaluate(req_comm)
    assert not res_comm.allowed
    assert res_comm.reason_code == "GOV_DENIED_COMMERCIAL_RESTRICTION"


def test_req_o_uk_remains_blocked_under_unresolved_permission(sample_source_identity: SourceIdentity):
    """Requirement O: UK ASHE data remains blocked while default_permission_state is REVIEW_REQUIRED."""
    engine = GovernancePolicyEngine(sources=(sample_source_identity,))
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVIEW_REQUIRED
    assert res.reason_code == "GOV_DENIED_UNREVIEWED_SOURCE"


def test_req_p_india_usa_prediction_regression():
    """Requirement P: India and USA inference evaluation succeeds cleanly under research policy."""
    us_source = SourceIdentity(
        source_id="us.jobintel.market-data",
        source_name="JobIntel US Market Data",
        publisher_name="JobIntel",
        license_name="Proprietary Tier 1",
        license_version="1.0",
        default_permission_state=PermissionState.APPROVED,
        registered_at=datetime.now(timezone.utc),
    )
    lineage = ModelLineageRecord(
        model_id="us-salary-xgb",
        market_id="US",
        algorithm_name="XGBRegressor",
        model_artifact_sha256="3D4468E2D79FA71804E1D02A7E15462D4A32BC6663E9733475225E9385C1E09B",
        preprocessor_artifact_sha256="F9D9B22C99757D8412F5868C65449A39A1C5FA2BA05BAEFE762D770281F998D8",
        training_data_source_id="us.jobintel.market-data",
        training_data_hash="AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899",
        license_tier="Tier 1 (Internal Analytics)",
        trained_at=datetime.now(timezone.utc),
        zero_retraining_certified=True,
    )
    engine = GovernancePolicyEngine(sources=(us_source,))
    req = GovernanceEvaluationRequest(
        source_id="us.jobintel.market-data",
        operation=GovernanceOperation.PUBLIC_MODEL_INFERENCE,
        model_id="us-salary-xgb",
        model_lineage=lineage,
    )
    res = engine.evaluate(req)
    assert res.allowed
    assert res.decision_status == PermissionState.APPROVED
    assert res.reason_code == "GOV_ALLOWED"


def test_req_q_malformed_manifest_isolation(sample_source_identity: SourceIdentity):
    """Requirement Q: Corrupting or breaking UK governance state does NOT block USA/India evaluation."""
    us_source = SourceIdentity(
        source_id="us.jobintel.market-data",
        source_name="JobIntel US Market Data",
        publisher_name="JobIntel",
        license_name="Proprietary Tier 1",
        license_version="1.0",
        default_permission_state=PermissionState.APPROVED,
        registered_at=datetime.now(timezone.utc),
    )
    lineage = ModelLineageRecord(
        model_id="us-salary-xgb",
        market_id="US",
        algorithm_name="XGBRegressor",
        model_artifact_sha256="3D4468E2D79FA71804E1D02A7E15462D4A32BC6663E9733475225E9385C1E09B",
        preprocessor_artifact_sha256="F9D9B22C99757D8412F5868C65449A39A1C5FA2BA05BAEFE762D770281F998D8",
        training_data_source_id="us.jobintel.market-data",
        training_data_hash="AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899",
        license_tier="Tier 1 (Internal Analytics)",
        trained_at=datetime.now(timezone.utc),
        zero_retraining_certified=True,
    )
    # UK source is broken / unreviewed
    engine = GovernancePolicyEngine(sources=(sample_source_identity, us_source))

    # Evaluate UK -> Fails
    uk_res = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="rel-broken",
    ))
    assert not uk_res.allowed

    # Evaluate US -> Passes with complete failure isolation
    us_res = engine.evaluate(GovernanceEvaluationRequest(
        source_id="us.jobintel.market-data",
        operation=GovernanceOperation.PUBLIC_MODEL_INFERENCE,
        model_id="us-salary-xgb",
        model_lineage=lineage,
    ))
    assert us_res.allowed


def test_req_r_policy_cache_invalidation(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """Requirement R: Cache invalidation / dynamic revocation flips subsequent policy decisions immediately."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_reg = RevocationRegistry()
    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=rev_reg,
    )
    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    # Decision 1: Initial evaluation is ALLOWED
    res1 = engine.evaluate(req)
    assert res1.allowed
    assert res1.decision_status == PermissionState.APPROVED
    assert res1.reason_code == "GOV_ALLOWED"

    # Dynamic Revocation occurs and cache is invalidated
    rev_reg.register(RevocationRecord(
        revocation_id="rev-dyn-001",
        scope=RevocationScope.APPROVAL,
        target_identifier="appr-ashe-pub-001",
        reason_code="EMERGENCY_DATA_KILL_SWITCH",
        description="Emergency revocation during active session.",
        revoked_by="Chief Compliance Officer",
        revoked_at=datetime.now(timezone.utc),
    ))
    engine.invalidate_cache()

    # Decision 2: Subsequent evaluation FLIPS from ALLOWED to DENIED/REVOKED
    res2 = engine.evaluate(req)
    assert not res2.allowed
    assert res2.decision_status == PermissionState.REVOKED
    assert res2.reason_code == "GOV_DENIED_APPROVAL_REVOKED"


def test_req_s_invalid_lifecycle_transitions():
    """Requirement S: Lifecycle state transition engine enforces formal rules and blocks invalid jumps."""
    # Valid transition
    validate_lifecycle_transition(LifecycleState.SOURCE_REGISTERED, LifecycleState.REUSE_REVIEW_REQUIRED)

    # Invalid jump (registered -> published)
    with pytest.raises(InvalidLifecycleTransitionError):
        validate_lifecycle_transition(LifecycleState.SOURCE_REGISTERED, LifecycleState.PUBLISHED)

    # Terminal state check: REVOKED cannot transition
    assert is_terminal_state(LifecycleState.REVOKED)
    with pytest.raises(InvalidLifecycleTransitionError):
        validate_lifecycle_transition(LifecycleState.REVOKED, LifecycleState.PUBLISHED)

    # Recoverable states check
    assert is_recoverable_state(LifecycleState.SUSPENDED)
    assert is_recoverable_state(LifecycleState.EXPIRED)


def test_req_t_url_metadata_field_validation():
    """Requirement T: Catalog DataSource supports tripartite URL fields additively."""
    src = get_source("uk.ons.ashe")
    assert src.canonical_publication_url is not None
    assert "regionbyoccupation4digitsocashetable15" in str(src.canonical_publication_url)
    assert src.acquisition_url is not None
    assert src.artifact_download_url is not None
    assert "ashetable152025revised.zip" in str(src.artifact_download_url)
    # Original source_reference must remain strictly preserved
    assert src.source_reference is not None
    assert "regionbyoccupation4digitsocashetable15" in str(src.source_reference)


# ===========================================================================
# SPRINT 2C.2 CORRECTIVE & HIERARCHICAL INTEGRATION TESTS (F-01 through F-07)
# ===========================================================================

def test_f07_dataset_scope_revocation_affects_all_releases(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """F-07: Dataset-wide revocation invalidates all releases belonging to that dataset."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rel1 = sample_release.model_copy(update={"release_id": "ashe-rel-001", "dataset_id": "uk.ons.ashe.table15"})
    rel2 = sample_release.model_copy(update={"release_id": "ashe-rel-002", "dataset_id": "uk.ons.ashe.table15"})
    appr1 = sample_approval.model_copy(update={"approval_id": "appr-001", "dataset_release_id": "ashe-rel-001"})
    appr2 = sample_approval.model_copy(update={"approval_id": "appr-002", "dataset_release_id": "ashe-rel-002"})

    rev_reg = RevocationRegistry()
    rev_reg.register(RevocationRecord(
        revocation_id="rev-ds-001",
        scope=RevocationScope.DATASET,
        target_identifier="uk.ons.ashe.table15",
        reason_code="DATASET_STATUTORY_DEFECT",
        description="Statutory methodological defect affecting entire dataset family.",
        revoked_by="Chief Statistician",
        revoked_at=datetime.now(timezone.utc),
    ))

    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(rel1, rel2),
        approvals=(appr1, appr2),
        revocation_registry=rev_reg,
    )

    req1 = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-rel-001",
    )
    req2 = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-rel-002",
    )

    res1 = engine.evaluate(req1)
    res2 = engine.evaluate(req2)

    assert not res1.allowed
    assert res1.decision_status == PermissionState.REVOKED
    assert res1.reason_code == "GOV_DENIED_REVOKED_DATASET"

    assert not res2.allowed
    assert res2.decision_status == PermissionState.REVOKED
    assert res2.reason_code == "GOV_DENIED_REVOKED_DATASET"


def test_f07_release_scope_revocation_isolates_target_release(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """F-07: Release-level revocation halts target release only; sibling release remains unaffected."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rel1 = sample_release.model_copy(update={"release_id": "ashe-rel-001", "dataset_id": "uk.ons.ashe.table15"})
    rel2 = sample_release.model_copy(update={"release_id": "ashe-rel-002", "dataset_id": "uk.ons.ashe.table15"})
    appr1 = sample_approval.model_copy(update={"approval_id": "appr-001", "dataset_release_id": "ashe-rel-001"})
    appr2 = sample_approval.model_copy(update={"approval_id": "appr-002", "dataset_release_id": "ashe-rel-002"})

    rev_reg = RevocationRegistry()
    rev_reg.register(RevocationRecord(
        revocation_id="rev-rel-001",
        scope=RevocationScope.RELEASE,
        target_identifier="ashe-rel-001",
        reason_code="EXTRACTION_CORRUPTION",
        description="Corrupted extraction for rel-001 only.",
        revoked_by="Data Lead",
        revoked_at=datetime.now(timezone.utc),
    ))

    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(rel1, rel2),
        approvals=(appr1, appr2),
        revocation_registry=rev_reg,
    )

    # Rel 1 must be denied
    req1 = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-rel-001",
    )
    res1 = engine.evaluate(req1)
    assert not res1.allowed
    assert res1.decision_status == PermissionState.REVOKED
    assert res1.reason_code == "GOV_DENIED_REVOKED_RELEASE"

    # Rel 2 must be allowed
    req2 = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-rel-002",
    )
    res2 = engine.evaluate(req2)
    assert res2.allowed
    assert res2.decision_status == PermissionState.APPROVED
    assert res2.reason_code == "GOV_ALLOWED"


def test_f07_source_revocation_overrides_all_lower_level_approvals(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """F-07: Source-wide revocation overrides approvals at every lower level."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_reg = RevocationRegistry()
    rev_reg.register(RevocationRecord(
        revocation_id="rev-src-001",
        scope=RevocationScope.SOURCE,
        target_identifier="uk.ons.ashe",
        reason_code="LEGAL_DISPUTE_HALT",
        description="Full legal freeze on all data from this publisher.",
        revoked_by="General Counsel",
        revoked_at=datetime.now(timezone.utc),
    ))

    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=rev_reg,
    )

    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="ashe-2025r-v1.0.2",
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_SOURCE"


def test_f07_model_scope_revocation(sample_source_identity: SourceIdentity):
    """F-07: Model-level revocation halts inference operations targeting that specific model."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rev_reg = RevocationRegistry()
    rev_reg.register(RevocationRecord(
        revocation_id="rev-mdl-001",
        scope=RevocationScope.MODEL,
        target_identifier="salary_usa_xgb_model",
        reason_code="BIAS_AUDIT_FAILURE",
        description="Adverse impact threshold exceeded in model audit.",
        revoked_by="Model Risk Officer",
        revoked_at=datetime.now(timezone.utc),
    ))

    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        revocation_registry=rev_reg,
    )

    lineage = ModelLineageRecord(
        model_id="salary_usa_xgb_model",
        market_id="US",
        algorithm_name="XGBoost",
        model_artifact_sha256="3D4468E2D79FA71804E1D02A7E15462D4A32BC6663E9733475225E9385C1E09B",
        preprocessor_artifact_sha256="F9D9B22C99757D8412F5868C65449A39A1C5FA2BA05BAEFE762D770281F998D8",
        training_data_source_id="us.jobintel.market-data",
        training_data_hash="AABBCCDDEEFF00112233445566778899AABBCCDDEEFF00112233445566778899",
        license_tier="Tier 1 (Internal Analytics)",
        trained_at=datetime.now(timezone.utc),
    )

    req = GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.INTERNAL_MODEL_INFERENCE,
        model_id="salary_usa_xgb_model",
        model_lineage=lineage,
    )
    res = engine.evaluate(req)
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_MODEL"


def test_f03_lifecycle_serving_state_matrix(
    sample_source_identity: SourceIdentity,
    sample_release: DatasetRelease,
    sample_approval: ApprovalRecord,
):
    """F-03: Serving operations require USE_APPROVED or PUBLISHED; DATA_ACQUIRED, DATA_VALIDATED, EXPIRED are blocked."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})

    # Test cases: (LifecycleState, expected_allowed, expected_status, expected_code)
    cases = [
        (LifecycleState.DATA_ACQUIRED, False, PermissionState.DENIED, "GOV_DENIED_LIFECYCLE_NOT_SERVABLE"),
        (LifecycleState.DATA_VALIDATED, False, PermissionState.DENIED, "GOV_DENIED_LIFECYCLE_NOT_SERVABLE"),
        (LifecycleState.SUSPENDED, False, PermissionState.DENIED, "GOV_DENIED_RELEASE_SUSPENDED"),
        (LifecycleState.REVOKED, False, PermissionState.REVOKED, "GOV_DENIED_RELEASE_REVOKED"),
        (LifecycleState.EXPIRED, False, PermissionState.EXPIRED, "GOV_DENIED_RELEASE_EXPIRED"),
        (LifecycleState.USE_APPROVED, True, PermissionState.APPROVED, "GOV_ALLOWED"),
        (LifecycleState.PUBLISHED, True, PermissionState.APPROVED, "GOV_ALLOWED"),
    ]

    for state, exp_allowed, exp_status, exp_code in cases:
        rel = sample_release.model_copy(update={"lifecycle_state": state})
        engine = GovernancePolicyEngine(
            sources=(approved_source,),
            releases=(rel,),
            approvals=(sample_approval,),
        )
        req = GovernanceEvaluationRequest(
            source_id="uk.ons.ashe",
            operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
            dataset_release_id="ashe-2025r-v1.0.2",
        )
        res = engine.evaluate(req)
        assert res.allowed == exp_allowed, f"Failed allowed check for state {state}"
        assert res.decision_status == exp_status, f"Failed status check for state {state}"
        assert res.reason_code == exp_code, f"Failed reason_code check for state {state}"


def test_f06_revocation_persistence_manifest_loading(tmp_path):
    """F-06: Manifest-based revocation loading validates schemas, handles missing and malformed files safely."""
    # 1. Valid manifest loading
    valid_manifest_path = tmp_path / "valid_revocations.json"
    valid_data = {
        "schema_version": "1.0.0",
        "description": "Test Revocation Config",
        "updated_at": "2026-11-13T12:00:00Z",
        "revocations": [
            {
                "revocation_id": "rev-file-001",
                "scope": "SOURCE",
                "target_identifier": "test.quarantined.source",
                "reason_code": "STATUTORY_CEASE_AND_DESIST",
                "description": "Cease and desist order served.",
                "revoked_by": "Compliance Lead",
                "revoked_at": "2026-11-13T12:00:00Z",
            }
        ],
    }
    valid_manifest_path.write_text(json.dumps(valid_data), encoding="utf-8")
    reg = RevocationRegistry.load_from_manifest_file(valid_manifest_path)
    assert len(reg) == 1
    match = reg.check_revocation("test.quarantined.source")
    assert match is not None
    assert match.reason_code == "STATUTORY_CEASE_AND_DESIST"

    # 2. Missing manifest file: falls back safely to empty registry
    missing_path = tmp_path / "does_not_exist.json"
    reg_missing = RevocationRegistry.load_from_manifest_file(missing_path)
    assert len(reg_missing) == 0

    # 3. Malformed JSON manifest: fails closed safely with empty registry
    malformed_path = tmp_path / "corrupted.json"
    malformed_path.write_text("{ NOT VALID JSON", encoding="utf-8")
    reg_malformed = RevocationRegistry.load_from_manifest_file(malformed_path)
    assert len(reg_malformed) == 0


def test_f05_training_entrypoint_governance_blocks():
    """F-05: Actual model training entry points halt immediately via TrainingGovernanceGate."""
    import src.india.modeling as india_mod
    import src.run_phase5_experiments as usa_mod

    # India training entrypoint execution is halted by Zero-Retraining quarantine
    with pytest.raises(PermissionError) as exc_ind:
        india_mod.run_all_experiments()
    assert "GOV_DENIED_ZERO_RETRAINING_RULE" in str(exc_ind.value)

    # USA training entrypoint execution is halted by lack of Tier 2 training authorization
    with pytest.raises(PermissionError) as exc_usa:
        usa_mod.main()
    assert "GOV_DENIED_TRAINING_UNAUTHORIZED" in str(exc_usa.value) or "GOV_DENIED_TIER2_LICENSE_REQUIRED" in str(exc_usa.value)


def test_f04_application_integration_service():
    """F-04: Controlled application integration layer evaluates UK fail-closed and records USA/India inference."""
    from src.backend.governance.service import (
        verify_uk_salary_governance,
        record_inference_governance,
        get_governance_engine,
    )
    from fastapi import HTTPException

    # 1. UK Salary fail-closed check
    with pytest.raises(HTTPException) as exc_uk:
        verify_uk_salary_governance()
    assert exc_uk.value.status_code == 503
    assert exc_uk.value.detail["code"] == "UK_DATA_NOT_PUBLISHED"

    # 2. Inference governance recording (research inference authorized under Tier 1)
    res_us = record_inference_governance("USA", "salary_usa_xgb_model")
    assert res_us.allowed
    assert res_us.reason_code == "GOV_ALLOWED_RESEARCH_INFERENCE"

    res_in = record_inference_governance("India", "salary_india_hgb_model")
    assert res_in.allowed
    assert res_in.reason_code == "GOV_ALLOWED_RESEARCH_INFERENCE"


# ===========================================================================
# SPRINT 2C.2.2 — TASK 1: Comprehensive Revocation Lifecycle Verification
# ===========================================================================

def test_task1_01_valid_manifest(tmp_path, sample_source_identity):
    """Task 1.1: Valid manifest loads cleanly and enforces revocation."""
    p = tmp_path / "valid_manifest.json"
    data = {
        "schema_version": "1.0.0",
        "description": "Valid Revocation Manifest",
        "updated_at": "2026-11-13T12:00:00Z",
        "revocations": [
            {
                "revocation_id": "rev-src-001",
                "scope": "SOURCE",
                "target_identifier": "uk.ons.ashe",
                "reason_code": "STATUTORY_CEASE_AND_DESIST",
                "description": "Cease and desist order.",
                "revoked_by": "Compliance Lead",
                "revoked_at": "2026-11-13T12:00:00Z",
            }
        ],
    }
    p.write_text(json.dumps(data), encoding="utf-8")
    reg = RevocationRegistry.load_from_manifest_file(p)
    assert reg.is_healthy
    assert reg.status == "HEALTHY"
    assert len(reg) == 1

    engine = GovernancePolicyEngine(sources=(sample_source_identity,), revocation_registry=reg)
    res = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
    ))
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_SOURCE"


def test_task1_02_missing_manifest(tmp_path, sample_source_identity):
    """Task 1.2: Missing manifest marks registry degraded and fails closed for governed operations, preserving internal inference."""
    missing = tmp_path / "non_existent.json"
    reg = RevocationRegistry.load_from_manifest_file(missing)
    assert not reg.is_healthy
    assert reg.status == "MISSING_MANIFEST"
    assert reg.load_error is not None
    assert len(reg) == 0

    engine = GovernancePolicyEngine(sources=(sample_source_identity,), revocation_registry=reg)

    # Governed operation FAILS CLOSED
    res_pub = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
    ))
    assert not res_pub.allowed
    assert res_pub.reason_code == "GOV_DENIED_REVOCATION_REGISTRY_UNAVAILABLE"
    assert "MISSING_MANIFEST" in res_pub.caveats[0]

    # Internal inference is preserved (does not fail closed on registry degradation)
    res_inf = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.INTERNAL_MODEL_INFERENCE,
        model_id="any-model",
    ))
    # It continues to subsequent gates (which handle source review/approval), not blocked by registry unavailability
    assert res_inf.reason_code != "GOV_DENIED_REVOCATION_REGISTRY_UNAVAILABLE"


def test_task1_03_malformed_json_manifest(tmp_path, sample_source_identity):
    """Task 1.3: Malformed JSON manifest marks registry degraded and fails closed for governed operations."""
    corrupted = tmp_path / "corrupted.json"
    corrupted.write_text("{ NOT VALID JSON ...", encoding="utf-8")
    reg = RevocationRegistry.load_from_manifest_file(corrupted)
    assert not reg.is_healthy
    assert reg.status == "MALFORMED_JSON"
    assert len(reg) == 0

    engine = GovernancePolicyEngine(sources=(sample_source_identity,), revocation_registry=reg)
    res = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
    ))
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_REVOCATION_REGISTRY_UNAVAILABLE"


def test_task1_04_unsupported_schema_version(tmp_path, sample_source_identity):
    """Task 1.4: Unsupported schema version marks registry degraded and fails closed."""
    invalid_ver = tmp_path / "future_schema.json"
    data = {
        "schema_version": "2.0.0",
        "description": "Future unsupported schema",
        "updated_at": "2026-11-13T12:00:00Z",
        "revocations": [],
    }
    invalid_ver.write_text(json.dumps(data), encoding="utf-8")
    reg = RevocationRegistry.load_from_manifest_file(invalid_ver)
    assert not reg.is_healthy
    assert reg.status == "UNSUPPORTED_SCHEMA"
    assert len(reg) == 0

    engine = GovernancePolicyEngine(sources=(sample_source_identity,), revocation_registry=reg)
    res = engine.evaluate(GovernanceEvaluationRequest(
        source_id="uk.ons.ashe",
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
    ))
    assert not res.allowed
    assert res.reason_code == "GOV_DENIED_REVOCATION_REGISTRY_UNAVAILABLE"


def test_task1_05_duplicate_revocation_ids():
    """Task 1.5: Duplicate revocation IDs update in-place without bloat or corruption."""
    reg = RevocationRegistry()
    rec1 = RevocationRecord(
        revocation_id="rev-dup-100",
        scope=RevocationScope.SOURCE,
        target_identifier="source.dup.test",
        reason_code="INITIAL_REASON",
        description="First registration",
        revoked_by="Auditor 1",
        revoked_at=datetime.now(timezone.utc),
    )
    rec2 = RevocationRecord(
        revocation_id="rev-dup-100",
        scope=RevocationScope.SOURCE,
        target_identifier="source.dup.test",
        reason_code="UPDATED_REASON",
        description="Second registration replaces first",
        revoked_by="Auditor 2",
        revoked_at=datetime.now(timezone.utc),
    )
    reg.register(rec1)
    assert len(reg) == 1
    assert reg.check_revocation("source.dup.test").reason_code == "INITIAL_REASON"

    reg.register(rec2)
    assert len(reg) == 1
    matched = reg.check_revocation("source.dup.test")
    assert matched is not None
    assert matched.reason_code == "UPDATED_REASON"
    assert matched.revoked_by == "Auditor 2"


def test_task1_06_expired_revocation():
    """Task 1.6: Expired revocations lapse, while active revocations enforce blocks."""
    from datetime import timedelta
    past_time = datetime.now(timezone.utc) - timedelta(days=10)
    future_time = datetime.now(timezone.utc) + timedelta(days=10)

    # 1. Expired revocation (temporary embargo that elapsed)
    rec_expired = RevocationRecord(
        revocation_id="rev-exp-01",
        scope=RevocationScope.SOURCE,
        target_identifier="source.expired.embargo",
        reason_code="TEMPORARY_COURT_EMBARGO",
        description="Embargo until past date",
        revoked_by="Compliance",
        revoked_at=past_time - timedelta(days=30),
        expires_at=past_time,
    )
    reg_exp = RevocationRegistry((rec_expired,))
    assert reg_exp.check_revocation("source.expired.embargo") is None

    # 2. Active revocation with future expiration
    rec_active = RevocationRecord(
        revocation_id="rev-act-01",
        scope=RevocationScope.SOURCE,
        target_identifier="source.active.embargo",
        reason_code="ACTIVE_COURT_EMBARGO",
        description="Embargo until future date",
        revoked_by="Compliance",
        revoked_at=past_time,
        expires_at=future_time,
    )
    reg_act = RevocationRegistry((rec_active,))
    match = reg_act.check_revocation("source.active.embargo")
    assert match is not None
    assert match.reason_code == "ACTIVE_COURT_EMBARGO"


def test_task1_07_source_level_revocation(sample_source_identity):
    """Task 1.7: Source-level revocation cascades to all child releases and models."""
    rec = RevocationRecord(
        revocation_id="rev-src-999",
        scope=RevocationScope.SOURCE,
        target_identifier=sample_source_identity.source_id,
        reason_code="TOTAL_SOURCE_REVOCATION",
        description="Source fully revoked",
        revoked_by="Legal Counsel",
        revoked_at=datetime.now(timezone.utc),
    )
    reg = RevocationRegistry((rec,))
    engine = GovernancePolicyEngine(sources=(sample_source_identity,), revocation_registry=reg)

    res = engine.evaluate(GovernanceEvaluationRequest(
        source_id=sample_source_identity.source_id,
        operation=GovernanceOperation.PUBLIC_AGGREGATE_DISPLAY,
        dataset_release_id="any-child-release",
        model_id="any-child-model",
    ))
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_REVOKED_SOURCE"


def test_task1_08_dataset_level_revocation(sample_source_identity):
    """Task 1.8: Dataset-level revocation blocks child releases while leaving sibling datasets alone."""
    rec = RevocationRecord(
        revocation_id="rev-ds-001",
        scope=RevocationScope.DATASET,
        target_identifier="ds.ashe.table1",
        reason_code="TABLE1_PII_DISCOVERED",
        description="PII leak in table 1",
        revoked_by="DPO",
        revoked_at=datetime.now(timezone.utc),
    )
    reg = RevocationRegistry((rec,))
    reg.bind_hierarchy(release_id="rel-t1-v1", dataset_id="ds.ashe.table1", source_id=sample_source_identity.source_id)
    reg.bind_hierarchy(release_id="rel-t2-v1", dataset_id="ds.ashe.table2", source_id=sample_source_identity.source_id)

    # Table 1 release is revoked
    assert reg.check_revocation(sample_source_identity.source_id, dataset_release_id="rel-t1-v1") is not None
    # Table 2 release is unaffected
    assert reg.check_revocation(sample_source_identity.source_id, dataset_release_id="rel-t2-v1") is None


def test_task1_09_approval_level_revocation(sample_source_identity, sample_release, sample_approval):
    """Task 1.9: Approval-level revocation invalidates only the specific targeted approval."""
    approved_source = sample_source_identity.model_copy(update={"default_permission_state": PermissionState.APPROVED})
    rec = RevocationRecord(
        revocation_id="rev-appr-001",
        scope=RevocationScope.APPROVAL,
        target_identifier=sample_approval.approval_id,
        reason_code="APPROVAL_SUPERSEDED",
        description="Approval revoked due to policy update",
        revoked_by="Governance Lead",
        revoked_at=datetime.now(timezone.utc),
    )
    reg = RevocationRegistry((rec,))

    engine = GovernancePolicyEngine(
        sources=(approved_source,),
        releases=(sample_release,),
        approvals=(sample_approval,),
        revocation_registry=reg,
    )
    res = engine.evaluate(GovernanceEvaluationRequest(
        source_id=approved_source.source_id,
        dataset_release_id=sample_release.release_id,
        operation=sample_approval.intended_operation,
    ))
    assert not res.allowed
    assert res.decision_status == PermissionState.REVOKED
    assert res.reason_code == "GOV_DENIED_APPROVAL_REVOKED"


def test_task1_10_manifest_rollback(tmp_path, sample_source_identity):
    """Task 1.10: Reverting to an earlier manifest cleanly rolls back revocation state."""
    manifest_file = tmp_path / "revocation_manifest.json"

    # Step A: Version with an active revocation
    manifest_v1 = {
        "schema_version": "1.0.0",
        "description": "V1 with revocation",
        "updated_at": "2026-11-13T12:00:00Z",
        "revocations": [
            {
                "revocation_id": "rev-rollback-1",
                "scope": "SOURCE",
                "target_identifier": "uk.ons.ashe",
                "reason_code": "TEMPORARY_BLOCK",
                "description": "Block in v1",
                "revoked_by": "Compliance",
                "revoked_at": "2026-11-13T12:00:00Z",
            }
        ],
    }
    manifest_file.write_text(json.dumps(manifest_v1), encoding="utf-8")
    reg_v1 = RevocationRegistry.load_from_manifest_file(manifest_file)
    assert reg_v1.check_revocation("uk.ons.ashe") is not None

    # Step B: Roll back file to V0 (empty revocations)
    manifest_v0 = {
        "schema_version": "1.0.0",
        "description": "V0 clean state",
        "updated_at": "2026-11-13T10:00:00Z",
        "revocations": [],
    }
    manifest_file.write_text(json.dumps(manifest_v0), encoding="utf-8")
    reg_v0 = RevocationRegistry.load_from_manifest_file(manifest_file)
    assert reg_v0.check_revocation("uk.ons.ashe") is None
    assert len(reg_v0) == 0


