from collections.abc import Iterable, Mapping
from typing import Any

from pydantic import ValidationError

from src.backend.data_catalog.registry import SourceRegistry
from src.backend.schemas.data import DataProvenance, DataQualityIssue, DataQualityResult, RejectedRow
from src.backend.schemas.market import MarketId
from src.backend.schemas.salary import SalaryObservation


def _issue_code(field: str | None, error_type: str) -> str:
    if error_type == "missing":
        return "missing_required_field"
    if field == "salary_value":
        return "invalid_salary"
    if field == "currency":
        return "unsupported_currency"
    if field == "market_id":
        return "unsupported_market"
    if field == "reference_period":
        return "invalid_reference_period"
    return "invalid_field"


def validate_salary_observations(
    rows: Iterable[Mapping[str, Any]],
    source_ids: frozenset[str] | None = None,
) -> DataQualityResult:
    known_source_ids = source_ids if source_ids is not None else SourceRegistry().identifiers()
    seen_identifiers: set[str] = set()
    issues: list[DataQualityIssue] = []
    rejected_rows: list[RejectedRow] = []
    accepted_count = 0
    rows_seen = 0

    for row_index, row in enumerate(rows):
        rows_seen += 1
        row_issue_codes: list[str] = []
        if not isinstance(row, Mapping):
            issues.append(DataQualityIssue(
                row_index=row_index,
                code="invalid_record",
                message="Record must be an object.",
            ))
            rejected_rows.append(RejectedRow(row_index=row_index, reason_codes=("invalid_record",)))
            continue

        observation_id = row.get("observation_id")
        if isinstance(observation_id, str):
            if observation_id in seen_identifiers:
                issues.append(DataQualityIssue(
                    row_index=row_index,
                    code="duplicate_identifier",
                    field="observation_id",
                    message="Observation identifier is duplicated.",
                ))
                row_issue_codes.append("duplicate_identifier")
            else:
                seen_identifiers.add(observation_id)

        try:
            observation = SalaryObservation.model_validate(row)
        except ValidationError as exc:
            for error in exc.errors(include_input=False):
                field = ".".join(str(part) for part in error["loc"]) or None
                code = _issue_code(field, error["type"])
                issues.append(DataQualityIssue(
                    row_index=row_index,
                    code=code,
                    field=field,
                    message="Invalid or missing value for this field.",
                ))
                row_issue_codes.append(code)
            observation = None

        if observation is not None and observation.source_id not in known_source_ids:
            issues.append(DataQualityIssue(
                row_index=row_index,
                code="unknown_source",
                field="source_id",
                message="Source identifier is not registered.",
            ))
            row_issue_codes.append("unknown_source")

        if row_issue_codes:
            rejected_rows.append(RejectedRow(
                row_index=row_index,
                reason_codes=tuple(dict.fromkeys(row_issue_codes)),
            ))
        else:
            accepted_count += 1

    return DataQualityResult(
        rows_seen=rows_seen,
        rows_accepted=accepted_count,
        rows_rejected=len(rejected_rows),
        issues=tuple(issues),
        rejected_rows=tuple(rejected_rows),
    )


def validate_data_provenance(
    record: Mapping[str, Any],
    source_ids: frozenset[str] | None = None,
) -> DataQualityResult:
    known_source_ids = source_ids if source_ids is not None else SourceRegistry().identifiers()
    issues: list[DataQualityIssue] = []

    try:
        provenance = DataProvenance.model_validate(record)
    except ValidationError as exc:
        for error in exc.errors(include_input=False):
            field = ".".join(str(part) for part in error["loc"]) or None
            code = "missing_required_field" if error["type"] == "missing" else (
                "invalid_reference_period" if field == "reference_period" else "invalid_field"
            )
            issues.append(DataQualityIssue(
                row_index=0,
                code=code,
                field=field,
                message="Invalid or missing value for this field.",
            ))
        provenance = None

    if provenance is not None and provenance.source_id not in known_source_ids:
        issues.append(DataQualityIssue(
            row_index=0,
            code="unknown_source",
            field="source_id",
            message="Source identifier is not registered.",
        ))

    rejected_rows = (
        (RejectedRow(row_index=0, reason_codes=tuple(dict.fromkeys(issue.code for issue in issues))),)
        if issues else ()
    )
    return DataQualityResult(
        rows_seen=1,
        rows_accepted=0 if issues else 1,
        rows_rejected=1 if issues else 0,
        issues=tuple(issues),
        rejected_rows=rejected_rows,
    )
