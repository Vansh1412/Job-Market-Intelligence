from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import Workbook
from pydantic import ValidationError

from src.backend.data_catalog.registry import get_source
from src.backend.ingestion.ashe2025 import (
    EXPECTED_HEADER,
    SOURCE_REFERENCE,
    TRANSFORMATION_VERSION,
    OccupationReference,
    classify_source_cell,
    load_occupation_reference,
    parse_cv_cell,
    parse_workbook_pair,
    sha256_file,
    verify_sha256,
)
from src.backend.ingestion.contracts import ASHERunManifest, ASHEValueStatus
from src.backend.ingestion.runner import (
    DEFAULT_ARCHIVE,
    DEFAULT_EXTRACTED,
    DEFAULT_SOC_REFERENCE,
    EXPECTED_ARCHIVE_SHA256,
    EXPECTED_CODES,
    EXPECTED_NUMERIC,
    EXPECTED_REGIONS,
    EXPECTED_RECORDS,
    EXPECTED_SUPPRESSED,
    EXPECTED_BLANK,
    build_data_provenance,
    count_value_statuses,
    serialize_dataset,
    validate_expected_grid,
    verify_archive_layout,
    PipelineError,
)
from src.backend.schemas.data import DataQualityResult, ReuseReviewStatus, ValidationStatus


ARCHIVE_SHA = "A" * 64
ESTIMATE_SHA = "B" * 64
CV_SHA = "C" * 64
SOC_SHA = "D" * 64
INGESTED_AT = datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)


def _write_source_workbook(path: Path, rows: list[tuple[object, ...]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Full-Time"
    for _ in range(4):
        sheet.append([None] * 17)
    sheet.append(list(EXPECTED_HEADER))
    for row in rows:
        sheet.append(list(row))
    workbook.save(path)


def _data_row(region: str, code: str, median: object) -> tuple[object, ...]:
    return (
        f"      {region}, Occupation {code.strip(chr(39))}", code, 10, median,
        None, 45_000.0, None, "x", "x", "x", "x", "x", "x", "x", "x", "x", "x",
    )


def _fixture_files(tmp_path: Path):
    estimate_path = tmp_path / "estimate.xlsx"
    cv_path = tmp_path / "cv.xlsx"
    estimate_rows = [
        _data_row("London", "'1111", 32_000.0),
        _data_row("Wales", "'1111", 31_000.0),
        _data_row("London", "'1112", "x"),
        _data_row("Wales", "'1112", None),
    ]
    cv_rows = [
        _data_row("London", "'1111", 5.0),
        _data_row("Wales", "'1111", 10.5),
        _data_row("London", "'1112", "x"),
        _data_row("Wales", "'1112", None),
    ]
    _write_source_workbook(estimate_path, estimate_rows)
    _write_source_workbook(cv_path, cv_rows)
    occupations = {
        "1111": OccupationReference("1111", "Official occupation one", 1, "Major group one"),
        "1112": OccupationReference("1112", "Official occupation two", 1, "Major group one"),
    }
    return estimate_path, cv_path, occupations, estimate_rows, cv_rows


def _parse_fixture(estimate_path, cv_path, occupations, **kwargs):
    arguments = {
        "run_id": "ashe25r-aaaaaaaaaaaaaaaa-ashe-table15-2025r-v1",
        "archive_sha256": ARCHIVE_SHA,
        "estimate_filename": estimate_path.name,
        "estimate_sha256": ESTIMATE_SHA,
        "cv_filename": cv_path.name,
        "cv_sha256": CV_SHA,
        "classification_filename": "soc-reference.xlsx",
        "classification_sha256": SOC_SHA,
        "catalog_source_reference": "https://example.test/registry-source",
    }
    arguments.update(kwargs)
    return parse_workbook_pair(estimate_path, cv_path, occupations, **arguments)


def test_archive_checksum_verification_accepts_matching_and_rejects_mismatch(tmp_path):
    source = tmp_path / "archive.zip"
    source.write_bytes(b"fixture archive bytes")
    expected = hashlib.sha256(source.read_bytes()).hexdigest().upper()
    assert verify_sha256(source, expected) == expected
    with pytest.raises(ValueError, match="checksum"):
        verify_sha256(source, "0" * 64)


def test_workbook_parsing_and_cell_status_classification(tmp_path):
    estimate, cv, occupations, _, _ = _fixture_files(tmp_path)
    parsed = _parse_fixture(estimate, cv, occupations)
    assert parsed.quality.rows_seen == 4
    assert parsed.quality.rows_accepted == 4
    assert parsed.quality.rows_rejected == 0
    assert parsed.value_status_counts == {
        "BLANK_UNKNOWN": 1,
        "REPORTED": 2,
        "SUPPRESSED_QUALITY": 1,
    }
    assert parsed.records[0].occupation_code == "1111"
    assert parsed.records[0].source_occupation_code == "'1111"
    assert parsed.records[0].classification_id == "SOC"
    assert parsed.records[0].classification_version == "2020"
    assert parsed.records[0].salary_value == Decimal("32000.0")
    assert parsed.records[0].original_ons_cv == Decimal("5.0")
    assert parsed.records[0].source_reference_matches_catalog is False
    assert classify_source_cell("x")[0] == ASHEValueStatus.SUPPRESSED_QUALITY
    assert classify_source_cell("..")[0] == ASHEValueStatus.SUPPRESSED_DISCLOSURE
    assert classify_source_cell(":")[0] == ASHEValueStatus.NOT_APPLICABLE
    assert classify_source_cell("-")[0] == ASHEValueStatus.NIL_OR_NEGLIGIBLE
    assert classify_source_cell(None)[0] == ASHEValueStatus.BLANK_UNKNOWN
    assert parsed.records[-1].salary_value is None
    assert parsed.records[-1].original_ons_median_cell == ""


def test_official_occupation_mapping_uses_hierarchy_and_preserves_titles(tmp_path):
    reference = tmp_path / "soc.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "SOC2020 descriptions"
    sheet.append((
        "UNIQUE ID", "SOC2020 Major Group", "SOC2020 Sub-Major Group",
        "SOC2020 Minor Group", "SOC2020 Unit Group", "SOC2020\nGroup Title",
    ))
    sheet.append(("<blank>", 1, "<blank>", "<blank>", "<blank>", "Major One"))
    sheet.append(("soc-1", "<blank>", "<blank>", "<blank>", 1111, "Official title"))
    sheet.append(("soc-2", "<blank>", "<blank>", "<blank>", 1112, "Second official title"))
    workbook.save(reference)
    mapped = load_occupation_reference(reference)
    assert set(mapped) == {"1111", "1112"}
    assert mapped["1111"].major_group_code == 1
    assert mapped["1111"].major_group_title == "Major One"
    assert mapped["1111"].title == "Official title"


def test_duplicate_occupation_region_is_rejected_with_stable_redacted_issue(tmp_path):
    estimate, cv, occupations, estimate_rows, cv_rows = _fixture_files(tmp_path)
    estimate_rows.insert(1, estimate_rows[0])
    cv_rows.insert(1, cv_rows[0])
    _write_source_workbook(estimate, estimate_rows)
    _write_source_workbook(cv, cv_rows)
    parsed = _parse_fixture(estimate, cv, occupations)
    assert parsed.quality.rows_seen == 5
    assert parsed.quality.rows_accepted == 4
    assert parsed.quality.rows_rejected == 1
    assert parsed.quality.rejected_rows[0].reason_codes == ("duplicate_occupation_region",)
    assert all("London" not in issue.message for issue in parsed.quality.issues)


def test_unknown_occupation_code_is_rejected_without_echoing_source_content(tmp_path):
    estimate, cv, occupations, estimate_rows, cv_rows = _fixture_files(tmp_path)
    estimate_rows[0] = _data_row("London", "'9999", 32_000.0)
    cv_rows[0] = _data_row("London", "'9999", 5.0)
    _write_source_workbook(estimate, estimate_rows)
    _write_source_workbook(cv, cv_rows)
    parsed = _parse_fixture(estimate, cv, occupations)
    assert "unknown_occupation_code" in parsed.quality.rejected_rows[0].reason_codes
    assert all("9999" not in issue.message for issue in parsed.quality.issues)


@pytest.mark.parametrize(
    ("value", "expected_code"),
    [
        (0, "non_positive_salary"),
        (-1, "non_positive_salary"),
        ("0", "non_positive_salary"),
        ("-1", "non_positive_salary"),
        ("32000", "invalid_salary_value"),
        ("NaN", "non_finite_salary"),
        ("Infinity", "non_finite_salary"),
        ("-Infinity", "non_finite_salary"),
    ],
)
def test_invalid_numeric_salary_values_are_rejected(value, expected_code, tmp_path):
    estimate, cv, occupations, estimate_rows, cv_rows = _fixture_files(tmp_path)
    estimate_rows[0] = _data_row("London", "'1111", value)
    _write_source_workbook(estimate, estimate_rows)
    parsed = _parse_fixture(estimate, cv, occupations)
    assert parsed.quality.rows_rejected == 1
    assert expected_code in parsed.quality.rejected_rows[0].reason_codes
    assert all(str(value) not in issue.message for issue in parsed.quality.issues)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_python_numeric_values_are_rejected(value):
    status, amount, raw_cell, error = classify_source_cell(value)
    assert status is None and amount is None
    assert error == "non_finite_salary"


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), "invalid"])
def test_cv_validation_rejects_invalid_values(value):
    _, _, error = parse_cv_cell(value)
    assert error == "invalid_cv"


def test_reported_salary_requires_valid_cv_and_quality_suppression_consistency(tmp_path):
    estimate, cv, occupations, _, cv_rows = _fixture_files(tmp_path)
    cv_rows[0] = _data_row("London", "'1111", 20.1)
    _write_source_workbook(cv, cv_rows)
    parsed = _parse_fixture(estimate, cv, occupations)
    assert parsed.quality.rows_rejected == 1
    assert "reported_cv_missing_or_above_threshold" in parsed.quality.rejected_rows[0].reason_codes


def test_expected_grid_checks_codes_regions_and_unique_keys(tmp_path):
    estimate, cv, occupations, _, _ = _fixture_files(tmp_path)
    parsed = _parse_fixture(estimate, cv, occupations)
    validate_expected_grid(
        parsed.records,
        occupations,
        expected_codes=2,
        expected_regions=("London", "Wales"),
        expected_rows=4,
    )
    with pytest.raises(PipelineError, match="occupation codes"):
        validate_expected_grid(parsed.records, occupations, expected_codes=3,
                               expected_regions=("London", "Wales"), expected_rows=4)


def test_provenance_generation_reuses_sprint1_contract_and_keeps_review_status():
    before = get_source("uk.ons.ashe")
    provenance = build_data_provenance(INGESTED_AT)
    after = get_source("uk.ons.ashe")
    assert provenance.source_id == "uk.ons.ashe"
    assert provenance.collected_at == INGESTED_AT
    assert provenance.reference_period == "2025"
    assert provenance.validation_status == ValidationStatus.VALIDATED
    assert before.reuse_review_status == after.reuse_review_status == ReuseReviewStatus.REVIEW_REQUIRED
    assert before.validation_status == after.validation_status == ValidationStatus.NOT_COLLECTED


def test_manifest_contract_records_review_gate_checksum_and_validation():
    quality = DataQualityResult(rows_seen=1, rows_accepted=1, rows_rejected=0)
    provenance = build_data_provenance(INGESTED_AT)
    manifest = ASHERunManifest(
        run_id="fixture-run",
        source_id="uk.ons.ashe",
        source_reuse_review_status=ReuseReviewStatus.REVIEW_REQUIRED,
        processing_mode="LOCAL_PREPARATION_ONLY",
        source_reference=SOURCE_REFERENCE,
            source_attribution="ONS ASHE 2025 revised, OGL v3.0",
        catalog_source_reference="https://example.test/registry-source",
        source_reference_matches_catalog=False,
        ingested_at=INGESTED_AT,
        dataset_version="2025 revised",
        source_reference_period="Tax year ending 5 April 2025",
        archive_filename="fixture.zip",
        archive_size_bytes=1,
        archive_sha256=ARCHIVE_SHA,
        archive_checksum_verified=True,
        archive_member_count=46,
        extracted_workbook_count=44,
        estimate_workbook_filename="estimate.xlsx",
        estimate_workbook_sha256=ESTIMATE_SHA,
        cv_workbook_filename="cv.xlsx",
        cv_workbook_sha256=CV_SHA,
        classification_reference_filename="soc.xlsx",
        classification_reference_sha256=SOC_SHA,
        transformation_version=TRANSFORMATION_VERSION,
        occupation_classification="SOC 2020",
        occupation_codes_verified=412,
        geography_level="GB work regions",
        geographic_coverage=("London", "Wales"),
        selected_sheet="Full-Time",
        selected_measure="Table 15.7a Annual pay - Gross; Median",
        selected_variables=("Description", "Code", "Median", "CV Median"),
        workbook_data_rows_scanned=1,
        non_data_rows_classified=0,
        source_numeric_percentile_cells=0,
        validation_result=quality,
        value_status_counts={"REPORTED": 1},
        validation_summary={},
        data_provenance=provenance,
        processed_dataset_filename="data.csv",
        processed_dataset_sha256="E" * 64,
        quality_report_filename="quality_report.md",
    )
    manifest_json = json.dumps(manifest.model_dump(mode="json"), sort_keys=True)
    assert '"source_reuse_review_status": "REVIEW_REQUIRED"' in manifest_json
    assert '"publication_eligible": false' in manifest_json
    assert '"archive_checksum_verified": true' in manifest_json


def test_dataset_serialization_is_deterministic_and_count_summary_is_exact(tmp_path):
    estimate, cv, occupations, _, _ = _fixture_files(tmp_path)
    parsed = _parse_fixture(estimate, cv, occupations)
    first = serialize_dataset(parsed.records)
    second = serialize_dataset(tuple(reversed(parsed.records)))
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()
    assert count_value_statuses(parsed.records) == {
        "BLANK_UNKNOWN": 1,
        "REPORTED": 2,
        "SUPPRESSED_QUALITY": 1,
    }


@pytest.mark.skipif(
    not (DEFAULT_ARCHIVE.is_file() and DEFAULT_EXTRACTED.is_dir() and DEFAULT_SOC_REFERENCE.is_file()),
    reason="local ONS source assets are ignored and are not required for CI unit tests",
)
def test_verified_source_reproduces_archive_grid_and_quality_counts():
    assets = verify_archive_layout(
        DEFAULT_ARCHIVE, DEFAULT_EXTRACTED, DEFAULT_SOC_REFERENCE,
        expected_archive_sha256=EXPECTED_ARCHIVE_SHA256,
    )
    occupations = load_occupation_reference(assets.soc_path)
    assert assets.archive_sha256 == EXPECTED_ARCHIVE_SHA256
    assert assets.extracted_workbook_count == 44
    parsed = parse_workbook_pair(
        assets.estimate_path,
        assets.cv_path,
        occupations,
        run_id="ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1",
        archive_sha256=assets.archive_sha256,
        estimate_filename=assets.estimate_path.name,
        estimate_sha256=assets.estimate_sha256,
        cv_filename=assets.cv_path.name,
        cv_sha256=assets.cv_sha256,
        classification_filename=assets.soc_path.name,
        classification_sha256=assets.soc_sha256,
        catalog_source_reference="https://example.test/catalog-source",
    )
    assert parsed.quality.rows_seen == EXPECTED_RECORDS
    assert parsed.quality.rows_accepted == EXPECTED_RECORDS
    assert parsed.quality.rows_rejected == 0
    assert parsed.source_numeric_percentile_cells == 0
    assert parsed.value_status_counts == {
        "BLANK_UNKNOWN": EXPECTED_BLANK,
        "REPORTED": EXPECTED_NUMERIC,
        "SUPPRESSED_QUALITY": EXPECTED_SUPPRESSED,
    }
    assert len(occupations) == EXPECTED_CODES
    assert {record.occupation_code for record in parsed.records} == set(occupations)
    assert {record.geography_label for record in parsed.records} == set(EXPECTED_REGIONS)
    assert len({(record.geography_label, record.occupation_code) for record in parsed.records}) == EXPECTED_RECORDS
    validate_expected_grid(parsed.records, occupations)


def test_invalid_pydantic_salary_and_cv_values_fail_contract():
    with pytest.raises(ValidationError):
        from src.backend.ingestion.contracts import ASHEAggregateRecord

        ASHEAggregateRecord.model_validate({
            "observation_id": "ashe25r-aaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb",
            "run_id": "fixture-run",
            "occupation_code": "1111",
            "occupation_description": "Example occupation",
            "official_occupation_title": "Official occupation",
            "source_occupation_code": "'1111",
            "major_group_code": 1,
            "major_group_title": "Managers",
            "geography_label": "London",
            "source_description": "London, Example occupation",
            "salary_value": Decimal("NaN"),
            "original_ons_median_cell": "NaN",
            "original_ons_cv": Decimal("-1"),
            "original_ons_cv_cell": "-1",
            "cv_quality_band": "INVALID",
            "value_status": "REPORTED",
            "source_archive_sha256": ARCHIVE_SHA,
            "source_estimate_workbook": "estimate.xlsx",
            "source_estimate_sha256": ESTIMATE_SHA,
            "source_cv_workbook": "cv.xlsx",
            "source_cv_sha256": CV_SHA,
            "classification_reference_file": "soc.xlsx",
            "classification_reference_sha256": SOC_SHA,
            "source_reference": SOURCE_REFERENCE,
            "catalog_source_reference": "https://example.test/registry-source",
            "source_reference_matches_catalog": False,
            "source_attribution": "ONS ASHE 2025 revised, OGL v3.0",
            "transformation_version": TRANSFORMATION_VERSION,
        })
