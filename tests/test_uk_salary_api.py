from __future__ import annotations

import json

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import AnyHttpUrl

from src.backend.data_catalog.registry import get_source as get_live_source
from src.backend.main import app
from src.backend.routers import uk_salary as uk_salary_router
from src.backend.schemas.data import DataSource, ReuseReviewStatus, SourceCategory, ValidationStatus
from src.backend.schemas.uk_salary import UKValueStatus
from src.backend.services.uk_salary_service import EXPECTED_REGIONS, SOURCE_ID, SOURCE_REFERENCE
from tests.uk_salary_fixtures import make_publishable_manifest, make_service, write_fixture


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def published_fixture(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    approved_manifest = make_publishable_manifest(dataset_path, manifest)
    manifest_path.write_text(json.dumps(approved_manifest), encoding="utf-8")
    source = DataSource(
        source_id=SOURCE_ID,
        source_name="Synthetic ASHE test source",
        source_organization="Synthetic test fixture",
        source_reference=AnyHttpUrl(SOURCE_REFERENCE),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=ReuseReviewStatus.APPROVED,
        dataset_description="Isolated synthetic source for router tests.",
        geographic_coverage=tuple(region.value for region in EXPECTED_REGIONS),
        reference_period="2025",
        validation_status=ValidationStatus.VALIDATED,
    )
    import src.backend.services.uk_salary_service as service_module

    monkeypatch.setattr(service_module, "get_source", lambda _source_id: source)
    monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: source)
    monkeypatch.setattr(uk_salary_router, "DEFAULT_DATASET_PATH", dataset_path)
    monkeypatch.setattr(uk_salary_router, "DEFAULT_MANIFEST_PATH", manifest_path)
    service = make_service(dataset_path, manifest_path, records)
    monkeypatch.setattr(uk_salary_router, "get_uk_salary_service", lambda: service)
    yield service, source


def _synthetic_source(
    reference,
    reuse=ReuseReviewStatus.REVIEW_REQUIRED,
    validation=ValidationStatus.NOT_COLLECTED,
    geography=None,
    reference_period="2025",
):
    return DataSource(
        source_id=SOURCE_ID,
        source_name="Synthetic ASHE test source",
        source_organization="Synthetic test fixture",
        source_reference=AnyHttpUrl(reference),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=reuse,
        dataset_description="Isolated synthetic source for router tests.",
        geographic_coverage=tuple(geography or (region.value for region in EXPECTED_REGIONS)),
        reference_period=reference_period,
        validation_status=validation,
    )


def _install_gate_inputs(monkeypatch, manifest_path, dataset_path, source):
    monkeypatch.setattr(uk_salary_router, "DEFAULT_MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(uk_salary_router, "DEFAULT_DATASET_PATH", dataset_path)
    monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: source)


def test_every_endpoint_fails_closed_without_salary_leakage(client, monkeypatch):
    calls = []

    def forbidden_service_load():
        calls.append("called")
        raise AssertionError("service must not load while publication is disabled")

    monkeypatch.setattr(uk_salary_router, "get_uk_salary_service", forbidden_service_load)
    paths = [
        "/api/v1/markets/UK/salary/occupations",
        "/api/v1/markets/UK/salary/occupations/1001",
        "/api/v1/markets/UK/salary/occupations/1001/regions",
        "/api/v1/markets/UK/salary/regions/East/occupations",
        "/api/v1/markets/UK/salary/metadata",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 503
        body = response.json()
        assert body["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"
        assert "salary" not in body
        assert "annual_gross_median_gbp" not in response.text
    assert calls == []


@pytest.mark.parametrize(
    "case",
    [
        "review_required_local",
        "not_collected_publishable",
        "approved_local",
        "approved_source_reference_mismatch",
        "approved_checksum_mismatch",
        "approved_missing_record",
        "approved_wrong_use",
        "approved_false_reference_match_flag",
        "approved_wrong_source_id",
        "approved_invalid_timestamp",
        "approved_incomplete_record",
        "actual_dataset_checksum_mismatch",
        "source_id_mismatch",
        "catalog_metadata_missing_reference",
        "catalog_geography_mismatch",
        "catalog_reference_period_mismatch",
        "missing_manifest",
        "malformed_manifest",
        "missing_source",
    ],
)
def test_real_publication_dependency_denies_each_incomplete_state_for_all_routes(
    client, tmp_path, monkeypatch, case
):
    dataset_path, manifest_path, manifest, _records, _service = write_fixture(tmp_path)
    current_catalog_reference = str(get_live_source(SOURCE_ID).source_reference)
    source = _synthetic_source(current_catalog_reference)

    if case == "review_required_local":
        pass
    elif case == "not_collected_publishable":
        manifest = make_publishable_manifest(dataset_path, manifest)
        source = _synthetic_source(SOURCE_REFERENCE, ReuseReviewStatus.APPROVED, ValidationStatus.NOT_COLLECTED)
    elif case == "approved_local":
        source = _synthetic_source(
            current_catalog_reference,
            ReuseReviewStatus.APPROVED,
            ValidationStatus.VALIDATED,
        )
    elif case in {
        "approved_source_reference_mismatch",
        "approved_checksum_mismatch",
        "approved_missing_record",
        "approved_wrong_use",
        "approved_false_reference_match_flag",
        "approved_wrong_source_id",
        "approved_invalid_timestamp",
        "approved_incomplete_record",
        "actual_dataset_checksum_mismatch",
        "catalog_geography_mismatch",
        "catalog_reference_period_mismatch",
    }:
        manifest = make_publishable_manifest(dataset_path, manifest)
        source = _synthetic_source(SOURCE_REFERENCE, ReuseReviewStatus.APPROVED, ValidationStatus.VALIDATED)
        if case == "approved_source_reference_mismatch":
            source = _synthetic_source(
                current_catalog_reference,
                ReuseReviewStatus.APPROVED,
                ValidationStatus.VALIDATED,
            )
        elif case == "approved_checksum_mismatch":
            manifest["publication_approval"]["approved_dataset_sha256"] = "0" * 64
        elif case == "approved_missing_record":
            manifest.pop("publication_approval")
        elif case == "approved_wrong_use":
            manifest["publication_approval"]["approved_uses"] = ["internal_analysis"]
        elif case == "approved_false_reference_match_flag":
            manifest["source_reference_matches_catalog"] = False
            manifest["publication_approval"]["source_reference_matches_catalog"] = False
        elif case == "approved_wrong_source_id":
            manifest["publication_approval"]["source_id"] = "different.source"
        elif case == "approved_invalid_timestamp":
            manifest["publication_approval"]["approved_at"] = "not-a-timestamp"
        elif case == "approved_incomplete_record":
            manifest["publication_approval"].pop("approved_by")
        elif case == "actual_dataset_checksum_mismatch":
            dataset_path.write_bytes(dataset_path.read_bytes() + b"tampered")
        elif case == "catalog_geography_mismatch":
            source = source.model_copy(update={"geographic_coverage": ("United Kingdom", "Regions")})
        elif case == "catalog_reference_period_mismatch":
            source = source.model_copy(update={"reference_period": "2026"})
    elif case == "missing_manifest":
        manifest_path.unlink()
    elif case == "malformed_manifest":
        manifest_path.write_text("{invalid", encoding="utf-8")

    if case not in {"missing_manifest", "malformed_manifest"}:
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _install_gate_inputs(monkeypatch, manifest_path, dataset_path, source)
    if case == "missing_source":
        monkeypatch.setattr(
            uk_salary_router,
            "get_source",
            lambda _source_id: (_ for _ in ()).throw(KeyError("private source detail")),
        )
    elif case == "source_id_mismatch":
        monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: source.model_copy(update={"source_id": "other.source"}))
    elif case == "catalog_metadata_missing_reference":
        monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: source.model_copy(update={"source_reference": None}))
    calls = []

    def forbidden_service_load():
        calls.append(True)
        raise AssertionError("service must not load while publication is denied")

    monkeypatch.setattr(uk_salary_router, "get_uk_salary_service", forbidden_service_load)
    paths = [
        "/api/v1/markets/UK/salary/occupations",
        "/api/v1/markets/UK/salary/occupations/1001",
        "/api/v1/markets/UK/salary/occupations/1001/regions",
        "/api/v1/markets/UK/salary/regions/East/occupations",
        "/api/v1/markets/UK/salary/metadata",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 503
        assert response.json()["detail"]["code"] in {"UK_DATA_NOT_PUBLISHED", "UK_DATA_UNAVAILABLE"}
        assert "annual_gross_median_gbp" not in response.text
        assert "45000" not in response.text
    assert calls == []


def test_real_publication_dependency_passes_complete_isolated_approval(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _service = write_fixture(tmp_path)
    approved_manifest = make_publishable_manifest(dataset_path, manifest)
    manifest_path.write_text(json.dumps(approved_manifest), encoding="utf-8")
    source = _synthetic_source(SOURCE_REFERENCE, ReuseReviewStatus.APPROVED, ValidationStatus.VALIDATED)
    _install_gate_inputs(monkeypatch, manifest_path, dataset_path, source)

    assert uk_salary_router.require_uk_publication() is None


@pytest.mark.parametrize("manifest_state", ["missing", "malformed"])
def test_real_publication_dependency_fails_closed_for_missing_or_malformed_manifest(
    tmp_path, monkeypatch, manifest_state
):
    manifest_path = tmp_path / "provenance_manifest.json"
    dataset_path = tmp_path / "dataset.csv"
    dataset_path.write_text("not loaded", encoding="utf-8")
    if manifest_state == "malformed":
        manifest_path.write_text("{invalid", encoding="utf-8")
    source = _synthetic_source(SOURCE_REFERENCE, ReuseReviewStatus.APPROVED, ValidationStatus.VALIDATED)
    _install_gate_inputs(monkeypatch, manifest_path, dataset_path, source)

    with pytest.raises(HTTPException) as exc:
        uk_salary_router.require_uk_publication()
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] in {"UK_DATA_NOT_PUBLISHED", "UK_DATA_UNAVAILABLE"}


def test_real_publication_dependency_fails_closed_when_source_entry_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: (_ for _ in ()).throw(KeyError("private")))
    with pytest.raises(HTTPException) as exc:
        uk_salary_router.require_uk_publication()
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "UK_DATA_UNAVAILABLE"


def test_occupation_search_and_pagination_contract(client, published_fixture):
    response = client.get("/api/v1/markets/UK/salary/occupations", params={"q": "ANALYST", "page": 1, "page_size": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["soc_code"] == "1001"
    assert body["context"]["source_id"] == "uk.ons.ashe"
    assert body["context"]["occupation_classification"] == "SOC 2020 unit group"
    assert body["coverage"]["expected_count"] == 11

    empty_page = client.get("/api/v1/markets/UK/salary/occupations", params={"q": "no match"})
    assert empty_page.status_code == 200
    assert empty_page.json()["items"] == []
    assert empty_page.json()["total_count"] == 0


def test_occupation_detail_and_partial_region_comparison(client, published_fixture):
    detail = client.get("/api/v1/markets/UK/salary/occupations/1001")
    assert detail.status_code == 200
    body = detail.json()
    assert len(body["regions"]) == 11
    assert body["regions"][0]["annual_gross_median_gbp"] == "45000"
    assert body["regions"][1]["value_status"] == "SUPPRESSED_QUALITY"
    assert body["regions"][1]["annual_gross_median_gbp"] is None
    assert body["regions"][2]["value_status"] == "BLANK_UNKNOWN"
    assert body["regions"][2]["annual_gross_median_gbp"] is None

    comparison = client.get("/api/v1/markets/UK/salary/occupations/1001/regions")
    assert comparison.status_code == 200
    compare_body = comparison.json()
    assert compare_body["reported_regions_count"] == 1
    assert compare_body["expected_regions_count"] == 11
    assert compare_body["coverage_warning"]


def test_regional_listing_filters_status_and_paginates(client, published_fixture):
    reported = client.get(
        "/api/v1/markets/UK/salary/regions/East/occupations",
        params={"value_status": UKValueStatus.REPORTED.value, "page_size": 1},
    )
    assert reported.status_code == 200
    assert reported.json()["items"][0]["observation"]["annual_gross_median_gbp"] == "45000"
    assert reported.json()["coverage"]["reported_count"] == 1

    suppressed = client.get(
        "/api/v1/markets/UK/salary/regions/East%20Midlands/occupations",
        params={"value_status": "SUPPRESSED_QUALITY"},
    )
    assert suppressed.status_code == 200
    assert suppressed.json()["items"][0]["observation"]["annual_gross_median_gbp"] is None


def test_source_metadata_contract(client, published_fixture):
    response = client.get("/api/v1/markets/UK/salary/metadata")
    assert response.status_code == 200
    body = response.json()
    assert body["context"]["reference_period"] == "Tax year ending 5 April 2025"
    assert body["context"]["publication_status"] == "PUBLISHED"
    assert body["occupation_count"] == 1
    assert body["region_count"] == 11
    assert body["observation_count"] == 11
    assert "data" not in body


def test_live_catalog_revocation_blocks_requests_even_after_service_was_loaded(
    client, published_fixture, monkeypatch
):
    _service, approved_source = published_fixture
    service_loads = []
    monkeypatch.setattr(
        uk_salary_router,
        "get_uk_salary_service",
        lambda: (service_loads.append(True) or _service),
    )

    first = client.get("/api/v1/markets/UK/salary/metadata")
    assert first.status_code == 200
    assert first.json()["context"]["publication_status"] == "PUBLISHED"
    assert len(service_loads) == 1

    revoked_source = approved_source.model_copy(update={"reuse_review_status": ReuseReviewStatus.REVIEW_REQUIRED})
    monkeypatch.setattr(uk_salary_router, "get_source", lambda _source_id: revoked_source)
    second = client.get("/api/v1/markets/UK/salary/metadata")
    assert second.status_code == 503
    assert second.json()["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"
    assert len(service_loads) == 1


def test_invalid_and_unknown_ids_have_distinct_responses(client, published_fixture):
    invalid_code = client.get("/api/v1/markets/UK/salary/occupations/10A1")
    assert invalid_code.status_code == 422
    unknown_code = client.get("/api/v1/markets/UK/salary/occupations/9999")
    assert unknown_code.status_code == 404
    assert unknown_code.json()["detail"] == "Occupation not found"

    invalid_region_syntax = client.get("/api/v1/markets/UK/salary/regions/East-Nowhere/occupations")
    assert invalid_region_syntax.status_code == 422
    unknown_region = client.get("/api/v1/markets/UK/salary/regions/Imaginary/occupations")
    assert unknown_region.status_code == 404


def test_query_bounds_and_status_validation(client, published_fixture):
    assert client.get("/api/v1/markets/UK/salary/occupations", params={"page_size": 101}).status_code == 422
    assert client.get("/api/v1/markets/UK/salary/occupations", params={"page": 0}).status_code == 422
    assert client.get("/api/v1/markets/UK/salary/occupations", params={"q": "   "}).status_code == 422
    assert client.get(
        "/api/v1/markets/UK/salary/regions/East/occupations",
        params={"value_status": "MADE_UP"},
    ).status_code == 422


# ===========================================================================
# SPRINT 2C.2.2 — TASK 2: Independent Dual-Layer UK Governance Gate Verification
# ===========================================================================

def test_task2_layer1_blocks_real_publication_state(client):
    """Task 2: Real unmodified UK publication state fails closed on Layer 1 across all 5 endpoints."""
    all_5_endpoints = [
        "/api/v1/markets/UK/salary/occupations",
        "/api/v1/markets/UK/salary/occupations/1001",
        "/api/v1/markets/UK/salary/occupations/1001/regions",
        "/api/v1/markets/UK/salary/regions/East/occupations",
        "/api/v1/markets/UK/salary/metadata",
    ]
    for endpoint in all_5_endpoints:
        res = client.get(endpoint)
        assert res.status_code == 503
        data = res.json()
        assert data["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"
        assert "annual_gross_median_gbp" not in res.text
        assert "items" not in data


def test_task2_layer1_revocation_blocks_when_layer2_satisfied(client, published_fixture):
    """Task 2: Layer 1 revocation independently fails closed even when Layer 2 is fully satisfied."""
    from src.backend.governance.service import get_governance_engine
    from src.backend.governance.schemas import RevocationRecord, RevocationScope
    from datetime import datetime, timezone

    engine = get_governance_engine()
    rec = RevocationRecord(
        revocation_id="rev-ashe-test-001",
        scope=RevocationScope.SOURCE,
        target_identifier=SOURCE_ID,
        reason_code="STATUTORY_HALT",
        description="Statutory cease and desist",
        revoked_by="Legal Counsel",
        revoked_at=datetime.now(timezone.utc),
    )
    engine.revocation_registry.register(rec)
    try:
        res = client.get("/api/v1/markets/UK/salary/metadata")
        assert res.status_code == 503
        assert res.json()["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"
    finally:
        # Clean up registry
        engine.revocation_registry._records_by_id.pop("rev-ashe-test-001", None)
        engine.revocation_registry._by_source.pop(SOURCE_ID, None)


def test_task2_layer1_degraded_registry_blocks_when_layer2_satisfied(client, published_fixture):
    """Task 2: Layer 1 degraded revocation registry independently fails closed even when Layer 2 is satisfied."""
    from src.backend.governance.service import get_governance_engine
    engine = get_governance_engine()
    original_healthy = engine.revocation_registry._is_healthy
    engine.revocation_registry._is_healthy = False
    engine.revocation_registry._status = "MISSING_MANIFEST"
    try:
        res = client.get("/api/v1/markets/UK/salary/metadata")
        assert res.status_code == 503
        assert res.json()["detail"]["code"] == "UK_DATA_NOT_PUBLISHED"
    finally:
        engine.revocation_registry._is_healthy = original_healthy
        engine.revocation_registry._status = "HEALTHY"


def test_task2_layer2_blocks_when_layer1_satisfied(client, published_fixture, monkeypatch):
    """Task 2: Layer 2 independently fails closed on checksum mismatch when Layer 1 is satisfied."""
    _service, source = published_fixture
    # Break checksum match in Layer 2
    import src.backend.routers.uk_salary as router_mod
    monkeypatch.setattr(router_mod, "approved_dataset_checksum_matches", lambda manifest, path: False)

    res = client.get("/api/v1/markets/UK/salary/metadata")
    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "UK_DATA_UNAVAILABLE"

