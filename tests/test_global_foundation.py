from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.backend.data_catalog.registry import SourceRegistry, get_source, get_sources
from src.backend.data_catalog.validation import validate_data_provenance, validate_salary_observations
from src.backend.employers.registry import EmployerRegistry, get_employers
from src.backend.main import app
from src.backend.markets.registry import MarketRegistry, get_market, get_markets
from src.backend.schemas.data import DataProvenance, ReuseReviewStatus, ValidationStatus
from src.backend.schemas.employer import (
    EmployerCategory,
    EmployerLocation,
    EmployerLocationType,
    EmployerProfile,
    EmployerSourceReference,
    EmployerVerificationStatus,
)
from src.backend.schemas.market import CapabilityStatus, CurrencyCode, MarketCapability, MarketId
from src.backend.schemas.salary import SalaryObservation, SalaryPeriod
from src.backend.routers.v1 import (
    list_employers,
    list_markets,
    list_sources,
    retrieve_employer,
    retrieve_market,
    retrieve_source,
)


def valid_salary_row(**overrides):
    row = {
        "observation_id": "test-observation-1",
        "market_id": "IN",
        "occupation_id": "software-engineer",
        "occupational_classification": "JobIntel role family",
        "occupational_classification_version": "1",
        "geographic_region": "Bengaluru",
        "salary_value": "1800000",
        "currency": "INR",
        "salary_period": "ANNUAL",
        "compensation_definition": "Annual gross salary",
        "reference_period": "2025",
        "source_id": "in.jobintel.market-data",
        "collected_at": "2025-01-15T10:00:00Z",
    }
    return row | overrides


def valid_provenance(**overrides):
    return {
        "source_id": "in.jobintel.market-data",
        "collected_at": "2025-01-15T10:00:00Z",
        "reference_period": "2025-Q1",
        "geographic_coverage": ["India"],
        "dataset_description": "Synthetic test provenance record.",
        "validation_status": "VALIDATED",
    } | overrides


def test_market_registry_has_five_explicit_market_configs():
    markets = get_markets()
    assert {market.market_id for market in markets} == set(MarketId)
    assert all(set(market.capabilities) == set(MarketCapability) for market in markets)
    assert get_market("IN").primary_currency == CurrencyCode.INR
    assert get_market("US").primary_currency == CurrencyCode.USD
    assert get_market("UK").primary_currency == CurrencyCode.GBP
    assert get_market("AU").primary_currency == CurrencyCode.AUD
    assert get_market("SG").primary_currency == CurrencyCode.SGD
    assert get_market("IN").capabilities[MarketCapability.SALARY_PREDICTION] == CapabilityStatus.AVAILABLE
    assert get_market("US").capabilities[MarketCapability.SALARY_PREDICTION] == CapabilityStatus.AVAILABLE
    assert all(get_market(market).capabilities[MarketCapability.SALARY_PREDICTION] == CapabilityStatus.NOT_IMPLEMENTED for market in ("UK", "AU", "SG"))
    assert all(get_market(market).data_availability == CapabilityStatus.NOT_IMPLEMENTED for market in ("UK", "AU", "SG"))
    assert get_market("UK").last_successful_update is None


def test_market_registry_rejects_unknown_and_duplicate_ids():
    with pytest.raises(KeyError):
        get_market("XX")
    market = get_markets()[0]
    with pytest.raises(ValueError, match="unique"):
        MarketRegistry((market, market))


def test_source_catalog_has_review_status_and_no_collected_new_market_data():
    sources = get_sources()
    assert len(sources) == 11
    assert len({source.source_id for source in sources}) == len(sources)
    assert all(source.source_reference is not None for source in sources)
    assert all(source.collected_at is None for source in sources)
    assert all(source.validation_status == ValidationStatus.NOT_COLLECTED for source in sources)
    assert all(source.reuse_review_status != ReuseReviewStatus.APPROVED for source in sources)
    assert all(source.reuse_review_status == ReuseReviewStatus.REVIEW_REQUIRED for source in sources if source.source_id.startswith(("uk.", "au.", "sg.")))
    assert get_source("uk.ons.ashe").reference_period is not None


def test_source_registry_rejects_unknown_and_duplicate_ids():
    with pytest.raises(KeyError):
        get_source("not.registered")
    source = get_sources()[0]
    with pytest.raises(ValueError, match="unique"):
        SourceRegistry((source, source))


def test_salary_observation_preserves_amount_currency_period_and_classification():
    observation = SalaryObservation.model_validate(valid_salary_row())
    assert observation.salary_value == Decimal("1800000")
    assert observation.currency == CurrencyCode.INR
    assert observation.salary_period == SalaryPeriod.ANNUAL
    assert observation.occupational_classification_version == "1"


@pytest.mark.parametrize(
    "overrides",
    [
        {"salary_value": "NaN"},
        {"salary_value": "Infinity"},
        {"salary_value": "-Infinity"},
        {"salary_value": "0"},
        {"salary_value": "-1"},
        {"currency": "XYZ"},
        {"market_id": "XX"},
        {"salary_period": "BIWEEKLY"},
        {"reference_period": "2025-13"},
        {"collected_at": "2025-01-15T10:00:00"},
    ],
)
def test_salary_observation_rejects_invalid_values(overrides):
    with pytest.raises(ValidationError):
        SalaryObservation.model_validate(valid_salary_row(**overrides))


def test_salary_row_validation_reports_reasons_without_echoing_input():
    rows = [
        valid_salary_row(),
        valid_salary_row(observation_id="test-observation-1"),
        valid_salary_row(observation_id="test-observation-3", salary_value="-999999", compensation_definition="private raw value"),
        valid_salary_row(observation_id="test-observation-4", source_id="unknown.source"),
        valid_salary_row(observation_id="test-observation-5", currency="XYZ"),
        valid_salary_row(observation_id="test-observation-6", market_id="XX"),
        {"observation_id": "test-observation-7", "salary_value": "SECRET-SALARY"},
        "not a record",
    ]
    result = validate_salary_observations(rows)
    assert (result.rows_seen, result.rows_accepted, result.rows_rejected) == (8, 1, 7)
    codes = {issue.code for issue in result.issues}
    assert {
        "duplicate_identifier",
        "invalid_salary",
        "unsupported_currency",
        "unsupported_market",
        "unknown_source",
        "missing_required_field",
        "invalid_record",
    } <= codes
    assert {row.row_index for row in result.rejected_rows} == {1, 2, 3, 4, 5, 6, 7}
    serialized = result.model_dump_json()
    assert "SECRET-SALARY" not in serialized
    assert "private raw value" not in serialized
    assert "-999999" not in serialized


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity", "0", "-1"])
def test_salary_quality_codes_nonfinite_and_nonpositive_amounts_as_invalid_salary(amount):
    result = validate_salary_observations([valid_salary_row(salary_value=amount)])
    assert result.rows_rejected == 1
    assert result.issues[0].code == "invalid_salary"
    assert result.issues[0].message == "Invalid or missing value for this field."


def test_data_provenance_validation_checks_source_and_period():
    provenance = DataProvenance.model_validate(valid_provenance())
    assert provenance.reference_period == "2025-Q1"
    assert validate_data_provenance(valid_provenance()).rows_accepted == 1
    unknown_source = validate_data_provenance(valid_provenance(source_id="missing.source"))
    assert unknown_source.rows_rejected == 1
    assert unknown_source.issues[0].code == "unknown_source"
    invalid_period = validate_data_provenance(valid_provenance(reference_period="2025-99"))
    assert invalid_period.rows_rejected == 1
    assert invalid_period.issues[0].code == "invalid_reference_period"


def test_employer_profile_requires_evidence_and_classifies_india_entities():
    reference = EmployerSourceReference(
        source_name="Official company page",
        source_organization="Example Test Entity",
        source_reference="https://example.com/company",
        collected_at=datetime(2025, 1, 15, tzinfo=timezone.utc),
    )
    profile = EmployerProfile(
        company_id="example-test-entity",
        company_name="Example Test Entity",
        headquarters_country="IN",
        company_category=EmployerCategory.INDIAN_HEADQUARTERED,
        official_website="https://example.com",
        operating_markets=(MarketId.IN,),
        source_references=(reference,),
    )
    assert profile.company_category == EmployerCategory.INDIAN_HEADQUARTERED
    with pytest.raises(ValidationError):
        EmployerProfile(
            company_id="incorrect-india-category",
            company_name="Incorrect India Category",
            headquarters_country="US",
            company_category=EmployerCategory.INDIAN_HEADQUARTERED,
            source_references=(reference,),
        )
    with pytest.raises(ValidationError):
        EmployerProfile(
            company_id="multinational-without-india",
            company_name="Multinational Example",
            headquarters_country="US",
            company_category=EmployerCategory.MULTINATIONAL_OPERATING_IN_INDIA,
            source_references=(reference,),
        )


def test_verified_employer_and_location_require_evidence_and_timestamp():
    reference = EmployerSourceReference(
        source_name="Official company page",
        source_organization="Example Test Entity",
        source_reference="https://example.com/office",
    )
    location = EmployerLocation(
        city="Bengaluru",
        country_code="IN",
        location_type=EmployerLocationType.OFFICE,
        verification_source=reference,
    )
    assert location.verification_source == reference
    with pytest.raises(ValidationError):
        EmployerLocation(
            city="Bengaluru",
            country_code="IN",
            location_type=EmployerLocationType.OFFICE,
            verification_status=EmployerVerificationStatus.REVIEW_REQUIRED,
        )
    with pytest.raises(ValidationError):
        EmployerProfile(
            company_id="verified-without-date",
            company_name="Verified Example",
            headquarters_country="IN",
            company_category=EmployerCategory.INDIAN_HEADQUARTERED,
            source_references=(EmployerSourceReference(
                source_name="Official company page",
                source_organization="Verified Example",
                source_reference="https://example.com/company",
            ),),
            verification_status=EmployerVerificationStatus.VERIFIED,
        )


def test_employer_registry_is_empty_and_rejects_duplicate_ids():
    assert get_employers() == []
    reference = EmployerSourceReference(
        source_name="Official company page",
        source_organization="Example Test Entity",
        source_reference="https://example.com/company",
    )
    employer = EmployerProfile(
        company_id="example-test-entity",
        company_name="Example Test Entity",
        headquarters_country="IN",
        company_category=EmployerCategory.INDIAN_HEADQUARTERED,
        source_references=(reference,),
    )
    with pytest.raises(ValueError, match="unique"):
        EmployerRegistry((employer, employer))


def test_global_foundation_api_routes_are_additive_and_return_expected_statuses():
    paths = app.openapi()["paths"]
    assert {
        "/api/v1/markets",
        "/api/v1/markets/{market_id}",
        "/api/v1/sources",
        "/api/v1/sources/{source_id}",
        "/api/v1/employers",
        "/api/v1/employers/{company_id}",
    } <= set(paths)
    assert {"/api/india/predict", "/india/predict", "/api/usa/predict", "/usa/predict"} <= set(paths)
    markets_response = paths["/api/v1/markets"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert markets_response["items"]["$ref"] == "#/components/schemas/MarketConfig"
    capability_routes = {
        (MarketId.IN, MarketCapability.SALARY_PREDICTION): ("/api/india/predict", "post"),
        (MarketId.IN, MarketCapability.SALARY_ANALYTICS): ("/api/india/market-summary", "get"),
        (MarketId.IN, MarketCapability.SKILLS_ANALYTICS): ("/api/india/skills", "get"),
        (MarketId.US, MarketCapability.SALARY_PREDICTION): ("/api/usa/predict", "post"),
        (MarketId.US, MarketCapability.SALARY_ANALYTICS): ("/api/usa/market-summary", "get"),
        (MarketId.US, MarketCapability.SKILLS_ANALYTICS): ("/api/usa/skills", "get"),
    }
    actual_available = {
        (market.market_id, capability)
        for market in get_markets()
        for capability, status in market.capabilities.items()
        if status == CapabilityStatus.AVAILABLE
    }
    assert actual_available == set(capability_routes)
    for (market_id, capability), (path, method) in capability_routes.items():
        assert get_market(market_id).capabilities[capability] == CapabilityStatus.AVAILABLE
        assert method in paths[path]
    assert len(list_markets()) == 5
    assert retrieve_market("UK").primary_currency == CurrencyCode.GBP
    assert len(list_sources()) == 11
    assert retrieve_source("uk.ons.ashe").source_id == "uk.ons.ashe"
    assert list_employers() == []
    for retrieve, identifier in (
        (retrieve_market, "XX"),
        (retrieve_source, "unknown.source"),
        (retrieve_employer, "unknown-company"),
    ):
        with pytest.raises(HTTPException) as error:
            retrieve(identifier)
        assert error.value.status_code == 404
