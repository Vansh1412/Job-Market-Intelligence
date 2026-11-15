from __future__ import annotations

import csv
import hashlib
import json
import logging
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from pydantic import ValidationError

from src.backend.data_catalog.registry import get_source
from src.backend.ingestion.contracts import ASHEAggregateRecord, ASHEValueStatus
from src.backend.schemas.uk_salary import (
    UKCoverage,
    UKOccupationDetail,
    UKOccupationPage,
    UKOccupationSummary,
    UKRegionComparison,
    UKRegionObservation,
    UKRegionOccupationItem,
    UKRegionOccupationPage,
    UKSalaryContext,
    UKSalaryMetadata,
    UKValueStatus,
    UKWorkRegion,
)

logger = logging.getLogger("jobintel.uk_salary")

SOURCE_ID = "uk.ons.ashe"
TRANSFORMATION_VERSION = "ashe-table15-2025r-v1.0.2"
EXPECTED_ARCHIVE_SHA256 = "AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3"
EXPECTED_CSV_SHA256 = "DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E"
REFERENCE_PERIOD = "Tax year ending 5 April 2025"
MEASURE = "Full-time annual gross pay median (ONS Table 15.7a)"
POPULATION_DEFINITION = (
    "Adult-rate full-time employee jobs held for over one year; gross annual earnings "
    "before deductions, under the ONS ASHE definition."
)
SOURCE_ATTRIBUTION = (
    "Source: Office for National Statistics, Annual Survey of Hours and Earnings, "
    "ASHE Table 15, 2025 revised; Open Government Licence v3.0."
)
SOURCE_REFERENCE = (
    "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
    "earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15"
)
EXPECTED_REGIONS = tuple(UKWorkRegion)
EXPECTED_STATUS_COUNTS = {
    "REPORTED": 1339,
    "SUPPRESSED_QUALITY": 2818,
    "BLANK_UNKNOWN": 375,
}
LOCAL_PREPARATION_MODE = "LOCAL_PREPARATION_ONLY"
PUBLICATION_APPROVED_MODE = "PUBLICATION_APPROVED"
PUBLIC_DASHBOARD_USE = "public_salary_display"

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = (
    REPO_ROOT
    / "data/processed/ashe_2025_revised/"
    "ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1.0.2/"
    "ashe_2025_full_time_annual_gross_median_gb.csv"
)
DEFAULT_MANIFEST_PATH = DEFAULT_DATASET_PATH.parent / "provenance_manifest.json"


class UKSalaryServiceError(RuntimeError):
    """Safe, stable service failure; message is suitable for server logs only."""

    def __init__(self, code: str, public_code: str = "UK_DATA_UNAVAILABLE") -> None:
        self.code = code
        self.public_code = public_code
        super().__init__(code)


class UKSalaryNotFound(LookupError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class UKSalaryCell:
    """Compact validated service record; source-only columns are discarded after checks."""

    occupation_code: str
    occupation_description: str
    official_occupation_title: str
    major_group_code: int
    major_group_title: str
    region_label: str
    salary_value: Decimal | None
    original_ons_median_cell: str
    original_ons_cv: Decimal | None
    original_ons_cv_cell: str | None
    cv_quality_band: str
    value_status: ASHEValueStatus


def has_valid_publication_approval(manifest: dict[str, Any]) -> bool:
    """Check the explicit approval record shape; this does not validate the data file."""
    approval = manifest.get("publication_approval")
    provenance = manifest.get("data_provenance")
    validation = manifest.get("validation_result")
    geography = [region.value for region in EXPECTED_REGIONS]
    status_counts = manifest.get("value_status_counts")
    if not isinstance(approval, dict):
        return False
    if not isinstance(provenance, dict) or not isinstance(validation, dict):
        return False
    if (
        manifest.get("processing_mode") != PUBLICATION_APPROVED_MODE
        or manifest.get("publication_eligible") is not True
        or manifest.get("source_reuse_review_status") != "APPROVED"
        or manifest.get("catalog_validation_status") != "VALIDATED"
        or manifest.get("source_id") != SOURCE_ID
        or manifest.get("source_reference") != SOURCE_REFERENCE
        or manifest.get("catalog_source_reference") != SOURCE_REFERENCE
        or manifest.get("source_reference_matches_catalog") is not True
        or manifest.get("transformation_version") != TRANSFORMATION_VERSION
        or manifest.get("dataset_version") != "2025 revised"
        or manifest.get("source_reference_period") != REFERENCE_PERIOD
        or manifest.get("occupation_classification") != "SOC 2020"
        or manifest.get("geography_level") != "GB work regions"
        or manifest.get("archive_checksum_verified") is not True
        or manifest.get("archive_sha256") != EXPECTED_ARCHIVE_SHA256
        or not isinstance(validation.get("rows_seen"), int)
        or validation.get("rows_seen") != validation.get("rows_accepted")
        or validation.get("rows_rejected") != 0
        or not isinstance(status_counts, dict)
        or any(not isinstance(count, int) or count < 0 for count in status_counts.values())
        or sum(status_counts.values()) != validation.get("rows_accepted")
        or manifest.get("geographic_coverage") != geography
        or provenance.get("source_id") != SOURCE_ID
        or provenance.get("reference_period") != "2025"
        or provenance.get("validation_status") != "VALIDATED"
        or provenance.get("geographic_coverage") != geography
        or provenance.get("source_reference") != SOURCE_REFERENCE
        or provenance.get("catalog_source_reference") != SOURCE_REFERENCE
        or provenance.get("source_reference_matches_catalog") is not True
        or approval.get("source_id") != SOURCE_ID
        or approval.get("source_reference") != SOURCE_REFERENCE
        or approval.get("catalog_source_reference") != SOURCE_REFERENCE
        or approval.get("source_reference_matches_catalog") is not True
        or approval.get("source_reuse_review_status") != "APPROVED"
        or approval.get("catalog_validation_status") != "VALIDATED"
        or not isinstance(approval.get("approval_id"), str)
        or not approval["approval_id"].strip()
        or not isinstance(approval.get("approved_by"), str)
        or not approval["approved_by"].strip()
        or approval.get("approved_dataset_sha256") != manifest.get("processed_dataset_sha256")
    ):
        return False
    approved_uses = approval.get("approved_uses")
    if not isinstance(approved_uses, list) or PUBLIC_DASHBOARD_USE not in approved_uses:
        return False
    try:
        approved_at = datetime.fromisoformat(str(approval.get("approved_at", "")).replace("Z", "+00:00"))
    except ValueError:
        return False
    return approved_at.utcoffset() is not None


def approved_dataset_checksum_matches(manifest: dict[str, Any], dataset_path: Path) -> bool:
    """Recheck approved bytes on each API request so cached indexes cannot outlive approval data."""
    expected = manifest.get("processed_dataset_sha256")
    approval = manifest.get("publication_approval")
    if (
        not isinstance(expected, str)
        or not isinstance(approval, dict)
        or len(expected) != 64
        or any(character not in "0123456789ABCDEF" for character in expected)
        or expected != approval.get("approved_dataset_sha256")
    ):
        return False
    try:
        return _sha256_file(dataset_path) == expected
    except UKSalaryServiceError:
        return False


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise UKSalaryServiceError("uk_dataset_missing") from exc
    except OSError as exc:
        raise UKSalaryServiceError("uk_dataset_unreadable") from exc
    return digest.hexdigest().upper()


def _decimal_or_none(value: str | None, field: str) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise UKSalaryServiceError(f"uk_invalid_{field}") from exc
    if not result.is_finite():
        raise UKSalaryServiceError(f"uk_non_finite_{field}")
    return result


def _csv_bool(value: str, field: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise UKSalaryServiceError(f"uk_invalid_{field}")


class UKSalaryService:
    """Read-only, checksum-pinned index over the prepared ASHE source cells."""

    def __init__(
        self,
        dataset_path: Path = DEFAULT_DATASET_PATH,
        manifest_path: Path = DEFAULT_MANIFEST_PATH,
        *,
        expected_archive_sha256: str = EXPECTED_ARCHIVE_SHA256,
        expected_csv_sha256: str = EXPECTED_CSV_SHA256,
        expected_regions: tuple[UKWorkRegion, ...] = EXPECTED_REGIONS,
        expected_occupation_count: int = 412,
        expected_row_count: int = 4532,
        expected_status_counts: dict[str, int] | None = None,
    ) -> None:
        started = time.perf_counter()
        self._dataset_path = dataset_path
        self._manifest_path = manifest_path
        self._expected_archive_sha256 = expected_archive_sha256
        self._expected_csv_sha256 = expected_csv_sha256
        self._expected_regions = expected_regions
        self._expected_occupation_count = expected_occupation_count
        self._expected_row_count = expected_row_count
        self._expected_status_counts = expected_status_counts or EXPECTED_STATUS_COUNTS

        manifest = self._read_manifest(self._manifest_path)
        self._validate_manifest(manifest)
        self._manifest = MappingProxyType(manifest)
        actual_csv_sha256 = _sha256_file(self._dataset_path)
        if actual_csv_sha256 != self._expected_csv_sha256:
            raise UKSalaryServiceError("uk_checksum_mismatch")
        if actual_csv_sha256 != manifest.get("processed_dataset_sha256"):
            raise UKSalaryServiceError("uk_manifest_checksum_mismatch")

        records = self._read_and_validate_rows()
        self._records: tuple[UKSalaryCell, ...] = tuple(records)
        self._by_code = self._index_by_code(self._records)
        self._by_region = self._index_by_region(self._records)
        self._context = self._make_context()
        self._load_duration_ms = (time.perf_counter() - started) * 1000.0
        logger.info("UK ASHE dataset validated and indexed; rows=%d", len(self._records))

    @property
    def load_duration_ms(self) -> float:
        return self._load_duration_ms

    @property
    def row_count(self) -> int:
        return len(self._records)

    @staticmethod
    def _read_manifest(path: Path | None = None) -> dict[str, Any]:
        manifest_path = path or DEFAULT_MANIFEST_PATH
        try:
            with manifest_path.open("r", encoding="utf-8") as stream:
                result = json.load(stream)
        except FileNotFoundError as exc:
            raise UKSalaryServiceError("uk_manifest_missing") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise UKSalaryServiceError("uk_manifest_invalid") from exc
        if not isinstance(result, dict):
            raise UKSalaryServiceError("uk_manifest_invalid")
        return result

    def _validate_manifest(self, manifest: dict[str, Any]) -> None:
        required = {
            "source_id": SOURCE_ID,
            "transformation_version": TRANSFORMATION_VERSION,
            "dataset_version": "2025 revised",
            "source_reference_period": REFERENCE_PERIOD,
            "occupation_classification": "SOC 2020",
            "geography_level": "GB work regions",
            "selected_sheet": "Full-Time",
            "selected_measure": "Table 15.7a Annual pay - Gross; Median",
            "archive_checksum_verified": True,
            "archive_sha256": self._expected_archive_sha256,
            "processed_dataset_filename": self._dataset_path.name,
            "extracted_workbook_count": 44,
            "occupation_codes_verified": self._expected_occupation_count,
        }
        if any(manifest.get(key) != value for key, value in required.items()):
            raise UKSalaryServiceError("uk_manifest_contract_mismatch")
        if manifest.get("source_reference") != SOURCE_REFERENCE:
            raise UKSalaryServiceError("uk_manifest_source_reference_mismatch")
        try:
            source = get_source(SOURCE_ID)
            source_id = source.source_id
            live_catalog_reference = str(source.source_reference) if source.source_reference is not None else None
        except Exception as exc:
            raise UKSalaryServiceError("uk_source_unregistered") from exc
        manifest_catalog_reference = manifest.get("catalog_source_reference")
        source_reference_matches_catalog = manifest.get("source_reference_matches_catalog")
        if source_id != SOURCE_ID or not live_catalog_reference:
            raise UKSalaryServiceError("uk_source_unregistered")
        if manifest_catalog_reference != live_catalog_reference:
            raise UKSalaryServiceError("uk_manifest_catalog_reference_mismatch")
        expected_reference_match = SOURCE_REFERENCE == manifest_catalog_reference
        if source_reference_matches_catalog is not expected_reference_match:
            raise UKSalaryServiceError("uk_manifest_reference_match_flag_invalid")
        processing_mode = manifest.get("processing_mode")
        if processing_mode == LOCAL_PREPARATION_MODE:
            if (
                manifest.get("publication_eligible") is not False
                or manifest.get("source_reuse_review_status") != "REVIEW_REQUIRED"
                or manifest.get("catalog_validation_status") not in (None, "NOT_COLLECTED")
                or manifest.get("publication_approval") not in (None, {})
            ):
                raise UKSalaryServiceError("uk_manifest_publication_state_mismatch")
        elif processing_mode == PUBLICATION_APPROVED_MODE:
            if not has_valid_publication_approval(manifest):
                raise UKSalaryServiceError("uk_manifest_publication_approval_invalid")
        else:
            raise UKSalaryServiceError("uk_manifest_processing_mode_invalid")
        if not isinstance(manifest.get("ingested_at"), str):
            raise UKSalaryServiceError("uk_manifest_timestamp_missing")
        try:
            ingested_at = datetime.fromisoformat(manifest["ingested_at"].replace("Z", "+00:00"))
            if ingested_at.utcoffset() is None:
                raise ValueError
        except (TypeError, ValueError) as exc:
            raise UKSalaryServiceError("uk_manifest_timestamp_invalid") from exc

        coverage = manifest.get("geographic_coverage")
        if coverage != [region.value for region in self._expected_regions]:
            raise UKSalaryServiceError("uk_manifest_geography_mismatch")
        validation = manifest.get("validation_result")
        if not isinstance(validation, dict):
            raise UKSalaryServiceError("uk_manifest_validation_missing")
        if (
            validation.get("rows_seen") != self._expected_row_count
            or validation.get("rows_accepted") != self._expected_row_count
            or validation.get("rows_rejected") != 0
        ):
            raise UKSalaryServiceError("uk_manifest_validation_mismatch")
        if manifest.get("value_status_counts") != self._expected_status_counts:
            raise UKSalaryServiceError("uk_manifest_status_counts_mismatch")
        provenance = manifest.get("data_provenance")
        if not isinstance(provenance, dict) or (
            provenance.get("source_id") != SOURCE_ID
            or provenance.get("reference_period") != "2025"
            or provenance.get("validation_status") != "VALIDATED"
            or provenance.get("geographic_coverage") != coverage
        ):
            raise UKSalaryServiceError("uk_manifest_provenance_mismatch")
        if processing_mode == PUBLICATION_APPROVED_MODE and (
            provenance.get("source_reference") != SOURCE_REFERENCE
            or provenance.get("catalog_source_reference") != SOURCE_REFERENCE
            or provenance.get("source_reference_matches_catalog") is not True
        ):
            raise UKSalaryServiceError("uk_manifest_provenance_mismatch")

    def _read_and_validate_rows(self) -> list[UKSalaryCell]:
        records: list[UKSalaryCell] = []
        try:
            with self._dataset_path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames != self._expected_columns():
                    raise UKSalaryServiceError("uk_schema_invalid")
                for row_number, raw in enumerate(reader, start=2):
                    if None in raw or any(value is None for value in raw.values()):
                        raise UKSalaryServiceError("uk_row_schema_invalid")
                    try:
                        payload: dict[str, Any] = dict(raw)
                        payload["salary_value"] = _decimal_or_none(raw["salary_value"], "salary")
                        payload["original_ons_cv"] = _decimal_or_none(raw["original_ons_cv"], "cv")
                        payload["original_ons_cv_cell"] = raw["original_ons_cv_cell"] or None
                        payload["geography_code"] = None
                        payload["major_group_code"] = int(raw["major_group_code"])
                        payload["source_reference_matches_catalog"] = _csv_bool(
                            raw["source_reference_matches_catalog"], "catalog_match"
                        )
                        record = ASHEAggregateRecord.model_validate(payload)
                    except (ValueError, ValidationError, UKSalaryServiceError) as exc:
                        if isinstance(exc, UKSalaryServiceError):
                            raise
                        raise UKSalaryServiceError("uk_row_invalid") from exc
                    self._validate_row(record, row_number)
                    records.append(UKSalaryCell(
                        occupation_code=record.occupation_code,
                        occupation_description=record.occupation_description,
                        official_occupation_title=record.official_occupation_title,
                        major_group_code=record.major_group_code,
                        major_group_title=record.major_group_title,
                        region_label=record.geography_label,
                        salary_value=record.salary_value,
                        original_ons_median_cell=record.original_ons_median_cell,
                        original_ons_cv=record.original_ons_cv,
                        original_ons_cv_cell=record.original_ons_cv_cell,
                        cv_quality_band=record.cv_quality_band,
                        value_status=record.value_status,
                    ))
        except FileNotFoundError as exc:
            raise UKSalaryServiceError("uk_dataset_missing") from exc
        except OSError as exc:
            raise UKSalaryServiceError("uk_dataset_unreadable") from exc

        if len(records) != self._expected_row_count:
            raise UKSalaryServiceError("uk_row_count_mismatch")
        codes = {record.occupation_code for record in records}
        if len(codes) != self._expected_occupation_count:
            raise UKSalaryServiceError("uk_occupation_count_mismatch")
        keys = {(record.occupation_code, record.region_label) for record in records}
        if len(keys) != self._expected_row_count:
            raise UKSalaryServiceError("uk_duplicate_or_missing_key")
        expected_regions = {region.value for region in self._expected_regions}
        if {record.region_label for record in records} != expected_regions:
            raise UKSalaryServiceError("uk_geography_mismatch")
        if len(keys) != len(codes) * len(expected_regions):
            raise UKSalaryServiceError("uk_incomplete_occupation_region_grid")

        descriptions_by_code: dict[str, tuple[str, str, int, str]] = {}
        for record in records:
            identity = (
                record.official_occupation_title,
                record.occupation_description,
                record.major_group_code,
                record.major_group_title,
            )
            existing = descriptions_by_code.setdefault(record.occupation_code, identity)
            if identity != existing:
                raise UKSalaryServiceError("uk_occupation_metadata_inconsistent")

        counts = Counter(record.value_status.value for record in records)
        if dict(counts) != self._expected_status_counts:
            raise UKSalaryServiceError("uk_status_counts_mismatch")
        if dict(counts) != self._manifest.get("value_status_counts"):
            raise UKSalaryServiceError("uk_manifest_status_counts_mismatch")
        return records

    @staticmethod
    def _expected_columns() -> list[str]:
        from src.backend.ingestion.runner import CSV_FIELDS

        return list(CSV_FIELDS)

    def _validate_row(self, row: ASHEAggregateRecord, row_number: int) -> None:
        if row.source_id != SOURCE_ID:
            raise UKSalaryServiceError("uk_row_source_mismatch")
        if row.transformation_version != TRANSFORMATION_VERSION:
            raise UKSalaryServiceError("uk_row_transformation_mismatch")
        if row.reference_period != REFERENCE_PERIOD:
            raise UKSalaryServiceError("uk_row_reference_period_mismatch")
        if row.classification_id != "SOC" or row.classification_version != "2020":
            raise UKSalaryServiceError("uk_row_classification_mismatch")
        if row.source_archive_sha256 != self._expected_archive_sha256:
            raise UKSalaryServiceError("uk_row_archive_mismatch")
        if row.source_reference != self._manifest.get("source_reference"):
            raise UKSalaryServiceError("uk_row_source_reference_mismatch")
        if row.catalog_source_reference != self._manifest.get("catalog_source_reference"):
            raise UKSalaryServiceError("uk_row_catalog_reference_mismatch")
        if row.source_reference_matches_catalog is not self._manifest.get("source_reference_matches_catalog"):
            raise UKSalaryServiceError("uk_row_reference_match_flag_mismatch")
        if self._manifest.get("processing_mode") == PUBLICATION_APPROVED_MODE and (
            row.source_reference != row.catalog_source_reference
            or row.source_reference_matches_catalog is not True
        ):
            raise UKSalaryServiceError("uk_row_publication_source_reference_mismatch")
        if row.source_estimate_workbook != self._manifest.get("estimate_workbook_filename"):
            raise UKSalaryServiceError("uk_row_estimate_source_mismatch")
        if row.source_estimate_sha256 != self._manifest.get("estimate_workbook_sha256"):
            raise UKSalaryServiceError("uk_row_estimate_checksum_mismatch")
        if row.source_cv_workbook != self._manifest.get("cv_workbook_filename"):
            raise UKSalaryServiceError("uk_row_cv_source_mismatch")
        if row.source_cv_sha256 != self._manifest.get("cv_workbook_sha256"):
            raise UKSalaryServiceError("uk_row_cv_checksum_mismatch")
        if row.classification_reference_sha256 != self._manifest.get("classification_reference_sha256"):
            raise UKSalaryServiceError("uk_row_classification_reference_mismatch")
        if row.value_status == ASHEValueStatus.REPORTED:
            try:
                median_source = Decimal(row.original_ons_median_cell)
            except InvalidOperation as exc:
                raise UKSalaryServiceError("uk_original_median_invalid") from exc
            if median_source != row.salary_value:
                raise UKSalaryServiceError("uk_original_median_mismatch")
        elif row.value_status == ASHEValueStatus.SUPPRESSED_QUALITY:
            if row.original_ons_median_cell != "x" or row.salary_value is not None:
                raise UKSalaryServiceError("uk_suppression_state_mismatch")
        elif row.value_status == ASHEValueStatus.BLANK_UNKNOWN:
            if row.original_ons_median_cell != "" or row.salary_value is not None:
                raise UKSalaryServiceError("uk_blank_state_mismatch")
        elif row.salary_value is not None:
            raise UKSalaryServiceError("uk_unavailable_value_present")

        if row.original_ons_cv is not None:
            try:
                source_cv = Decimal(row.original_ons_cv_cell or "")
            except InvalidOperation as exc:
                raise UKSalaryServiceError("uk_original_cv_invalid") from exc
            if source_cv != row.original_ons_cv:
                raise UKSalaryServiceError("uk_original_cv_mismatch")

    @staticmethod
    def _index_by_code(
        records: tuple[UKSalaryCell, ...],
    ) -> MappingProxyType:
        mutable: dict[str, dict[str, UKSalaryCell]] = {}
        for record in records:
            mutable.setdefault(record.occupation_code, {})[record.region_label] = record
        frozen = {
            code: MappingProxyType(dict(sorted(region_map.items())))
            for code, region_map in mutable.items()
        }
        return MappingProxyType(dict(sorted(frozen.items())))

    @staticmethod
    def _index_by_region(
        records: tuple[UKSalaryCell, ...],
    ) -> MappingProxyType:
        mutable: dict[str, list[UKSalaryCell]] = {region.value: [] for region in EXPECTED_REGIONS}
        for record in records:
            mutable[record.region_label].append(record)
        frozen = {
            region: tuple(sorted(rows, key=lambda item: item.occupation_code))
            for region, rows in mutable.items()
        }
        return MappingProxyType(frozen)

    def _make_context(self) -> UKSalaryContext:
        try:
            source = get_source(SOURCE_ID)
            published = (
                has_valid_publication_approval(dict(self._manifest))
                and str(source.source_reference) == self._manifest.get("source_reference")
                and self._manifest.get("source_reference") == self._manifest.get("catalog_source_reference")
                and self._manifest.get("source_reference_matches_catalog") is True
                and tuple(source.geographic_coverage) == tuple(self._manifest.get("geographic_coverage", ()))
                and source.reference_period == self._manifest.get("data_provenance", {}).get("reference_period")
                and source.reuse_review_status.value == "APPROVED"
                and source.validation_status.value == "VALIDATED"
            )
        except Exception:
            published = False
        return UKSalaryContext(
            reference_period=REFERENCE_PERIOD,
            measure=MEASURE,
            population_definition=POPULATION_DEFINITION,
            occupation_classification="SOC 2020 unit group",
            geography_coverage=self._expected_regions,
            transformation_version=TRANSFORMATION_VERSION,
            data_quality_status="VALIDATED",
            publication_status="PUBLISHED" if published else "NOT_PUBLISHED",
            source_attribution=SOURCE_ATTRIBUTION,
        )

    @staticmethod
    def _to_region_observation(record: UKSalaryCell) -> UKRegionObservation:
        return UKRegionObservation(
            region_label=UKWorkRegion(record.region_label),
            value_status=UKValueStatus(record.value_status.value),
            annual_gross_median_gbp=record.salary_value,
            original_ons_median_cell=record.original_ons_median_cell,
            cv_percent=record.original_ons_cv,
            original_ons_cv_cell=record.original_ons_cv_cell,
            cv_quality_band=record.cv_quality_band,
        )

    @staticmethod
    def _coverage(records: tuple[UKSalaryCell, ...] | list[UKSalaryCell]) -> UKCoverage:
        counts = Counter(record.value_status.value for record in records)
        expected = len(records)
        reported = counts[ASHEValueStatus.REPORTED.value]
        return UKCoverage(
            reported_count=reported,
            suppressed_count=(
                counts[ASHEValueStatus.SUPPRESSED_QUALITY.value]
                + counts[ASHEValueStatus.SUPPRESSED_DISCLOSURE.value]
            ),
            blank_count=(
                counts[ASHEValueStatus.BLANK_UNKNOWN.value]
                + counts[ASHEValueStatus.NOT_APPLICABLE.value]
                + counts[ASHEValueStatus.NIL_OR_NEGLIGIBLE.value]
            ),
            expected_count=expected,
            reported_coverage_ratio=(Decimal(reported) / Decimal(expected)).quantize(Decimal("0.0001")),
        )

    @staticmethod
    def _occupation_summary(
        code: str,
        rows_by_region: MappingProxyType,
    ) -> UKOccupationSummary:
        rows = tuple(rows_by_region[region.value] for region in EXPECTED_REGIONS)
        statuses = Counter(row.value_status.value for row in rows)
        first = rows[0]
        return UKOccupationSummary(
            soc_code=code,
            official_title=first.official_occupation_title,
            source_description=first.occupation_description,
            reported_region_count=statuses[ASHEValueStatus.REPORTED.value],
            suppressed_region_count=statuses[ASHEValueStatus.SUPPRESSED_QUALITY.value],
            blank_region_count=statuses[ASHEValueStatus.BLANK_UNKNOWN.value],
        )

    def list_occupations(self, q: str | None, page: int, page_size: int) -> UKOccupationPage:
        query = q.strip().casefold() if q is not None else ""
        summaries = [
            self._occupation_summary(code, by_region)
            for code, by_region in self._by_code.items()
            if not query
            or query in code.casefold()
            or query in by_region[EXPECTED_REGIONS[0].value].official_occupation_title.casefold()
            or query in by_region[EXPECTED_REGIONS[0].value].occupation_description.casefold()
        ]
        total = len(summaries)
        start = (page - 1) * page_size
        return UKOccupationPage(
            context=self._context,
            items=tuple(summaries[start : start + page_size]),
            page=page,
            page_size=page_size,
            total_count=total,
            has_next=start + page_size < total,
            coverage=self._coverage(self._records),
        )

    def _get_rows_for_code(self, code: str) -> tuple[UKSalaryCell, ...]:
        by_region = self._by_code.get(code)
        if by_region is None:
            raise UKSalaryNotFound("occupation_not_found")
        return tuple(by_region[region.value] for region in EXPECTED_REGIONS)

    def get_occupation(self, code: str) -> UKOccupationDetail:
        rows = self._get_rows_for_code(code)
        return UKOccupationDetail(
            context=self._context,
            occupation=self._occupation_summary(code, self._by_code[code]),
            regions=tuple(self._to_region_observation(row) for row in rows),
            coverage=self._coverage(rows),
        )

    def compare_regions(self, code: str) -> UKRegionComparison:
        rows = self._get_rows_for_code(code)
        summary = self._occupation_summary(code, self._by_code[code])
        reported = summary.reported_region_count
        ratio = (Decimal(reported) / Decimal(len(self._expected_regions))).quantize(Decimal("0.0001"))
        warning = None
        if reported != len(self._expected_regions):
            warning = (
                f"Only {reported} of {len(self._expected_regions)} regions have reportable estimates; "
                "this is not a complete regional comparison."
            )
        return UKRegionComparison(
            context=self._context,
            soc_code=code,
            official_title=summary.official_title,
            observations=tuple(self._to_region_observation(row) for row in rows),
            reported_regions_count=reported,
            coverage_ratio=ratio,
            coverage_warning=warning,
        )

    def list_region_occupations(
        self,
        region: str,
        value_status: UKValueStatus,
        page: int,
        page_size: int,
    ) -> UKRegionOccupationPage:
        try:
            region_enum = UKWorkRegion(region)
        except ValueError as exc:
            raise UKSalaryNotFound("region_not_found") from exc
        all_rows = self._by_region[region_enum.value]
        matching = tuple(row for row in all_rows if row.value_status.value == value_status.value)
        total = len(matching)
        start = (page - 1) * page_size
        items = tuple(
            UKRegionOccupationItem(
                soc_code=row.occupation_code,
                official_title=row.official_occupation_title,
                source_description=row.occupation_description,
                observation=self._to_region_observation(row),
            )
            for row in matching[start : start + page_size]
        )
        return UKRegionOccupationPage(
            context=self._context,
            region_label=region_enum,
            items=items,
            value_status_filter=value_status,
            page=page,
            page_size=page_size,
            total_count=total,
            has_next=start + page_size < total,
            coverage=self._coverage(all_rows),
        )

    def metadata(self) -> UKSalaryMetadata:
        ingested_at = datetime.fromisoformat(str(self._manifest["ingested_at"]).replace("Z", "+00:00"))
        return UKSalaryMetadata(
            context=self._context,
            dataset_version="2025 revised",
            source_reference=SOURCE_REFERENCE,
            source_archive_sha256=self._expected_archive_sha256,
            processed_dataset_sha256=self._expected_csv_sha256,
            occupation_count=len(self._by_code),
            region_count=len(self._by_region),
            observation_count=len(self._records),
            status_counts={UKValueStatus(key): value for key, value in self._expected_status_counts.items()},
            ingested_at=ingested_at,
        )


@lru_cache(maxsize=1)
def get_uk_salary_service() -> UKSalaryService:
    """Lazily load and validate the one approved-versioned artifact per process."""
    return UKSalaryService()
