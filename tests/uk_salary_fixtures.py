from __future__ import annotations

import hashlib
import json
import csv
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from src.backend.data_catalog.registry import get_source
from src.backend.ingestion.contracts import ASHEAggregateRecord, ASHEValueStatus
from src.backend.ingestion.runner import serialize_dataset
from src.backend.schemas.data import DataProvenance, DataQualityResult, ValidationStatus
from src.backend.schemas.uk_salary import UKWorkRegion
from src.backend.services.uk_salary_service import (
    EXPECTED_ARCHIVE_SHA256,
    EXPECTED_REGIONS,
    REFERENCE_PERIOD,
    SOURCE_ATTRIBUTION,
    SOURCE_ID,
    SOURCE_REFERENCE,
    TRANSFORMATION_VERSION,
    UKSalaryService,
)

FIXTURE_CODE = "1001"
FIXTURE_TITLE = "Data analysts"
FIXTURE_OCCUPATION_DESCRIPTION = "Data analysts"
FIXTURE_RUN_ID = f"ashe25r-{EXPECTED_ARCHIVE_SHA256[:16].lower()}-{TRANSFORMATION_VERSION}"
CATALOG_SOURCE_REFERENCE = str(get_source(SOURCE_ID).source_reference)


def make_records(occupation_codes: tuple[str, ...] = (FIXTURE_CODE,)) -> tuple[ASHEAggregateRecord, ...]:
    records = []
    row_number = 0
    for code in occupation_codes:
        for index, region in enumerate(EXPECTED_REGIONS):
            row_number += 1
            if index == 0:
                status = ASHEValueStatus.REPORTED
                amount = Decimal("45000")
                median_cell = "45000"
                cv = Decimal("5")
                cv_cell = "5"
                quality_band = "CV_LE_5"
            elif index == 1:
                status = ASHEValueStatus.SUPPRESSED_QUALITY
                amount = None
                median_cell = "x"
                cv = None
                cv_cell = "x"
                quality_band = "CV_GT_20_SUPPRESSED"
            else:
                status = ASHEValueStatus.BLANK_UNKNOWN
                amount = None
                median_cell = ""
                cv = None
                cv_cell = None
                quality_band = "CV_BLANK_UNKNOWN"

            records.append(ASHEAggregateRecord(
                observation_id=f"ashe25r-{EXPECTED_ARCHIVE_SHA256[:16].lower()}-{row_number:016x}",
                run_id=FIXTURE_RUN_ID,
                occupation_code=code,
                occupation_description=FIXTURE_OCCUPATION_DESCRIPTION,
                official_occupation_title=FIXTURE_TITLE,
                source_occupation_code=f"'{code}",
                major_group_code=1,
                major_group_title="Managers, directors and senior officials",
                geography_label=region.value,
                source_description=f"{region.value}, {FIXTURE_OCCUPATION_DESCRIPTION}",
                salary_value=amount,
                original_ons_median_cell=median_cell,
                original_ons_cv=cv,
                original_ons_cv_cell=cv_cell,
                cv_quality_band=quality_band,
                value_status=status,
                source_archive_sha256=EXPECTED_ARCHIVE_SHA256,
                source_estimate_workbook="estimate.xlsx",
                source_estimate_sha256="A" * 64,
                source_cv_workbook="cv.xlsx",
                source_cv_sha256="B" * 64,
                classification_reference_file="soc2020.xlsx",
                classification_reference_sha256="C" * 64,
                source_reference=SOURCE_REFERENCE,
                catalog_source_reference=CATALOG_SOURCE_REFERENCE,
                source_reference_matches_catalog=SOURCE_REFERENCE == CATALOG_SOURCE_REFERENCE,
                source_attribution=SOURCE_ATTRIBUTION,
                transformation_version=TRANSFORMATION_VERSION,
            ))
    return tuple(records)


def make_manifest(dataset_path: Path, records: tuple[ASHEAggregateRecord, ...]) -> dict:
    statuses = Counter(record.value_status.value for record in records)
    dataset_sha = hashlib.sha256(serialize_dataset(records)).hexdigest().upper()
    return {
        "run_id": FIXTURE_RUN_ID,
        "source_id": SOURCE_ID,
        "source_reuse_review_status": "REVIEW_REQUIRED",
        "processing_mode": "LOCAL_PREPARATION_ONLY",
        "publication_eligible": False,
        "source_reference": SOURCE_REFERENCE,
        "catalog_source_reference": CATALOG_SOURCE_REFERENCE,
        "source_reference_matches_catalog": SOURCE_REFERENCE == CATALOG_SOURCE_REFERENCE,
        "source_attribution": SOURCE_ATTRIBUTION,
        "ingested_at": "2026-11-12T00:00:00Z",
        "dataset_version": "2025 revised",
        "source_reference_period": REFERENCE_PERIOD,
        "archive_filename": "source.zip",
        "archive_size_bytes": 100,
        "archive_sha256": EXPECTED_ARCHIVE_SHA256,
        "archive_checksum_verified": True,
        "archive_member_count": 46,
        "extracted_workbook_count": 44,
        "estimate_workbook_filename": "estimate.xlsx",
        "estimate_workbook_sha256": "A" * 64,
        "cv_workbook_filename": "cv.xlsx",
        "cv_workbook_sha256": "B" * 64,
        "classification_reference_filename": "soc2020.xlsx",
        "classification_reference_sha256": "C" * 64,
        "transformation_version": TRANSFORMATION_VERSION,
        "occupation_classification": "SOC 2020",
        "occupation_codes_verified": len({record.occupation_code for record in records}),
        "geography_level": "GB work regions",
        "geographic_coverage": [region.value for region in EXPECTED_REGIONS],
        "selected_sheet": "Full-Time",
        "selected_measure": "Table 15.7a Annual pay - Gross; Median",
        "selected_variables": ["Description", "Code", "Median", "CV Median"],
        "workbook_data_rows_scanned": len(records),
        "non_data_rows_classified": 0,
        "source_numeric_percentile_cells": 0,
        "validation_result": {
            "rows_seen": len(records),
            "rows_accepted": len(records),
            "rows_rejected": 0,
            "issues": [],
            "rejected_rows": [],
        },
        "value_status_counts": dict(statuses),
        "validation_summary": {},
        "data_provenance": DataProvenance(
            source_id=SOURCE_ID,
            collected_at=datetime(2026, 11, 12, tzinfo=timezone.utc),
            reference_period="2025",
            geographic_coverage=tuple(region.value for region in EXPECTED_REGIONS),
            dataset_description="Synthetic ASHE fixture for isolated service tests.",
            validation_status=ValidationStatus.VALIDATED,
        ).model_dump(mode="json"),
        "processed_dataset_filename": dataset_path.name,
        "processed_dataset_sha256": dataset_sha,
        "quality_report_filename": "quality_report.md",
    }


def make_publishable_manifest(dataset_path: Path, manifest: dict) -> dict:
    """Rewrite only a temporary fixture to a matching identity; grants no real permission."""
    with dataset_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    for row in rows:
        row["source_reference"] = SOURCE_REFERENCE
        row["catalog_source_reference"] = SOURCE_REFERENCE
        row["source_reference_matches_catalog"] = "True"
    with dataset_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    result = dict(manifest)
    dataset_sha256 = hashlib.sha256(dataset_path.read_bytes()).hexdigest().upper()
    result.update({
        "processing_mode": "PUBLICATION_APPROVED",
        "publication_eligible": True,
        "source_reuse_review_status": "APPROVED",
        "catalog_validation_status": "VALIDATED",
        "source_reference": SOURCE_REFERENCE,
        "catalog_source_reference": SOURCE_REFERENCE,
        "source_reference_matches_catalog": True,
        "processed_dataset_sha256": dataset_sha256,
    })
    provenance = dict(result["data_provenance"])
    provenance.update({
        "source_reference": SOURCE_REFERENCE,
        "catalog_source_reference": SOURCE_REFERENCE,
        "source_reference_matches_catalog": True,
    })
    result["data_provenance"] = provenance
    result["publication_approval"] = {
        "approval_id": "synthetic-test-approval",
        "approved_by": "synthetic-test-fixture",
        "approved_at": "2026-11-12T00:00:00Z",
        "source_id": SOURCE_ID,
        "source_reference": SOURCE_REFERENCE,
        "catalog_source_reference": SOURCE_REFERENCE,
        "source_reference_matches_catalog": True,
        "source_reuse_review_status": "APPROVED",
        "catalog_validation_status": "VALIDATED",
        "approved_dataset_sha256": dataset_sha256,
        "approved_uses": ["public_salary_display"],
    }
    return result


def write_fixture(tmp_path: Path, records: tuple[ASHEAggregateRecord, ...] | None = None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    actual_records = records or make_records()
    dataset_path = tmp_path / "ashe_fixture.csv"
    manifest_path = tmp_path / "provenance_manifest.json"
    dataset_bytes = serialize_dataset(actual_records)
    dataset_path.write_bytes(dataset_bytes)
    manifest = make_manifest(dataset_path, actual_records)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    service = make_service(dataset_path, manifest_path, actual_records)
    return dataset_path, manifest_path, manifest, actual_records, service


def make_service(dataset_path, manifest_path, records, *, expected_csv_sha256=None):
    if expected_csv_sha256 is None and dataset_path.exists():
        actual_hash = hashlib.sha256(dataset_path.read_bytes()).hexdigest().upper()
    elif expected_csv_sha256 is None and manifest_path.exists():
        actual_hash = json.loads(manifest_path.read_text(encoding="utf-8"))["processed_dataset_sha256"]
    else:
        actual_hash = expected_csv_sha256 or "0" * 64
    expected_status_counts = dict(Counter(record.value_status.value for record in records))
    return UKSalaryService(
        dataset_path,
        manifest_path,
        expected_archive_sha256=EXPECTED_ARCHIVE_SHA256,
        expected_csv_sha256=actual_hash,
        expected_regions=EXPECTED_REGIONS,
        expected_occupation_count=len({record.occupation_code for record in records}),
        expected_row_count=len(records),
        expected_status_counts=expected_status_counts,
    )
