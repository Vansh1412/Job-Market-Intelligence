from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal

import pytest

from src.backend.schemas.uk_salary import UKValueStatus
from src.backend.services.uk_salary_service import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MANIFEST_PATH,
    EXPECTED_REGIONS,
    SOURCE_REFERENCE,
    UKSalaryNotFound,
    UKSalaryService,
    UKSalaryServiceError,
)
from src.backend.ingestion.runner import serialize_dataset
from tests.uk_salary_fixtures import make_publishable_manifest, make_records, make_service, write_fixture


def _patch_live_catalog_reference(monkeypatch, reference):
    from pydantic import AnyHttpUrl
    import src.backend.services.uk_salary_service as service_module
    from src.backend.data_catalog.registry import get_source

    source = get_source("uk.ons.ashe").model_copy(update={
        "source_reference": AnyHttpUrl(reference),
        "geographic_coverage": tuple(region.value for region in EXPECTED_REGIONS),
        "reference_period": "2025",
    })
    monkeypatch.setattr(service_module, "get_source", lambda _source_id: source)


def _rewrite_csv(dataset_path, manifest_path, rows, fieldnames=None):
    if fieldnames is None:
        with dataset_path.open(encoding="utf-8", newline="") as stream:
            fieldnames = next(csv.reader(stream))
    with dataset_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: value for key, value in row.items() if key in fieldnames} for row in rows)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["processed_dataset_sha256"] = hashlib.sha256(dataset_path.read_bytes()).hexdigest().upper()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def _read_rows(dataset_path):
    with dataset_path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def test_valid_dataset_manifest_and_provenance_load(tmp_path):
    _, _, manifest, _, service = write_fixture(tmp_path)
    assert service.row_count == 11
    assert service.metadata().context.source_id == "uk.ons.ashe"
    assert service.metadata().context.reference_period == "Tax year ending 5 April 2025"
    assert service.metadata().context.transformation_version == "ashe-table15-2025r-v1.0.2"
    assert manifest["publication_eligible"] is False
    assert service.metadata().context.publication_status == "NOT_PUBLISHED"


def test_local_manifest_state_is_preserved_and_never_marked_published(tmp_path):
    _, manifest_path, _, _, service = write_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["processing_mode"] == "LOCAL_PREPARATION_ONLY"
    assert manifest["publication_eligible"] is False
    assert manifest["source_reuse_review_status"] == "REVIEW_REQUIRED"
    assert "catalog_validation_status" not in manifest
    assert service.metadata().context.publication_status == "NOT_PUBLISHED"


def test_current_local_phase2a_manifest_remains_non_publishable():
    if not DEFAULT_MANIFEST_PATH.is_file():
        pytest.skip("the ignored Phase 2A manifest is unavailable in this environment")
    manifest = json.loads(DEFAULT_MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["processing_mode"] == "LOCAL_PREPARATION_ONLY"
    assert manifest["publication_eligible"] is False
    assert manifest["source_reuse_review_status"] == "REVIEW_REQUIRED"
    assert "catalog_validation_status" not in manifest


def test_valid_future_publishable_manifest_passes_integrity_without_claiming_publication(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    service = make_service(dataset_path, manifest_path, records)

    assert service.row_count == 11
    # The registry is intentionally still REVIEW_REQUIRED / NOT_COLLECTED.
    assert service.metadata().context.publication_status == "NOT_PUBLISHED"


def test_publishable_manifest_with_invalid_dataset_checksum_is_rejected(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest["processed_dataset_sha256"] = "0" * 64
    future_manifest["publication_approval"]["approved_dataset_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_checksum_mismatch"):
        make_service(dataset_path, manifest_path, records)


def test_publishable_manifest_with_incorrect_source_identity_is_rejected(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest["publication_approval"]["source_id"] = "different.source"
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_publication_approval_invalid"):
        make_service(dataset_path, manifest_path, records)


def test_publishable_manifest_without_approval_metadata_is_rejected(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest.pop("publication_approval")
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_publication_approval_invalid"):
        make_service(dataset_path, manifest_path, records)


def test_dataset_source_reference_must_match_manifest(tmp_path):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    rows[0]["source_reference"] = SOURCE_REFERENCE + "/incorrect"
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)

    with pytest.raises(UKSalaryServiceError, match="uk_row_source_reference_mismatch"):
        make_service(dataset_path, manifest_path, records)


def test_manifest_source_reference_must_match_verified_dataset_identity(tmp_path):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    manifest["source_reference"] = SOURCE_REFERENCE + "/incorrect"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_source_reference_mismatch"):
        make_service(dataset_path, manifest_path, records)


def test_manifest_catalog_reference_must_match_live_catalog_entry(tmp_path):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    manifest["catalog_source_reference"] = "https://catalog.example.invalid/other"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_catalog_reference_mismatch"):
        make_service(dataset_path, manifest_path, records)


def test_false_reference_match_flag_is_rejected_for_publication_manifest(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest["source_reference_matches_catalog"] = False
    future_manifest["publication_approval"]["source_reference_matches_catalog"] = False
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_reference_match_flag_invalid"):
        make_service(dataset_path, manifest_path, records)


def test_inconsistent_future_data_provenance_is_rejected(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest["data_provenance"]["source_reference"] = SOURCE_REFERENCE + "/wrong"
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_publication_approval_invalid"):
        make_service(dataset_path, manifest_path, records)


def test_approval_checksum_must_match_manifest_checksum(tmp_path, monkeypatch):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    future_manifest["publication_approval"]["approved_dataset_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match="uk_manifest_publication_approval_invalid"):
        make_service(dataset_path, manifest_path, records)


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("timestamp", "uk_manifest_publication_approval_invalid"),
        ("use", "uk_manifest_publication_approval_invalid"),
        ("catalog_status", "uk_manifest_publication_approval_invalid"),
        ("mode", "uk_manifest_processing_mode_invalid"),
    ],
)
def test_incomplete_future_publication_metadata_is_rejected(tmp_path, monkeypatch, mutation, expected_code):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    future_manifest = make_publishable_manifest(dataset_path, manifest)
    _patch_live_catalog_reference(monkeypatch, future_manifest["source_reference"])
    if mutation == "timestamp":
        future_manifest["publication_approval"]["approved_at"] = "not-a-time"
    elif mutation == "use":
        future_manifest["publication_approval"]["approved_uses"] = ["internal_analysis"]
    elif mutation == "catalog_status":
        future_manifest["catalog_validation_status"] = "NOT_COLLECTED"
    elif mutation == "mode":
        future_manifest["processing_mode"] = "UNRECOGNIZED"
    manifest_path.write_text(json.dumps(future_manifest), encoding="utf-8")

    with pytest.raises(UKSalaryServiceError, match=expected_code):
        make_service(dataset_path, manifest_path, records)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("source_id", "not.uk.ashe", "uk_manifest_contract_mismatch"),
        ("transformation_version", "ashe-table15-2025r-v9", "uk_manifest_contract_mismatch"),
        ("archive_checksum_verified", False, "uk_manifest_contract_mismatch"),
        ("occupation_classification", "SOC 2010", "uk_manifest_contract_mismatch"),
        ("geography_level", "UK", "uk_manifest_contract_mismatch"),
        ("publication_eligible", True, "uk_manifest_publication_state_mismatch"),
        ("archive_sha256", "0" * 64, "uk_manifest_contract_mismatch"),
    ],
)
def test_manifest_identity_and_release_controls_are_validated(tmp_path, field, value, code):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    manifest[field] = value
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(UKSalaryServiceError) as exc:
        make_service(dataset_path, manifest_path, records)
    assert exc.value.code == code


def test_csv_checksum_is_pinned_and_checked(tmp_path):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    dataset_path.write_bytes(dataset_path.read_bytes() + b" ")
    with pytest.raises(UKSalaryServiceError, match="uk_checksum_mismatch"):
        make_service(dataset_path, manifest_path, records, expected_csv_sha256=manifest["processed_dataset_sha256"])


def test_required_schema_is_validated_without_skipping_rows(tmp_path):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    fieldnames.remove("original_ons_cv_cell")
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)
    with pytest.raises(UKSalaryServiceError, match="uk_schema_invalid"):
        make_service(dataset_path, manifest_path, records)


def test_duplicate_occupation_region_is_rejected(tmp_path):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    rows[-1] = dict(rows[2])  # preserve status counts but duplicate a blank region key
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)
    with pytest.raises(UKSalaryServiceError, match="uk_duplicate_or_missing_key"):
        make_service(dataset_path, manifest_path, records)


@pytest.mark.parametrize("bad_value", ["NaN", "Infinity", "-Infinity", "0", "-1"])
def test_invalid_nonfinite_or_nonpositive_median_is_rejected(tmp_path, bad_value):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    rows[0]["salary_value"] = bad_value
    rows[0]["original_ons_median_cell"] = bad_value
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)
    with pytest.raises(UKSalaryServiceError) as exc:
        make_service(dataset_path, manifest_path, records)
    assert exc.value.code in {"uk_row_invalid", "uk_non_finite_salary"}


@pytest.mark.parametrize("bad_cv", ["NaN", "Infinity", "-1", "invalid"])
def test_invalid_cv_is_rejected(tmp_path, bad_cv):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    rows[0]["original_ons_cv"] = bad_cv
    rows[0]["original_ons_cv_cell"] = bad_cv
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)
    with pytest.raises(UKSalaryServiceError):
        make_service(dataset_path, manifest_path, records)


def test_reported_suppressed_and_blank_values_remain_distinct(tmp_path):
    _, _, _, _, service = write_fixture(tmp_path)
    detail = service.get_occupation("1001")
    assert detail.regions[0].value_status == UKValueStatus.REPORTED
    assert detail.regions[0].annual_gross_median_gbp == Decimal("45000")
    assert detail.regions[0].cv_percent == Decimal("5")
    assert detail.regions[1].value_status == UKValueStatus.SUPPRESSED_QUALITY
    assert detail.regions[1].original_ons_median_cell == "x"
    assert detail.regions[1].annual_gross_median_gbp is None
    assert detail.regions[2].value_status == UKValueStatus.BLANK_UNKNOWN
    assert detail.regions[2].original_ons_median_cell == ""
    assert detail.regions[2].annual_gross_median_gbp is None
    assert detail.coverage.reported_count == 1
    assert detail.coverage.suppressed_count == 1
    assert detail.coverage.blank_count == 9


def test_source_ids_and_row_occupation_codes_are_validated(tmp_path):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    fieldnames, rows = _read_rows(dataset_path)
    rows[0]["source_id"] = "unknown.source"
    _rewrite_csv(dataset_path, manifest_path, rows, fieldnames)
    with pytest.raises(UKSalaryServiceError):
        make_service(dataset_path, manifest_path, records)

    code_path, code_manifest, _, code_records, _ = write_fixture(tmp_path / "invalid-code-copy")
    code_fields, code_rows = _read_rows(code_path)
    code_rows[0]["occupation_code"] = "10A1"
    _rewrite_csv(code_path, code_manifest, code_rows, code_fields)
    with pytest.raises(UKSalaryServiceError, match="uk_row_invalid"):
        make_service(code_path, code_manifest, code_records)


@pytest.mark.parametrize("missing", ["dataset", "manifest"])
def test_missing_artifacts_fail_closed(tmp_path, missing):
    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path)
    if missing == "dataset":
        dataset_path.unlink()
        expected_code = "uk_dataset_missing"
    else:
        manifest_path.unlink()
        expected_code = "uk_manifest_missing"
    with pytest.raises(UKSalaryServiceError) as exc:
        make_service(dataset_path, manifest_path, records)
    assert exc.value.code == expected_code


def test_unsupported_transformation_is_rejected(tmp_path):
    dataset_path, manifest_path, manifest, records, _ = write_fixture(tmp_path)
    manifest["transformation_version"] = "future-unverified"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(UKSalaryServiceError, match="uk_manifest_contract_mismatch"):
        make_service(dataset_path, manifest_path, records)


def test_unknown_occupation_raises_not_found(tmp_path):
    _, _, _, _, service = write_fixture(tmp_path)
    with pytest.raises(UKSalaryNotFound, match="occupation_not_found"):
        service.get_occupation("9999")


def test_partial_coverage_and_region_comparison_are_explicit(tmp_path):
    _, _, _, _, service = write_fixture(tmp_path)
    comparison = service.compare_regions("1001")
    assert comparison.reported_regions_count == 1
    assert comparison.expected_regions_count == 11
    assert comparison.coverage_ratio == Decimal("0.0909")
    assert comparison.coverage_warning is not None
    assert sum(item.annual_gross_median_gbp is not None for item in comparison.observations) == 1


def test_deterministic_search_order_and_bounded_pagination(tmp_path):
    records = make_records(("1002", "1001"))
    _, _, _, _, service = write_fixture(tmp_path, records)
    first = service.list_occupations("analyst", 1, 1)
    second = service.list_occupations("analyst", 2, 1)
    beyond = service.list_occupations("analyst", 3, 1)
    assert [item.soc_code for item in first.items] == ["1001"]
    assert [item.soc_code for item in second.items] == ["1002"]
    assert first.total_count == 2 and first.has_next is True
    assert second.has_next is False
    assert beyond.items == () and beyond.total_count == 2
    assert service.list_occupations("no-match", 1, 10).total_count == 0


def test_regional_listing_filters_status_and_exposes_full_coverage(tmp_path):
    _, _, _, _, service = write_fixture(tmp_path)
    reported = service.list_region_occupations("East", UKValueStatus.REPORTED, 1, 10)
    suppressed = service.list_region_occupations("East Midlands", UKValueStatus.SUPPRESSED_QUALITY, 1, 10)
    assert reported.total_count == 1
    assert reported.items[0].observation.annual_gross_median_gbp == Decimal("45000")
    assert reported.coverage.expected_count == 1
    assert suppressed.total_count == 1
    assert suppressed.items[0].observation.annual_gross_median_gbp is None


def test_invalid_region_and_unknown_publication_source_fail_closed(tmp_path, monkeypatch):
    _, _, _, _, service = write_fixture(tmp_path)
    with pytest.raises(UKSalaryNotFound, match="region_not_found"):
        service.list_region_occupations("Imaginary", UKValueStatus.REPORTED, 1, 10)

    import src.backend.services.uk_salary_service as module

    dataset_path, manifest_path, _, records, _ = write_fixture(tmp_path / "second")
    monkeypatch.setattr(module, "get_source", lambda _source: (_ for _ in ()).throw(KeyError("private")))
    with pytest.raises(UKSalaryServiceError, match="uk_source_unregistered"):
        make_service(dataset_path, manifest_path, records)


def test_loading_does_not_mutate_source_files(tmp_path):
    dataset_path, manifest_path, _, _, _ = write_fixture(tmp_path)
    before = (dataset_path.read_bytes(), manifest_path.read_bytes())
    UKSalaryService(
        dataset_path,
        manifest_path,
        expected_archive_sha256="AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3",
        expected_csv_sha256=hashlib.sha256(before[0]).hexdigest().upper(),
        expected_occupation_count=1,
        expected_row_count=11,
        expected_status_counts={"REPORTED": 1, "SUPPRESSED_QUALITY": 1, "BLANK_UNKNOWN": 9},
    )
    assert (dataset_path.read_bytes(), manifest_path.read_bytes()) == before


def test_default_artifact_paths_point_only_to_processed_data():
    assert DEFAULT_DATASET_PATH.parts[-1] == "ashe_2025_full_time_annual_gross_median_gb.csv"
    assert DEFAULT_MANIFEST_PATH.name == "provenance_manifest.json"
    assert "processed" in DEFAULT_DATASET_PATH.parts


@pytest.mark.skipif(
    not (DEFAULT_DATASET_PATH.is_file() and DEFAULT_MANIFEST_PATH.is_file()),
    reason="verified local ASHE artifacts are ignored and are not required for CI unit tests",
)
def test_local_processed_ashe_artifact_passes_service_validation():
    service = UKSalaryService()
    assert service.row_count == 4532
    assert service.metadata().occupation_count == 412
    assert service.metadata().region_count == 11
    assert service.metadata().observation_count == 4532
    assert service.metadata().context.publication_status == "NOT_PUBLISHED"
