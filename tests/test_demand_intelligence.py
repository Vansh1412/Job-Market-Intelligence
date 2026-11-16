"""Automated test suite for Job Demand Intelligence (Sprint 3B.2).

Verifies:
- Metric schema definitions and underlying constructs
- Source provenance and legal licenses
- 28 atomic demand observations across US, AU, UK, SG, IN
- Detailed occupation profiles and regional distributions
- Time-series trend calculations and piecewise thresholds
- 11-dimension cross-market comparability engine
- Skill gap analysis algorithm and actionable recommendations
- REST API contracts under both /v1/demand and /api/v1/demand
"""

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.schemas.demand import (
    DemandComparabilityVerdict,
    DemandMetricType,
    DemandObservation,
    DemandTrendDirection,
    ShortageStatus,
    SkillGapAnalysisRequest,
)
from src.backend.schemas.market import MarketId
from src.backend.services.demand_service import DemandService, get_demand_service

client = TestClient(app)


@pytest.fixture
def demand_service() -> DemandService:
    return get_demand_service()


# 1. CATALOG TESTS
def test_demand_metrics_catalog(demand_service: DemandService):
    metrics = demand_service.get_metrics()
    assert len(metrics) == 7
    metric_types = {m.metric_type for m in metrics}
    assert DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS in metric_types
    assert DemandMetricType.ANNUAL_JOB_OPENINGS in metric_types
    assert DemandMetricType.OBSERVED_VACANCIES in metric_types
    assert DemandMetricType.SHORTAGE_INDICATOR in metric_types

    # Verify every metric has limitations and construct
    for m in metrics:
        assert len(m.limitations) > 0
        assert len(m.underlying_construct) > 10


def test_demand_sources_catalog(demand_service: DemandService):
    sources = demand_service.get_sources()
    assert len(sources) == 10
    source_ids = {s["source_id"] for s in sources}
    assert "us.bls.ep" in source_ids
    assert "au.jsa.ivi" in source_ids
    assert "uk.ons.labour-demand" in source_ids
    assert "sg.mom.vacancies" in source_ids
    assert "in.jobintel.tech-demand" in source_ids

    # Verify licenses are present
    for s in sources:
        assert "license" in s
        assert len(s["license"]) > 3


def test_demand_markets_overview(demand_service: DemandService):
    markets = demand_service.get_markets_overview()
    assert len(markets) == 5
    m_ids = {m["market_id"] for m in markets}
    assert m_ids == {"US", "AU", "UK", "SG", "IN"}
    for m in markets:
        assert m["total_observations"] > 0
        if m["market_id"] == "UK":
            assert m["coverage_status"] == "WITHHELD_PENDING_REVIEW"
            assert m["publication_status"] == "REVIEW_REQUIRED"
        else:
            assert m["coverage_status"] == "AVAILABLE"
            assert m["publication_status"] == "PUBLISHED"


# 2. OBSERVATIONS AND PROFILES
def test_demand_observations_count_and_integrity(demand_service: DemandService):
    obs = demand_service.list_observations()
    assert len(obs) == 28

    # Check distribution across markets
    by_market = {m: len(demand_service.list_observations(market_id=m)) for m in MarketId}
    assert by_market[MarketId.US] == 7
    assert by_market[MarketId.AU] == 4
    assert by_market[MarketId.UK] == 8
    assert by_market[MarketId.SG] == 6
    assert by_market[MarketId.IN] == 3


def test_us_software_developer_profile(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile(MarketId.US, "15-1252")
    assert profile is not None
    assert profile.occupation_title == "Software Developers"
    assert profile.primary_metric_type == DemandMetricType.ANNUAL_JOB_OPENINGS
    assert profile.primary_metric_value == 140100.0
    assert profile.primary_metric_unit == "Annual Openings"
    assert len(profile.regional_distribution) >= 5
    assert profile.regional_distribution[0].region_code == "CA"
    assert profile.regional_distribution[0].share_percentage == 21.0
    assert len(profile.top_skills) > 5
    assert any(s.skill_name == "Python" for s in profile.top_skills)


def test_au_software_engineer_profile(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile(MarketId.AU, "261313")
    assert profile is not None
    assert profile.occupation_title == "Software Engineer"
    assert profile.primary_metric_type == DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS
    assert profile.primary_metric_value == 4820.0
    assert profile.shortage_status == ShortageStatus.NATIONAL_SHORTAGE
    assert profile.future_demand_rating == "Strong"
    assert len(profile.regional_distribution) >= 5
    assert profile.regional_distribution[0].region_code == "NSW"


def test_uk_programmer_profile(demand_service: DemandService):
    # Public view: publication gate active, value withheld as null to prevent leak and conflation with zero
    profile = demand_service.get_occupation_demand_profile(MarketId.UK, "2134", public_view=True)
    assert profile is not None
    assert profile.occupation_title == "Programmers and software development professionals"
    assert profile.primary_metric_type == DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS
    assert profile.publication_gate_active is True
    assert profile.publication_gate_code == "UK_DEMAND_DATA_NOT_PUBLISHED"
    assert profile.primary_metric_value is None
    assert profile.primary_metric_value != 0.0
    assert len(profile.trend_time_series) == 0
    assert len(profile.regional_distribution) == 0
    assert profile.shortage_status == ShortageStatus.NATIONAL_SHORTAGE
    assert any("withheld" in d.lower() for d in profile.methodology_disclaimers)

    # Internal research view: allows internal verification of source baseline
    prof_internal = demand_service.get_occupation_demand_profile(MarketId.UK, "2134", public_view=False)
    assert prof_internal is not None
    assert prof_internal.primary_metric_value == 112.5


def test_sg_software_developer_profile(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile(MarketId.SG, "25121")
    assert profile is not None
    assert profile.occupation_title == "Software Developer"
    assert profile.primary_metric_type == DemandMetricType.OBSERVED_VACANCIES
    assert profile.primary_metric_value == 3420.0
    assert profile.unfilled_rate_over_6_months == 32.4
    assert profile.shortage_status == ShortageStatus.NATIONAL_SHORTAGE


def test_in_software_developer_profile(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile(MarketId.IN, "2512.0100")
    assert profile is not None
    assert profile.occupation_title == "Software Developer"
    assert profile.primary_metric_type == DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS
    assert profile.primary_metric_value == 24500.0
    assert profile.shortage_status == ShortageStatus.REGIONAL_SHORTAGE
    assert any("calibrated sample benchmark" in d.lower() for d in profile.methodology_disclaimers)


# 3. TREND CALCULATION TESTS
def test_trend_calculation_strong_growth(demand_service: DemandService):
    # US Data Scientist has 14200 -> 20800 (+46.5%)
    profile = demand_service.get_occupation_demand_profile(MarketId.US, "15-2051")
    assert profile is not None
    assert profile.trend_direction == DemandTrendDirection.STRONG_GROWTH
    assert profile.trend_percentage_change is not None
    assert profile.trend_percentage_change > 10.0


def test_trend_calculation_moderate_growth(demand_service: DemandService):
    # AU Software Engineer: 4600 -> 4820 (+4.8%)
    profile = demand_service.get_occupation_demand_profile(MarketId.AU, "261313")
    assert profile is not None
    assert profile.trend_direction == DemandTrendDirection.MODERATE_GROWTH
    assert profile.trend_percentage_change == 4.8


def test_trend_calculation_decline(demand_service: DemandService):
    # UK IT Quality & Testing internal baseline: 100.0 -> 96.2 (-3.8%)
    profile = demand_service.get_occupation_demand_profile(MarketId.UK, "2136", public_view=False)
    assert profile is not None
    assert profile.trend_direction == DemandTrendDirection.MODERATE_DECLINE
    assert profile.trend_percentage_change == -3.8


# 4. 11-DIMENSION COMPARABILITY ENGINE
def test_cross_market_comparability_us_vs_au_software_engineer(demand_service: DemandService):
    res = demand_service.compare_demand(
        canonical_id="CAN_OCC_SOFTWARE_ENGINEER",
        market_a=MarketId.US,
        market_b=MarketId.AU,
    )
    assert res.canonical_id == "CAN_OCC_SOFTWARE_ENGINEER"
    assert res.market_a == MarketId.US
    assert res.market_b == MarketId.AU
    assert len(res.dimension_evaluations) == 11
    # US is ANNUAL_JOB_OPENINGS, AU is OBSERVED_JOB_ADVERTISEMENTS
    assert res.verdict == DemandComparabilityVerdict.METHODOLOGICALLY_DISTINCT
    assert len(res.warnings) > 0
    # Confirm dimensions 1, 3, 4, 9, 11 are critical mismatches
    dim_map = {d.dimension.split(".")[0]: d for d in res.dimension_evaluations}
    assert dim_map["1"].match is False
    assert dim_map["1"].severity == "CRITICAL"


def test_cross_market_comparability_au_vs_uk(demand_service: DemandService):
    res = demand_service.compare_demand(
        canonical_id="CAN_OCC_SOFTWARE_ENGINEER",
        market_a=MarketId.AU,
        market_b=MarketId.UK,
    )
    assert len(res.dimension_evaluations) == 11
    # Both are OBSERVED_JOB_ADVERTISEMENTS, but AU is raw count, UK is index base 100
    dim_map = {d.dimension.split(".")[0]: d for d in res.dimension_evaluations}
    assert dim_map["1"].match is True  # Both OBSERVED_JOB_ADVERTISEMENTS


def test_cross_market_comparability_missing_concept(demand_service: DemandService):
    res = demand_service.compare_demand(
        canonical_id="CAN_OCC_NONEXISTENT",
        market_a=MarketId.US,
        market_b=MarketId.UK,
    )
    assert res.verdict == DemandComparabilityVerdict.INSUFFICIENT_DATA


# 5. SKILL GAP ANALYSIS
def test_skill_gap_analysis_high_match(demand_service: DemandService):
    req = SkillGapAnalysisRequest(
        target_occupation_id="15-1252",
        market_id=MarketId.US,
        user_skills=["Python", "Java", "Docker", "AWS", "SQL", "Git", "REST APIs", "System Design", "TypeScript", "Kubernetes"],
    )
    res = demand_service.analyze_skill_gaps(req)
    assert res.match_percentage >= 70.0
    assert len(res.matched_skills) >= 6
    assert res.readiness_level in ("HIGH", "MODERATE")
    assert len(res.recommendations) >= 2


def test_skill_gap_analysis_low_match(demand_service: DemandService):
    req = SkillGapAnalysisRequest(
        target_occupation_id="15-1252",
        market_id=MarketId.US,
        user_skills=["HTML", "CSS"],
    )
    res = demand_service.analyze_skill_gaps(req)
    assert res.match_percentage < 30.0
    assert len(res.missing_critical_skills) > 0
    assert res.readiness_level in ("EMERGING", "FOUNDATIONAL")
    assert any("Immediate Priority" in r for r in res.recommendations)


# 6. API ENDPOINTS INTEGRATION
def test_api_demand_markets():
    resp = client.get("/v1/demand/markets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5

    # Test /api prefix parity
    resp_api = client.get("/api/v1/demand/markets")
    assert resp_api.status_code == 200
    assert resp_api.json() == data


def test_api_demand_metrics():
    resp = client.get("/v1/demand/metrics")
    assert resp.status_code == 200
    assert len(resp.json()) == 7


def test_api_demand_occupations():
    resp = client.get("/v1/demand/occupations?market=US")
    assert resp.status_code == 200
    assert len(resp.json()) == 7


def test_api_demand_occupation_detail():
    resp = client.get("/v1/demand/occupations/15-1252?market=US")
    assert resp.status_code == 200
    data = resp.json()
    assert data["occupation_title"] == "Software Developers"
    assert data["primary_metric_value"] == 140100.0


def test_api_demand_trends():
    resp = client.get("/v1/demand/occupations/15-1252/trends?market=US")
    assert resp.status_code == 200
    data = resp.json()
    assert "time_series" in data
    assert len(data["time_series"]) == 5


def test_api_demand_regions():
    resp = client.get("/v1/demand/occupations/15-1252/regions?market=US")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5


def test_api_demand_skills():
    resp = client.get("/v1/demand/occupations/15-1252/skills?market=US")
    assert resp.status_code == 200
    assert len(resp.json()) > 5


def test_api_demand_compare():
    resp = client.get("/v1/demand/compare?canonical_id=CAN_OCC_SOFTWARE_ENGINEER&market_a=US&market_b=AU")
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "METHODOLOGICALLY_DISTINCT"
    assert len(data["dimension_evaluations"]) == 11


def test_api_demand_skill_gaps():
    payload = {
        "target_occupation_id": "15-1252",
        "market_id": "US",
        "user_skills": ["Python", "Docker", "AWS"],
    }
    resp = client.post("/v1/demand/skills/gaps", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "match_percentage" in data
    assert "missing_critical_skills" in data
    assert len(data["recommendations"]) > 0


def test_uk_salary_governance_remains_unbroken():
    """Verify that adding demand intelligence endpoints does NOT break UK salary 503 fail-closed gate."""
    resp = client.get("/api/v1/markets/UK/salary/occupations")
    assert resp.status_code == 503
    data = resp.json()
    assert data["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"

    # Also check /v1/salary/occupations/UK_SOC_2020:2134
    res2 = client.get("/v1/salary/occupations/UK_SOC_2020:2134")
    assert res2.status_code == 503
    assert res2.json()["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"


# 7. SPRINT 3B.2.2 DISCLOSURE HARDENING & LICENSING GATE TESTS
def test_provenance_labels_and_mapping(demand_service: DemandService):
    from src.backend.schemas.demand import DemandProvenance, PROVENANCE_METADATA

    for prov in DemandProvenance:
        assert prov in PROVENANCE_METADATA
        meta = PROVENANCE_METADATA[prov]
        assert "label" in meta and len(meta["label"]) > 0
        assert "description" in meta and len(meta["description"]) > 10

    # Test US observation has OFFICIALLY_DERIVED
    us_obs = demand_service.list_observations(market_id="US", public_view=False)[0]
    assert us_obs.provenance == DemandProvenance.OFFICIALLY_DERIVED
    assert us_obs.provenance_label == "Derived from official data"

    # Test India observation has JOBINTEL_CURATED
    in_obs = demand_service.list_observations(market_id="IN", public_view=False)[0]
    assert in_obs.provenance == DemandProvenance.JOBINTEL_CURATED
    assert in_obs.provenance_label == "JobIntel research benchmark"


def test_us_regional_allocation_disclosure(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile("US", "15-1252")
    assert profile is not None
    assert profile.regional_disclosure is not None
    assert "derived allocations using employment weights" in profile.regional_disclosure
    assert "not independently observed" in profile.regional_disclosure


def test_au_occupation_inheritance_disclosure(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile("AU", "261313")
    assert profile is not None
    assert profile.occupation_inheritance_disclosure is not None
    assert "broader four-digit ANZSCO" in profile.occupation_inheritance_disclosure


def test_sg_modelled_regional_warning(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile("SG", "25121")
    assert profile is not None
    assert profile.regional_disclosure is not None
    assert "MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED" in profile.regional_disclosure


def test_india_calibrated_benchmark_disclosure(demand_service: DemandService):
    profile = demand_service.get_occupation_demand_profile("IN", "2512.0100")
    assert profile is not None
    assert profile.benchmark_disclosure is not None
    assert "not an official MoSPI national vacancy census" in profile.benchmark_disclosure
    assert profile.provenance == "JOBINTEL_CURATED"
    assert profile.provenance_label == "JobIntel research benchmark"


def test_skill_gap_mathematical_formula_transparency(demand_service: DemandService):
    from src.backend.schemas.demand import SkillGapAnalysisRequest

    res = demand_service.analyze_skill_gaps(
        SkillGapAnalysisRequest(
            target_occupation_id="15-1252",
            market_id=MarketId.US,
            user_skills=["Python", "SQL", "Git", "Docker"],
        )
    )
    assert res.matched_skill_weight > 0.0
    assert res.total_required_weight >= res.matched_skill_weight
    assert "Skill Coverage (%)" in res.formula_explanation
    assert "not an employability probability" in res.methodology_notes
    assert any("rule-based" in r for r in res.recommendations)


def test_uk_data_leak_prevention_on_api():
    # Verify API list endpoint sanitizes UK records: value must be null (not 0.0)
    resp = client.get("/v1/demand/occupations?market=UK")
    assert resp.status_code == 200
    records = resp.json()
    assert len(records) == 8
    for r in records:
        assert r["value"] is None
        assert r["value"] != 0.0
        assert len(r["time_series"]) == 0
        assert len(r["regional_breakdown"]) == 0
        assert "UK_DEMAND_DATA_NOT_PUBLISHED" in r["notes"]

    # Verify detail endpoint enforces publication gate: value must be null
    detail = client.get("/v1/demand/occupations/2134?market=UK").json()
    assert detail["publication_gate_active"] is True
    assert detail["publication_gate_code"] == "UK_DEMAND_DATA_NOT_PUBLISHED"
    assert detail["primary_metric_value"] is None
    assert detail["primary_metric_value"] != 0.0
    assert len(detail["trend_time_series"]) == 0
    assert len(detail["regional_distribution"]) == 0


# 8. SPRINT 3B.2.3.1 SEMANTIC WITHHELD RECONCILIATION TESTS
def test_withheld_metric_serializes_as_null_in_json():
    """Verify serialized JSON contains explicit null for primary_metric_value, not 0.0."""
    resp = client.get("/v1/demand/occupations/2134?market=UK")
    assert resp.status_code == 200
    # Check raw text to verify exact null token in JSON
    raw_text = resp.text
    assert '"primary_metric_value":null' in raw_text or '"primary_metric_value": null' in raw_text
    data = resp.json()
    assert data["primary_metric_value"] is None
    assert data["publication_gate_active"] is True
    assert data["publication_gate_code"] == "UK_DEMAND_DATA_NOT_PUBLISHED"


def test_withheld_pending_review_distinction_from_measured_zero(demand_service: DemandService):
    """Proves WITHHELD_PENDING_REVIEW != 0 and MEASURED_ZERO == 0."""
    gated_prof = demand_service.get_occupation_demand_profile(MarketId.UK, "2134", public_view=True)
    assert gated_prof.primary_metric_value is None
    assert gated_prof.primary_metric_value != 0.0

    # Test genuine measured zero preservation on DemandObservation schema
    zero_obs = DemandObservation(
        observation_id="dmd-test-zero",
        market_id=MarketId.US,
        occupation_id="15-9999",
        source_id="us.bls.ep",
        metric_type=DemandMetricType.ANNUAL_JOB_OPENINGS,
        metric_unit="Annual Openings",
        value=0.0,
        reference_period="2024",
    )
    assert zero_obs.value == 0.0
    assert zero_obs.value is not None
    assert zero_obs.value != gated_prof.primary_metric_value


def test_compare_endpoint_sanitizes_withheld_values_to_null():
    """Verify cross-market comparison serializes metric_b.value as null when UK is gated."""
    resp = client.get("/v1/demand/compare?canonical_id=CAN_OCC_SOFTWARE_ENGINEER&market_a=US&market_b=UK")
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "METHODOLOGICALLY_DISTINCT"
    # metric_a (US) should have actual volume
    assert data["metric_a"]["value"] is not None
    assert data["metric_a"]["value"] > 0
    # metric_b (UK) must be null, NOT 0.0
    assert data["metric_b"]["value"] is None
    assert data["metric_b"]["publication_gate_active"] is True
    assert any("withheld" in w.lower() for w in data["warnings"])


def test_uk_qualitative_shortage_independence(demand_service: DemandService):
    """Verify that UK shortage status remains available via independent uk.gov.shortage source."""
    prof = demand_service.get_occupation_demand_profile(MarketId.UK, "2134", public_view=True)
    assert prof.shortage_status == ShortageStatus.NATIONAL_SHORTAGE
    sources = demand_service.get_sources()
    shortage_src = next((s for s in sources if s["source_id"] == "uk.gov.shortage"), None)
    assert shortage_src is not None
    assert shortage_src["publication_status"] == "PUBLISHED"
    assert "Open Government Licence" in shortage_src["license"]

