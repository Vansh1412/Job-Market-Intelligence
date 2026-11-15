from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Iterable

from src.backend.data_catalog.registry import get_source
from src.backend.ingestion.ashe2025 import (
    EXPECTED_REGIONS,
    REFERENCE_PERIOD,
    SOURCE_ATTRIBUTION,
    SOURCE_ID,
    SOURCE_REFERENCE,
    TRANSFORMATION_VERSION,
    ParseResult,
    OccupationReference,
    load_occupation_reference,
    parse_workbook_pair,
    sha256_file,
    summarize_quality,
)
from src.backend.ingestion.contracts import ASHEAggregateRecord, ASHERunManifest, ASHEValueStatus
from src.backend.schemas.data import DataProvenance, ReuseReviewStatus, ValidationStatus


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data/raw/ashe_table15_2025_revised"
DEFAULT_ARCHIVE = DEFAULT_DATA_ROOT / "ashetable152025revised.zip"
DEFAULT_EXTRACTED = DEFAULT_DATA_ROOT / "extracted"
DEFAULT_SOC_REFERENCE = DEFAULT_DATA_ROOT / (
    "soc2020_reference/soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx"
)
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data/processed/ashe_2025_revised"
EXPECTED_ARCHIVE_SHA256 = "AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3"
EXPECTED_SOC_SHA256 = "B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3"
EXPECTED_WORKBOOKS = 44
EXPECTED_RECORDS = 4_532
EXPECTED_CODES = 412
EXPECTED_NUMERIC = 1_339
EXPECTED_SUPPRESSED = 2_818
EXPECTED_BLANK = 375
ESTIMATE_MEMBER = (
    "Table 15 (4)/Work Region Occupation SOC20 (4) Table 15.7a   "
    "Annual pay - Gross 2025.xlsx"
)
CV_MEMBER = (
    "Table 15 (4)/Work Region Occupation SOC20 (4) Table 15.7b   "
    "Annual pay - Gross 2025 CV.xlsx"
)
OUTPUT_FILENAME = "ashe_2025_full_time_annual_gross_median_gb.csv"

CSV_FIELDS = (
    "observation_id", "run_id", "market_id", "occupation_code",
    "occupation_description", "official_occupation_title", "source_occupation_code",
    "classification_id", "classification_version", "major_group_code",
    "major_group_title", "geography_code", "geography_level", "geography_label",
    "source_description", "salary_value", "original_ons_median_cell",
    "original_ons_cv", "original_ons_cv_cell", "cv_quality_band", "value_status",
    "salary_measure_code", "earnings_definition", "statistic", "employee_group",
    "currency", "salary_period", "reference_period", "source_id",
    "source_asset_version", "source_archive_sha256", "source_estimate_workbook",
    "source_estimate_sha256", "source_cv_workbook", "source_cv_sha256",
    "classification_reference_file", "classification_reference_sha256",
    "source_reference", "catalog_source_reference", "source_reference_matches_catalog",
    "source_attribution", "transformation_version",
)


class PipelineError(RuntimeError):
    def __init__(self, code: str, message: str, *, parse_result: ParseResult | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.parse_result = parse_result


@dataclass(frozen=True)
class InputAssets:
    archive_sha256: str
    archive_size_bytes: int
    archive_member_count: int
    extracted_workbook_count: int
    estimate_path: Path
    estimate_sha256: str
    cv_path: Path
    cv_sha256: str
    soc_path: Path
    soc_sha256: str


@dataclass(frozen=True)
class PipelineResult:
    output_directory: Path
    dataset_path: Path
    manifest_path: Path
    quality_report_path: Path
    dataset_sha256: str
    run_id: str
    records_written: int
    reused_existing_output: bool


def verify_archive_layout(
    archive_path: Path,
    extracted_root: Path,
    soc_reference_path: Path,
    *,
    expected_archive_sha256: str = EXPECTED_ARCHIVE_SHA256,
    expected_soc_sha256: str = EXPECTED_SOC_SHA256,
    expected_workbook_count: int = EXPECTED_WORKBOOKS,
) -> InputAssets:
    if not archive_path.is_file() or not extracted_root.is_dir() or not soc_reference_path.is_file():
        raise PipelineError("missing_source_asset", "Required local ASHE source assets are missing.")
    archive_sha = sha256_file(archive_path)
    if archive_sha.casefold() != expected_archive_sha256.casefold():
        raise PipelineError("source_checksum_mismatch", "ASHE archive checksum does not match the verified release.")
    soc_sha = sha256_file(soc_reference_path)
    if soc_sha.casefold() != expected_soc_sha256.casefold():
        raise PipelineError("classification_checksum_mismatch", "SOC reference checksum does not match the verified reference.")

    try:
        with zipfile.ZipFile(archive_path) as archive:
            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise PipelineError("corrupt_archive_member", "ASHE archive integrity check failed.")
            names = archive.namelist()
            workbook_members = {
                PurePosixPath(name).as_posix()
                for name in names
                if not name.endswith("/") and name.casefold().endswith(".xlsx")
            }
            if len(workbook_members) != expected_workbook_count:
                raise PipelineError("unexpected_archive_workbook_count", "ASHE archive workbook count is unexpected.")

            extracted_members = {
                path.relative_to(extracted_root).as_posix()
                for path in extracted_root.rglob("*.xlsx")
                if path.is_file()
            }
            if extracted_members != workbook_members:
                raise PipelineError("extraction_inventory_mismatch", "Extracted workbook inventory does not match the archive.")

            if ESTIMATE_MEMBER not in workbook_members or CV_MEMBER not in workbook_members:
                raise PipelineError("selected_workbook_missing", "Selected annual-pay workbook is absent from the archive.")

            estimate_path = extracted_root.joinpath(*PurePosixPath(ESTIMATE_MEMBER).parts)
            cv_path = extracted_root.joinpath(*PurePosixPath(CV_MEMBER).parts)
            estimate_bytes = archive.read(ESTIMATE_MEMBER)
            cv_bytes = archive.read(CV_MEMBER)
            estimate_hash = hashlib.sha256(estimate_bytes).hexdigest().upper()
            cv_hash = hashlib.sha256(cv_bytes).hexdigest().upper()
            if sha256_file(estimate_path) != estimate_hash or sha256_file(cv_path) != cv_hash:
                raise PipelineError("extracted_workbook_checksum_mismatch", "Extracted workbook bytes differ from the verified archive.")
            archive_size = archive_path.stat().st_size
    except zipfile.BadZipFile as exc:
        raise PipelineError("invalid_archive", "ASHE archive is not a valid ZIP file.") from exc

    return InputAssets(
        archive_sha256=archive_sha,
        archive_size_bytes=archive_size,
        archive_member_count=len(names),
        extracted_workbook_count=len(extracted_members),
        estimate_path=estimate_path,
        estimate_sha256=estimate_hash,
        cv_path=cv_path,
        cv_sha256=cv_hash,
        soc_path=soc_reference_path,
        soc_sha256=soc_sha,
    )


def validate_expected_grid(
    records: Iterable[ASHEAggregateRecord],
    occupations: dict[str, OccupationReference],
    *,
    expected_codes: int = EXPECTED_CODES,
    expected_regions: tuple[str, ...] = EXPECTED_REGIONS,
    expected_rows: int = EXPECTED_RECORDS,
) -> None:
    materialized = tuple(records)
    codes = {record.occupation_code for record in materialized}
    regions = {record.geography_label for record in materialized}
    keys = {(record.geography_label, record.occupation_code) for record in materialized}
    expected_keys = {(region, code) for region in expected_regions for code in occupations}
    if len(occupations) != expected_codes or codes != set(occupations):
        raise PipelineError("unexpected_occupation_count", "Parsed occupation codes do not match the verified SOC 2020 set.")
    if regions != set(expected_regions):
        raise PipelineError("unexpected_region_count", "Parsed work regions do not match the verified coverage.")
    if len(keys) != len(materialized):
        raise PipelineError("duplicate_occupation_region", "Parsed occupation-region keys are duplicated.")
    if len(materialized) != expected_rows or keys != expected_keys:
        raise PipelineError("incomplete_source_grid", "Parsed occupation-region grid is incomplete or unexpected.")


def count_value_statuses(records: Iterable[ASHEAggregateRecord]) -> dict[str, int]:
    return dict(sorted(Counter(record.value_status.value for record in records).items()))


def build_data_provenance(ingested_at: datetime) -> DataProvenance:
    return DataProvenance(
        source_id=SOURCE_ID,
        collected_at=ingested_at,
        reference_period="2025",
        geographic_coverage=EXPECTED_REGIONS,
        dataset_description=(
            "ASHE 2025 revised Table 15 (4), full-time median gross annual pay by "
            "SOC 2020 unit group and Great Britain work region. Local preparation only."
        ),
        validation_status=ValidationStatus.VALIDATED,
    )


def serialize_dataset(records: Iterable[ASHEAggregateRecord]) -> bytes:
    output = __import__("io").StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    for record in sorted(records, key=lambda item: (item.geography_label, item.occupation_code)):
        data = record.model_dump(mode="python")
        row: dict[str, object] = {}
        for name in CSV_FIELDS:
            value = data.get(name)
            if isinstance(value, Decimal):
                value = format(value, "f")
            elif value is None:
                value = ""
            elif hasattr(value, "value"):
                value = value.value
            row[name] = value
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def _source_catalog_reference() -> tuple[str, bool]:
    try:
        source = get_source(SOURCE_ID)
    except KeyError as exc:
        raise PipelineError("unknown_catalog_source", "ASHE source ID is not registered.") from exc
    if source.reuse_review_status != ReuseReviewStatus.REVIEW_REQUIRED:
        raise PipelineError("unexpected_source_review_status", "ASHE source review status changed; preparation is blocked.")
    if source.validation_status != ValidationStatus.NOT_COLLECTED:
        raise PipelineError("unexpected_catalog_validation_status", "ASHE catalog validation state changed; preparation is blocked.")
    return str(source.source_reference), str(source.source_reference) == SOURCE_REFERENCE


def build_quality_report(
    records: tuple[ASHEAggregateRecord, ...],
    *,
    run_id: str,
    dataset_sha256: str,
    source_numeric_percentile_cells: int,
    validation_summary: dict[str, int],
) -> str:
    statuses = Counter(record.value_status.value for record in records)
    cv_bands = Counter(
        record.cv_quality_band for record in records
        if record.value_status == ASHEValueStatus.REPORTED
    )
    region_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        region_counts[record.geography_label][record.value_status.value] += 1

    lines = [
        "# ASHE 2025 Revised — Local Preparation Quality Report",
        "",
        "**Processing mode:** LOCAL_PREPARATION_ONLY  ",
        "**Source reuse status:** REVIEW_REQUIRED  ",
        "**Publication eligible:** No  ",
        f"**Run ID:** `{run_id}`  ",
        f"**Processed dataset SHA-256:** `{dataset_sha256}`",
        "",
        "This report describes a validated source-preserving aggregate preparation. It does not approve public release and contains no rejected source contents or salary values.",
        "",
        "## Validation summary",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Records structurally accepted | {len(records)} |",
        f"| Reported median cells | {statuses[ASHEValueStatus.REPORTED.value]} |",
        f"| Quality-suppressed (`x`) cells | {statuses[ASHEValueStatus.SUPPRESSED_QUALITY.value]} |",
        f"| Blank/unknown cells | {statuses[ASHEValueStatus.BLANK_UNKNOWN.value]} |",
        "| Rejected source rows | 0; any rejected row blocks artifact generation |",
        f"| CV values ≤5% | {cv_bands['CV_LE_5']} |",
        f"| CV values >5–10% | {cv_bands['CV_GT_5_LE_10']} |",
        f"| CV values >10–20% | {cv_bands['CV_GT_10_LE_20']} |",
        "| Non-finite numeric salaries | 0 (pipeline rejects these) |",
        "| Zero or negative reported salaries | 0 (pipeline rejects these) |",
        f"| Numeric source P10–P90 cells | {source_numeric_percentile_cells}; no distribution curve is prepared |",
        "| SOC 2020 codes | 412 matched to official unit groups |",
        "| GB work regions | 11; no Northern Ireland or UK total |",
        "",
        "## Region-level cell coverage",
        "",
        "| Work region | Reported numeric | `x` suppressed | Blank/unknown |",
        "|---|---:|---:|---:|",
    ]
    for region in EXPECTED_REGIONS:
        counts = region_counts[region]
        lines.append(
            f"| {region} | {counts['REPORTED']} | {counts['SUPPRESSED_QUALITY']} | {counts['BLANK_UNKNOWN']} |"
        )
    lines.extend([
        "",
        "## Data handling",
        "",
        "Source values and markers are preserved. Suppressed and blank estimates have no salary amount. No imputation, annualization, currency conversion, aggregation of occupation medians, or salary distribution derivation was performed.",
        "",
        "The ONS source remains `REVIEW_REQUIRED` in the existing registry; the output is local-only and is not eligible for an API or public dashboard.",
        "",
    ])
    if not validation_summary:
        lines.insert(lines.index("## Data handling"), "No validation issue codes were raised.")
    else:
        # Stable codes only; never put source values or descriptions in this report.
        lines.insert(lines.index("## Data handling"), "Validation issue counts: " + ", ".join(
            f"`{code}`={count}" for code, count in sorted(validation_summary.items())
        ) + ".")
    return "\n".join(lines)


def _manifest_json(manifest: ASHERunManifest) -> bytes:
    payload = manifest.model_dump(mode="json")
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _existing_output_is_same(output_dir: Path, dataset_bytes: bytes, archive_sha: str) -> bool:
    dataset_path = output_dir / OUTPUT_FILENAME
    manifest_path = output_dir / "provenance_manifest.json"
    if not dataset_path.is_file() or not manifest_path.is_file():
        return False
    if dataset_path.read_bytes() != dataset_bytes:
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        manifest.get("archive_sha256") == archive_sha
        and manifest.get("transformation_version") == TRANSFORMATION_VERSION
        and manifest.get("processed_dataset_sha256") == hashlib.sha256(dataset_bytes).hexdigest().upper()
        and manifest.get("publication_eligible") is False
        and manifest.get("source_reuse_review_status") == ReuseReviewStatus.REVIEW_REQUIRED.value
    )


def run_ashe_2025_pipeline(
    *,
    archive_path: Path = DEFAULT_ARCHIVE,
    extracted_root: Path = DEFAULT_EXTRACTED,
    soc_reference_path: Path = DEFAULT_SOC_REFERENCE,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    local_preparation_only: bool = False,
    ingested_at: datetime | None = None,
) -> PipelineResult:
    if not local_preparation_only:
        raise PipelineError(
            "local_preparation_acknowledgement_required",
            "Pass --local-preparation-only; the catalog remains REVIEW_REQUIRED and output is not publishable.",
        )
    catalog_reference, source_reference_matches = _source_catalog_reference()
    assets = verify_archive_layout(archive_path, extracted_root, soc_reference_path)
    occupations = load_occupation_reference(assets.soc_path)
    if len(occupations) != EXPECTED_CODES:
        raise PipelineError("unexpected_official_occupation_count", "SOC reference code count is unexpected.")

    timestamp = ingested_at or datetime.now(timezone.utc)
    if timestamp.utcoffset() is None:
        raise PipelineError("invalid_ingestion_timestamp", "Ingestion timestamp must be timezone-aware.")
    run_id = f"ashe25r-{assets.archive_sha256[:16].lower()}-{TRANSFORMATION_VERSION}"
    parsed = parse_workbook_pair(
        assets.estimate_path,
        assets.cv_path,
        occupations,
        run_id=run_id,
        archive_sha256=assets.archive_sha256,
        estimate_filename=assets.estimate_path.name,
        estimate_sha256=assets.estimate_sha256,
        cv_filename=assets.cv_path.name,
        cv_sha256=assets.cv_sha256,
        classification_filename=assets.soc_path.name,
        classification_sha256=assets.soc_sha256,
        catalog_source_reference=catalog_reference,
    )
    if parsed.quality.rows_rejected:
        raise PipelineError(
            "source_rows_rejected",
            "ASHE validation rejected source rows; no processed dataset was written.",
            parse_result=parsed,
        )
    try:
        validate_expected_grid(parsed.records, occupations)
    except PipelineError as exc:
        raise PipelineError(exc.code, str(exc), parse_result=parsed) from exc

    statuses = Counter(count_value_statuses(parsed.records))
    expected_statuses = {
        ASHEValueStatus.REPORTED.value: EXPECTED_NUMERIC,
        ASHEValueStatus.SUPPRESSED_QUALITY.value: EXPECTED_SUPPRESSED,
        ASHEValueStatus.BLANK_UNKNOWN.value: EXPECTED_BLANK,
    }
    if dict(statuses) != expected_statuses:
        raise PipelineError("unexpected_value_status_counts", "ASHE cell-status counts differ from the verified release.", parse_result=parsed)

    dataset_bytes = serialize_dataset(parsed.records)
    dataset_sha = hashlib.sha256(dataset_bytes).hexdigest().upper()
    issue_counts = summarize_quality(parsed)
    quality_report = build_quality_report(
        parsed.records,
        run_id=run_id,
        dataset_sha256=dataset_sha,
        source_numeric_percentile_cells=parsed.source_numeric_percentile_cells,
        validation_summary=issue_counts,
    )
    quality_filename = "quality_report.md"
    dataset_filename = OUTPUT_FILENAME
    provenance = build_data_provenance(timestamp)
    manifest = ASHERunManifest(
        run_id=run_id,
        source_id=SOURCE_ID,
        source_reuse_review_status=ReuseReviewStatus.REVIEW_REQUIRED,
        processing_mode="LOCAL_PREPARATION_ONLY",
        source_reference=SOURCE_REFERENCE,
        source_attribution=SOURCE_ATTRIBUTION,
        catalog_source_reference=catalog_reference,
        source_reference_matches_catalog=source_reference_matches,
        ingested_at=timestamp,
        dataset_version="2025 revised",
        source_reference_period=REFERENCE_PERIOD,
        archive_filename=archive_path.name,
        archive_size_bytes=assets.archive_size_bytes,
        archive_sha256=assets.archive_sha256,
        archive_checksum_verified=True,
        archive_member_count=assets.archive_member_count,
        extracted_workbook_count=assets.extracted_workbook_count,
        estimate_workbook_filename=assets.estimate_path.name,
        estimate_workbook_sha256=assets.estimate_sha256,
        cv_workbook_filename=assets.cv_path.name,
        cv_workbook_sha256=assets.cv_sha256,
        classification_reference_filename=assets.soc_path.name,
        classification_reference_sha256=assets.soc_sha256,
        transformation_version=TRANSFORMATION_VERSION,
        occupation_classification="SOC 2020",
        occupation_codes_verified=len(occupations),
        geography_level="GB work regions",
        geographic_coverage=EXPECTED_REGIONS,
        selected_sheet="Full-Time",
        selected_measure="Table 15.7a Annual pay - Gross; Median",
        selected_variables=(
            "Description", "Code", "Median", "CV Median", "Full-Time",
            "Table 15.7a Annual pay - Gross",
        ),
        workbook_data_rows_scanned=parsed.workbook_rows_scanned,
        non_data_rows_classified=parsed.non_data_rows_classified,
        source_numeric_percentile_cells=parsed.source_numeric_percentile_cells,
        validation_result=parsed.quality,
        value_status_counts=dict(sorted(statuses.items())),
        validation_summary=issue_counts,
        data_provenance=provenance,
        processed_dataset_filename=dataset_filename,
        processed_dataset_sha256=dataset_sha,
        quality_report_filename=quality_filename,
    )
    manifest_bytes = _manifest_json(manifest)
    output_dir = output_root / run_id
    dataset_path = output_dir / dataset_filename
    manifest_path = output_dir / "provenance_manifest.json"
    report_path = output_dir / quality_filename

    output_root.mkdir(parents=True, exist_ok=True)
    if output_dir.exists():
        if _existing_output_is_same(output_dir, dataset_bytes, assets.archive_sha256):
            return PipelineResult(
                output_directory=output_dir,
                dataset_path=dataset_path,
                manifest_path=manifest_path,
                quality_report_path=report_path,
                dataset_sha256=dataset_sha,
                run_id=run_id,
                records_written=len(parsed.records),
                reused_existing_output=True,
            )
        raise PipelineError("output_version_conflict", "Existing versioned output differs; it was not overwritten.")

    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_id}.", dir=output_root))
    try:
        (temp_dir / dataset_filename).write_bytes(dataset_bytes)
        (temp_dir / "provenance_manifest.json").write_bytes(manifest_bytes)
        (temp_dir / quality_filename).write_text(quality_report, encoding="utf-8", newline="\n")
        if sha256_file(temp_dir / dataset_filename) != dataset_sha:
            raise PipelineError("output_checksum_mismatch", "Processed dataset checksum verification failed.")
        temp_dir.rename(output_dir)
    except Exception:
        if temp_dir.exists():
            for child in temp_dir.iterdir():
                child.unlink(missing_ok=True)
            temp_dir.rmdir()
        raise

    return PipelineResult(
        output_directory=output_dir,
        dataset_path=dataset_path,
        manifest_path=manifest_path,
        quality_report_path=report_path,
        dataset_sha256=dataset_sha,
        run_id=run_id,
        records_written=len(parsed.records),
        reused_existing_output=False,
    )
