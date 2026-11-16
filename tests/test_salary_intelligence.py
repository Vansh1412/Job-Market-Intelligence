"""
Test Suite for Cross-Market Salary Intelligence (Sprint 3B.1).

Validates source metadata, FX and World Bank ICP 2024 PPP rates,
observation completeness across all 28 national occupations,
strict FX vs PPP separation, automated comparability evaluations,
and fail-closed UK ASHE governance enforcement.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.schemas.salary import ComparabilityVerdict
from src.backend.services.salary_service import get_salary_service

client = TestClient(app)


def test_salary_sources_endpoint():
    """Verify official sources list and required metadata fields."""
    res = client.get("/v1/salary/sources")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) == 5

    source_ids = {s["source_id"] for s in sources}
    expected_ids = {
        "US_BLS_OEWS_2023",
        "UK_ONS_ASHE_2024",
        "AU_ABS_EEH_2023",
        "SG_MOM_OWS_2023",
        "IN_JOBINTEL_BENCHMARK_2024",
    }
    assert source_ids == expected_ids

    for s in sources:
        assert s["authority"]
        assert s["publication_name"]
        assert s["license"]
        assert s["pay_concept"]
        assert s["frequency"] == "ANNUAL"
        assert s["source_url"].startswith("http")


def test_salary_source_by_id():
    """Verify single source lookup and 404 for unknown source."""
    res = client.get("/v1/salary/sources/US_BLS_OEWS_2023")
    assert res.status_code == 200
    assert res.json()["market_id"] == "US"

    res_missing = client.get("/v1/salary/sources/NON_EXISTENT_SOURCE")
    assert res_missing.status_code == 404


def test_salary_rates_endpoint_and_strict_separation():
    """Verify FX rates, PPP factors, and the strict separation warning invariant."""
    res = client.get("/v1/salary/rates")
    assert res.status_code == 200
    data = res.json()
    assert data["base_currency"] == "USD"
    assert data["reference_year"] == "2024"
    assert "CRITICAL METHODOLOGICAL INVARIANT" in data["methodology"]["separation_warning"]

    rates = data["rates"]
    assert "USD" in rates
    assert "GBP" in rates
    assert "AUD" in rates
    assert "SGD" in rates
    assert "INR" in rates

    # INR: Nominal FX is 83.5, while PPP factor is 23.8 (differs by > 3x)
    inr = rates["INR"]
    assert inr["nominal_fx_to_usd"] == 83.5
    assert inr["ppp_conversion_factor_to_usd"] == 23.8
    assert inr["nominal_fx_to_usd"] > inr["ppp_conversion_factor_to_usd"] * 3.0


def test_salary_convert_endpoint():
    """Verify dual currency conversion for nominal USD and PPP USD."""
    # Convert 1,200,000 INR (12 LPA)
    res = client.get("/v1/salary/convert?amount=1200000&from_currency=INR")
    assert res.status_code == 200
    data = res.json()
    assert data["original_currency"] == "INR"
    assert data["original_amount"] == 1200000.0
    # Nominal USD = 1200000 / 83.5 = ~14371.20
    assert 14300.0 < data["nominal_usd"] < 14450.0
    # PPP USD = 1200000 / 23.8 = ~50420.17
    assert 50000.0 < data["ppp_usd"] < 51000.0
    assert data["ppp_usd"] > data["nominal_usd"] * 3.0

    # Test invalid currency
    res_err = client.get("/v1/salary/convert?amount=1000&from_currency=XYZ")
    assert res_err.status_code == 400


def test_salary_observations_all_28_national_occupations():
    """Verify that all 28 national occupations have salary observations."""
    res = client.get("/v1/salary/observations")
    assert res.status_code == 200
    obs = res.json()
    assert len(obs) == 28

    markets = {o["market_id"] for o in obs}
    assert markets == {"US", "UK", "AU", "SG", "IN"}

    # Verify distribution per market
    market_counts = {}
    for o in obs:
        m = o["market_id"]
        market_counts[m] = market_counts.get(m, 0) + 1

    assert market_counts["US"] == 7
    assert market_counts["UK"] == 8
    assert market_counts["AU"] == 4
    assert market_counts["SG"] == 6
    assert market_counts["IN"] == 3


def test_salary_observations_market_filter():
    """Verify market filtering on observations endpoint."""
    res_us = client.get("/v1/salary/observations?market_id=US")
    assert res_us.status_code == 200
    assert len(res_us.json()) == 7

    res_au = client.get("/v1/salary/observations?market_id=AU")
    assert res_au.status_code == 200
    assert len(res_au.json()) == 4


def test_occupation_salary_profile_us():
    """Verify detailed salary profile for US Software Developers."""
    res = client.get("/v1/salary/occupations/US_SOC_2018:15-1252")
    assert res.status_code == 200
    data = res.json()
    assert data["occupation_id"] == "US_SOC_2018:15-1252"
    assert data["currency"] == "USD"
    pcts = data["percentiles"]
    assert pcts["p10"] == 77020.0
    assert pcts["p25"] == 101370.0
    assert pcts["p50"] == 132270.0
    assert pcts["p75"] == 168050.0
    assert pcts["p90"] == 208620.0
    assert data["nominal_usd_median"] == 132270.0
    assert data["ppp_usd_median"] == 132270.0


def test_occupation_salary_profile_uk_fail_closed():
    """Verify UK salary observation fails closed with HTTP 503 under active governance gate."""
    res = client.get("/v1/salary/occupations/UK_SOC_2020:2134")
    assert res.status_code == 503
    data = res.json()
    assert data["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"


def test_occupation_salary_profile_not_found():
    """Verify 404 for unknown occupation ID."""
    res = client.get("/v1/salary/occupations/NON_EXISTENT_OCC_9999")
    assert res.status_code == 404


def test_cross_market_comparison_us_software_developer():
    """Verify cross-market comparison results for US Software Developer."""
    res = client.get("/v1/salary/compare?occupation_id=US_SOC_2018:15-1252")
    assert res.status_code == 200
    data = res.json()

    assert data["source_occupation_id"] == "US_SOC_2018:15-1252"
    assert data["source_market_id"] == "US"
    assert data["source_currency"] == "USD"
    assert data["source_median_original"] == 132270.0

    comparisons = data["comparisons"]
    assert len(comparisons) == 4

    comp_markets = {c["market_id"] for c in comparisons}
    assert comp_markets == {"UK", "AU", "SG", "IN"}

    # UK must be gracefully withheld with INSUFFICIENT_DATA
    uk_comp = next(c for c in comparisons if c["market_id"] == "UK")
    assert uk_comp["is_suppressed"] is True
    assert uk_comp["comparability_verdict"] == ComparabilityVerdict.INSUFFICIENT_DATA
    assert uk_comp["original_median"] is None
    assert any("withheld by governance policy gate" in cav for cav in uk_comp["comparability_caveats"])

    # Singapore comparison
    sg_comp = next(c for c in comparisons if c["market_id"] == "SG")
    assert sg_comp["original_currency"] == "SGD"
    assert sg_comp["original_median"] == 97500.0
    assert sg_comp["nominal_usd_median"] == 72490.66
    assert sg_comp["ppp_usd_median"] == 116071.41
    assert sg_comp["comparability_verdict"] == ComparabilityVerdict.COMPARABLE_WITH_ADJUSTMENTS

    # India comparison
    in_comp = next(c for c in comparisons if c["market_id"] == "IN")
    assert in_comp["original_currency"] == "INR"
    assert in_comp["original_median"] == 1200000.0
    assert in_comp["nominal_usd_median"] == 14371.20
    assert in_comp["ppp_usd_median"] == 50420.40
    assert in_comp["comparability_verdict"] == ComparabilityVerdict.COMPARABLE_WITH_MAJOR_CAVEATS
    assert any("Pay Concept Disparity: India uses Cost to Company (CTC)" in cav for cav in in_comp["comparability_caveats"])
    assert any("Methodological Divergence" in cav for cav in in_comp["comparability_caveats"])


def test_cross_market_comparison_uk_source_fail_closed():
    """Verify that requesting cross-market comparison with UK as source fails closed with HTTP 503."""
    res = client.get("/v1/salary/compare?occupation_id=UK_SOC_2020:2134")
    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"


def test_cross_market_comparison_missing_occupation():
    """Verify 404 for unknown source occupation ID."""
    res = client.get("/v1/salary/compare?occupation_id=NON_EXISTENT_OCC")
    assert res.status_code == 404


def test_comparability_dimensions_completeness():
    """Verify that all 11 comparability dimensions are declared in comparison results."""
    res = client.get("/v1/salary/compare?occupation_id=US_SOC_2018:15-1252")
    assert res.status_code == 200
    dims = res.json()["comparability_dimensions"]
    assert len(dims) == 11
    expected_dims = {
        "CURRENCY_MISMATCH",
        "PAY_PERIOD_FREQUENCY",
        "PAY_CONCEPT_DEFINITION",
        "SURVEY_POPULATION",
        "OVERTIME_AND_BONUS_TREATMENT",
        "GEOGRAPHIC_COVERAGE",
        "REFERENCE_YEAR_ALIGNMENT",
        "CLASSIFICATION_GRANULARITY",
        "PERCENTILE_AVAILABILITY",
        "SOURCE_METHODOLOGY_TYPE",
        "STATISTICAL_SUPPRESSION_AND_RSE",
    }
    assert set(dims) == expected_dims


def test_legacy_salary_endpoints_remain_operational():
    """Verify that existing legacy endpoints are completely unaffected."""
    res_summary = client.get("/api/salary/summary")
    assert res_summary.status_code == 200

    res_role = client.get("/api/salary/by-role")
    assert res_role.status_code == 200

    res_comp = client.get("/api/salary/comparator")
    assert res_comp.status_code == 200
