from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from itertools import zip_longest
from pathlib import Path
from typing import BinaryIO

from openpyxl import load_workbook
from pydantic import ValidationError

from src.backend.ingestion.contracts import ASHEAggregateRecord, ASHEValueStatus
from src.backend.schemas.data import DataQualityIssue, DataQualityResult, RejectedRow


TRANSFORMATION_VERSION = "ashe-table15-2025r-v1.0.2"
SOURCE_ID = "uk.ons.ashe"
SOURCE_REFERENCE = (
    "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/"
    "earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15"
)
SOURCE_ATTRIBUTION = (
    "Source: Office for National Statistics, Annual Survey of Hours and Earnings, "
    "ASHE Table 15, 2025 revised; Open Government Licence v3.0."
)
REFERENCE_PERIOD = "Tax year ending 5 April 2025"
EXPECTED_HEADER = (
    "Description", "Code", "(thousand)", "Median", "change", "Mean", "change",
    10, 20, 25, 30, 40, 60, 70, 75, 80, 90,
)
EXPECTED_REGIONS = (
    "East", "East Midlands", "London", "North East", "North West", "Scotland",
    "South East", "South West", "Wales", "West Midlands", "Yorkshire and The Humber",
)
CELL_CODE = re.compile(r"^'?([0-9]{4})$")
FOOTER_PREFIXES = (
    "a  employees", "b  figures", "key -", "the quality of an estimate", "source:"
)
MARKER_STATUS = {
    "x": ASHEValueStatus.SUPPRESSED_QUALITY,
    "..": ASHEValueStatus.SUPPRESSED_DISCLOSURE,
    ":": ASHEValueStatus.NOT_APPLICABLE,
    "-": ASHEValueStatus.NIL_OR_NEGLIGIBLE,
}


@dataclass(frozen=True)
class OccupationReference:
    code: str
    title: str
    major_group_code: int
    major_group_title: str


@dataclass(frozen=True)
class ParseResult:
    records: tuple[ASHEAggregateRecord, ...]
    quality: DataQualityResult
    workbook_rows_scanned: int
    non_data_rows_classified: int
    source_numeric_percentile_cells: int
    value_status_counts: dict[str, int]


class WorkbookContractError(ValueError):
    """Raised for an unsupported sheet/header without leaking workbook cells."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def verify_sha256(path: Path, expected: str) -> str:
    actual = sha256_file(path)
    if not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or actual.casefold() != expected.casefold():
        raise ValueError("Source checksum verification failed.")
    return actual


def _is_blank_row(row: tuple[object, ...]) -> bool:
    return all(value is None for value in row)


def _is_known_footer(row: tuple[object, ...]) -> bool:
    description = row[0]
    if not isinstance(description, str):
        return False
    return description.strip().casefold().startswith(FOOTER_PREFIXES)


def _issue(row_index: int, code: str, field: str, message: str) -> DataQualityIssue:
    return DataQualityIssue(row_index=row_index, code=code, field=field, message=message)


def classify_source_cell(value: object) -> tuple[ASHEValueStatus | None, Decimal | None, str, str | None]:
    """Return (status, numeric amount, original cell text, stable error code)."""
    if isinstance(value, bool):
        return None, None, str(value), "invalid_value_marker"
    if isinstance(value, (int, float, Decimal)):
        try:
            amount = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None, None, str(value), "invalid_salary_value"
        if not amount.is_finite():
            return None, None, str(value), "non_finite_salary"
        if amount <= 0:
            return None, None, str(value), "non_positive_salary"
        return ASHEValueStatus.REPORTED, amount, str(amount), None
    if value is None:
        return ASHEValueStatus.BLANK_UNKNOWN, None, "", None
    if isinstance(value, str):
        marker = value.strip()
        if marker.casefold() in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
            return None, None, marker, "non_finite_salary"
        if marker in MARKER_STATUS:
            return MARKER_STATUS[marker], None, marker, None
        try:
            parsed_text_number = Decimal(marker)
        except InvalidOperation:
            parsed_text_number = None
        if parsed_text_number is not None:
            if not parsed_text_number.is_finite():
                return None, None, marker, "non_finite_salary"
            if parsed_text_number <= 0:
                return None, None, marker, "non_positive_salary"
            return None, None, marker, "invalid_salary_value"
    return None, None, "", "invalid_value_marker"


def parse_cv_cell(value: object) -> tuple[Decimal | None, str | None, str | None]:
    """Return (numeric CV, original marker, stable error code)."""
    if isinstance(value, bool):
        return None, str(value), "invalid_cv"
    if isinstance(value, (int, float, Decimal)):
        try:
            cv = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None, str(value), "invalid_cv"
        if not cv.is_finite() or cv < 0:
            return None, str(value), "invalid_cv"
        return cv, str(cv), None
    if value is None:
        return None, None, None
    if isinstance(value, str) and value.strip() in {"x", "..", ":", "-", "."}:
        return None, value.strip(), None
    return None, str(value), "invalid_cv"


def cv_band(cv: Decimal | None, status: ASHEValueStatus, cv_marker: str | None) -> str:
    if cv is not None:
        if cv <= 5:
            return "CV_LE_5"
        if cv <= 10:
            return "CV_GT_5_LE_10"
        if cv <= 20:
            return "CV_GT_10_LE_20"
        return "CV_GT_20"
    if status == ASHEValueStatus.SUPPRESSED_QUALITY or cv_marker == "x":
        return "CV_GT_20_SUPPRESSED"
    if cv_marker == ".":
        return "CV_UNAVAILABLE"
    if cv_marker is None:
        return "CV_BLANK_UNKNOWN"
    return f"CV_MARKER_{cv_marker.replace('.', 'DOT').replace(':', 'NA')}"


def _check_status_cv_consistency(
    status: ASHEValueStatus,
    cv: Decimal | None,
    cv_marker: str | None,
) -> str | None:
    if status == ASHEValueStatus.REPORTED:
        if cv is None or cv > 20:
            return "reported_cv_missing_or_above_threshold"
    elif status == ASHEValueStatus.SUPPRESSED_QUALITY:
        if not (cv_marker == "x" or (cv is not None and cv > 20)):
            return "suppression_cv_inconsistent"
    return None


def load_occupation_reference(path: Path) -> dict[str, OccupationReference]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        if "SOC2020 descriptions" not in workbook.sheetnames:
            raise WorkbookContractError("SOC reference workbook is missing its expected sheet.")
        sheet = workbook["SOC2020 descriptions"]
        header = next(sheet.iter_rows(min_row=1, max_row=1, max_col=6, values_only=True))
        if tuple(header[:6]) != (
            "UNIQUE ID", "SOC2020 Major Group", "SOC2020 Sub-Major Group",
            "SOC2020 Minor Group", "SOC2020 Unit Group", "SOC2020\nGroup Title",
        ):
            raise WorkbookContractError("SOC reference workbook headers are not recognized.")
        major_titles: dict[int, str] = {}
        units: dict[str, OccupationReference] = {}
        current_major: int | None = None
        for row in sheet.iter_rows(min_row=2, max_col=6, values_only=True):
            major, sub_major, minor, unit, title = row[1], row[2], row[3], row[4], row[5]
            if (
                isinstance(major, int)
                and sub_major in (None, "<blank>")
                and minor in (None, "<blank>")
                and unit in (None, "<blank>")
            ):
                current_major = major
                major_titles[major] = str(title).strip()
            if isinstance(unit, int) and len(str(unit)) == 4:
                code = str(unit)
                if current_major is None or int(code[0]) != current_major:
                    raise WorkbookContractError("SOC unit-group hierarchy is inconsistent.")
                if code in units:
                    raise WorkbookContractError("SOC reference contains duplicate unit-group codes.")
                units[code] = OccupationReference(
                    code=code,
                    title=str(title).strip(),
                    major_group_code=current_major,
                    major_group_title=major_titles[current_major],
                )
        return units
    finally:
        workbook.close()


def _open_workbook(source: Path | BinaryIO):
    if hasattr(source, "seek"):
        source.seek(0)
    return load_workbook(source, read_only=True, data_only=True)


def parse_workbook_pair(
    estimate_source: Path | BinaryIO,
    cv_source: Path | BinaryIO,
    occupations: dict[str, OccupationReference],
    *,
    run_id: str,
    archive_sha256: str,
    estimate_filename: str,
    estimate_sha256: str,
    cv_filename: str,
    cv_sha256: str,
    classification_filename: str,
    classification_sha256: str,
    catalog_source_reference: str,
) -> ParseResult:
    estimate_book = _open_workbook(estimate_source)
    cv_book = _open_workbook(cv_source)
    issues: list[DataQualityIssue] = []
    rejected: list[RejectedRow] = []
    accepted: list[ASHEAggregateRecord] = []
    status_counts: Counter[str] = Counter()
    scanned = 0
    physical_rows_scanned = 0
    non_data_rows = 0
    numeric_percentile_cells = 0
    seen_keys: set[tuple[str, str]] = set()
    try:
        if "Full-Time" not in estimate_book.sheetnames or "Full-Time" not in cv_book.sheetnames:
            raise WorkbookContractError("Estimate/CV workbooks are missing the expected Full-Time sheet.")
        estimate_sheet = estimate_book["Full-Time"]
        cv_sheet = cv_book["Full-Time"]
        estimate_header = tuple(next(estimate_sheet.iter_rows(
            min_row=5, max_row=5, max_col=17, values_only=True
        )))
        cv_header = tuple(next(cv_sheet.iter_rows(min_row=5, max_row=5, max_col=17, values_only=True)))
        if estimate_header != EXPECTED_HEADER or cv_header != EXPECTED_HEADER:
            raise WorkbookContractError("Estimate/CV workbook data headers are not recognized.")

        estimate_rows = estimate_sheet.iter_rows(min_row=6, max_col=17, values_only=True)
        cv_rows = cv_sheet.iter_rows(min_row=6, max_col=17, values_only=True)
        sentinel = object()
        for excel_row, pair in enumerate(zip_longest(estimate_rows, cv_rows, fillvalue=sentinel), start=6):
            row, cv_row = pair
            if row is sentinel or cv_row is sentinel:
                raise WorkbookContractError("Estimate and CV worksheet row counts differ.")
            physical_rows_scanned += 1
            if _is_blank_row(row) and _is_blank_row(cv_row):
                non_data_rows += 1
                continue
            if _is_known_footer(row) and _is_known_footer(cv_row):
                non_data_rows += 1
                continue

            scanned += 1
            numeric_percentile_cells += sum(
                isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)
                for value in row[7:17]
            )
            row_codes: list[str] = []
            description, source_code = row[0], row[1]
            cv_description, cv_source_code = cv_row[0], cv_row[1]

            if not isinstance(description, str) or not description.strip():
                row_codes.append("missing_source_description")
                issues.append(_issue(excel_row, "missing_source_description", "source_description", "Required source description is missing."))
            if not isinstance(source_code, str) or not CELL_CODE.fullmatch(source_code.strip()):
                row_codes.append("invalid_occupation_code")
                issues.append(_issue(excel_row, "invalid_occupation_code", "occupation_code", "Source occupation code is invalid."))
                code = None
            else:
                code = CELL_CODE.fullmatch(source_code.strip()).group(1)
                if code not in occupations:
                    row_codes.append("unknown_occupation_code")
                    issues.append(_issue(excel_row, "unknown_occupation_code", "occupation_code", "Code is absent from the verified SOC 2020 reference."))
            if source_code != cv_source_code or description != cv_description:
                row_codes.append("estimate_cv_key_mismatch")
                issues.append(_issue(excel_row, "estimate_cv_key_mismatch", "source_key", "Estimate and CV source dimensions do not match."))

            region: str | None = None
            occupation_description: str | None = None
            if isinstance(description, str) and "," in description:
                region, occupation_description = (part.strip() for part in description.strip().split(",", 1))
                if region not in EXPECTED_REGIONS:
                    row_codes.append("unexpected_geography")
                    issues.append(_issue(excel_row, "unexpected_geography", "geography_label", "Source geography is outside the verified region set."))
                if not occupation_description:
                    row_codes.append("missing_occupation_description")
                    issues.append(_issue(excel_row, "missing_occupation_description", "occupation_description", "Occupation description is missing."))
            elif isinstance(description, str) and description.strip():
                row_codes.append("invalid_source_description")
                issues.append(_issue(excel_row, "invalid_source_description", "source_description", "Source description does not contain the expected dimensions."))

            if code is not None and region is not None:
                key = (region, code)
                if key in seen_keys:
                    row_codes.append("duplicate_occupation_region")
                    issues.append(_issue(excel_row, "duplicate_occupation_region", "occupation_region_key", "Occupation-region key is duplicated."))
                else:
                    seen_keys.add(key)

            value_status, salary_value, source_median_cell, median_error = classify_source_cell(row[3])
            if median_error:
                row_codes.append(median_error)
                messages = {
                    "invalid_salary_value": "Source salary value is not a valid number.",
                    "non_finite_salary": "Source salary value is not finite.",
                    "non_positive_salary": "Reported salary must be greater than zero.",
                    "invalid_value_marker": "Source salary cell has an unrecognized value state.",
                }
                issues.append(_issue(excel_row, median_error, "salary_value", messages[median_error]))

            original_cv, cv_marker, cv_error = parse_cv_cell(cv_row[3])
            if cv_error:
                row_codes.append(cv_error)
                issues.append(_issue(excel_row, cv_error, "original_ons_cv", "Source CV is invalid."))
            if value_status is not None and cv_error is None:
                consistency_error = _check_status_cv_consistency(value_status, original_cv, cv_marker)
                if consistency_error:
                    row_codes.append(consistency_error)
                    issues.append(_issue(excel_row, consistency_error, "original_ons_cv", "Source estimate and CV states are inconsistent."))

            if row_codes:
                rejected.append(RejectedRow(row_index=excel_row, reason_codes=tuple(dict.fromkeys(row_codes))))
                continue

            # The checks above establish these values and code-map membership.
            assert code is not None and region is not None and occupation_description is not None
            assert value_status is not None
            occupation = occupations[code]
            cell_key_digest = hashlib.sha256(f"{region}\x1f{code}".encode("utf-8")).hexdigest()[:16]
            observation_id = f"ashe25r-{archive_sha256[:16].lower()}-{cell_key_digest}"
            try:
                record = ASHEAggregateRecord(
                    observation_id=observation_id,
                    run_id=run_id,
                    occupation_code=code,
                    occupation_description=occupation_description,
                    official_occupation_title=occupation.title,
                    source_occupation_code=str(source_code),
                    major_group_code=occupation.major_group_code,
                    major_group_title=occupation.major_group_title,
                    geography_label=region,
                    source_description=str(description),
                    salary_value=salary_value,
                    original_ons_median_cell=source_median_cell,
                    original_ons_cv=original_cv,
                    original_ons_cv_cell=cv_marker,
                    cv_quality_band=cv_band(original_cv, value_status, cv_marker),
                    value_status=value_status,
                    source_archive_sha256=archive_sha256,
                    source_estimate_workbook=estimate_filename,
                    source_estimate_sha256=estimate_sha256,
                    source_cv_workbook=cv_filename,
                    source_cv_sha256=cv_sha256,
                    classification_reference_file=classification_filename,
                    classification_reference_sha256=classification_sha256,
                    source_reference=SOURCE_REFERENCE,
                    catalog_source_reference=catalog_source_reference,
                    source_reference_matches_catalog=(catalog_source_reference == SOURCE_REFERENCE),
                    source_attribution=SOURCE_ATTRIBUTION,
                    transformation_version=TRANSFORMATION_VERSION,
                )
            except ValidationError as exc:
                field_codes = {
                    "salary_value": "invalid_salary_value",
                    "original_ons_cv": "invalid_cv",
                    "occupation_code": "invalid_occupation_code",
                }
                codes = []
                for error in exc.errors(include_input=False):
                    field = str(error["loc"][0]) if error["loc"] else "record"
                    stable_code = field_codes.get(field, "invalid_aggregate_record")
                    codes.append(stable_code)
                    issues.append(_issue(excel_row, stable_code, field, "Aggregate record failed schema validation."))
                rejected.append(RejectedRow(row_index=excel_row, reason_codes=tuple(dict.fromkeys(codes))))
                continue
            accepted.append(record)
            status_counts[value_status.value] += 1
    finally:
        estimate_book.close()
        cv_book.close()

    result = DataQualityResult(
        rows_seen=scanned,
        rows_accepted=len(accepted),
        rows_rejected=len(rejected),
        issues=tuple(issues),
        rejected_rows=tuple(rejected),
    )
    return ParseResult(
        records=tuple(accepted),
        quality=result,
        workbook_rows_scanned=physical_rows_scanned,
        non_data_rows_classified=non_data_rows,
        source_numeric_percentile_cells=numeric_percentile_cells,
        value_status_counts=dict(sorted(status_counts.items())),
    )


def summarize_quality(result: ParseResult) -> dict[str, int]:
    issue_counts = Counter(issue.code for issue in result.quality.issues)
    return dict(sorted(issue_counts.items()))
