from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.backend.schemas.data import DataProvenance, DataQualityResult, ReuseReviewStatus


class ASHEValueStatus(StrEnum):
    REPORTED = "REPORTED"
    SUPPRESSED_QUALITY = "SUPPRESSED_QUALITY"
    SUPPRESSED_DISCLOSURE = "SUPPRESSED_DISCLOSURE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NIL_OR_NEGLIGIBLE = "NIL_OR_NEGLIGIBLE"
    BLANK_UNKNOWN = "BLANK_UNKNOWN"


class ASHEAggregateRecord(BaseModel):
    """One source-published aggregate cell, not an individual salary record."""

    model_config = ConfigDict(frozen=True)

    observation_id: str = Field(pattern=r"^ashe25r-[0-9a-f]{16}-[0-9a-f]{16}$")
    run_id: str = Field(min_length=12, max_length=96)
    market_id: Literal["UK"] = "UK"
    occupation_code: str = Field(pattern=r"^[0-9]{4}$")
    occupation_description: str = Field(min_length=1, max_length=200)
    official_occupation_title: str = Field(min_length=1, max_length=200)
    source_occupation_code: str = Field(pattern=r"^'?\d{4}$")
    classification_id: Literal["SOC"] = "SOC"
    classification_version: Literal["2020"] = "2020"
    major_group_code: int = Field(ge=1, le=9)
    major_group_title: str = Field(min_length=1, max_length=160)
    geography_code: None = None
    geography_level: Literal["WORK_REGION"] = "WORK_REGION"
    geography_label: str = Field(min_length=2, max_length=80)
    source_description: str = Field(min_length=2, max_length=300)
    salary_value: Decimal | None
    original_ons_median_cell: str = Field(max_length=64)
    original_ons_cv: Decimal | None
    original_ons_cv_cell: str | None = Field(default=None, max_length=64)
    cv_quality_band: str
    value_status: ASHEValueStatus
    salary_measure_code: Literal["15.7a"] = "15.7a"
    earnings_definition: Literal["Gross annual pay"] = "Gross annual pay"
    statistic: Literal["MEDIAN"] = "MEDIAN"
    employee_group: Literal["FULL_TIME"] = "FULL_TIME"
    currency: Literal["GBP"] = "GBP"
    salary_period: Literal["ANNUAL"] = "ANNUAL"
    reference_period: Literal["Tax year ending 5 April 2025"] = "Tax year ending 5 April 2025"
    source_id: Literal["uk.ons.ashe"] = "uk.ons.ashe"
    source_asset_version: Literal["2025-revised-table15-four-digit"] = "2025-revised-table15-four-digit"
    source_archive_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    source_estimate_workbook: str = Field(min_length=1, max_length=220)
    source_estimate_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    source_cv_workbook: str = Field(min_length=1, max_length=220)
    source_cv_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    classification_reference_file: str = Field(min_length=1, max_length=220)
    classification_reference_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    source_reference: str = Field(min_length=8, max_length=300)
    catalog_source_reference: str = Field(min_length=8, max_length=300)
    source_reference_matches_catalog: bool
    source_attribution: str = Field(min_length=10, max_length=300)
    transformation_version: str = Field(min_length=3, max_length=32)

    @field_validator("salary_value")
    @classmethod
    def salary_is_finite_positive_when_present(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and (not value.is_finite() or value <= 0):
            raise ValueError("reported salary must be finite and positive")
        return value

    @field_validator("original_ons_cv")
    @classmethod
    def cv_is_finite_nonnegative_when_present(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and (not value.is_finite() or value < 0):
            raise ValueError("CV must be finite and nonnegative")
        return value

    @model_validator(mode="after")
    def value_status_matches_source_value(self) -> "ASHEAggregateRecord":
        if self.value_status == ASHEValueStatus.REPORTED:
            if self.salary_value is None or self.original_ons_cv is None:
                raise ValueError("reported estimate requires salary and CV")
            if self.original_ons_cv > Decimal("20"):
                raise ValueError("reported estimate CV must not exceed the ONS suppression threshold")
        elif self.salary_value is not None:
            raise ValueError("non-reported estimate must not contain a salary amount")
        expected_cell = {
            ASHEValueStatus.SUPPRESSED_QUALITY: "x",
            ASHEValueStatus.SUPPRESSED_DISCLOSURE: "..",
            ASHEValueStatus.NOT_APPLICABLE: ":",
            ASHEValueStatus.NIL_OR_NEGLIGIBLE: "-",
            ASHEValueStatus.BLANK_UNKNOWN: "",
        }.get(self.value_status)
        if expected_cell is not None and self.original_ons_median_cell != expected_cell:
            raise ValueError("source median marker and value status do not match")
        return self


class ASHERunManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    source_id: Literal["uk.ons.ashe"]
    source_reuse_review_status: ReuseReviewStatus
    processing_mode: Literal["LOCAL_PREPARATION_ONLY"]
    publication_eligible: Literal[False] = False
    source_reference: str
    catalog_source_reference: str
    source_reference_matches_catalog: bool
    source_attribution: str
    ingested_at: datetime
    dataset_version: Literal["2025 revised"]
    source_reference_period: Literal["Tax year ending 5 April 2025"]
    archive_filename: str
    archive_size_bytes: int = Field(ge=1)
    archive_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    archive_checksum_verified: bool
    archive_member_count: int = Field(ge=1)
    extracted_workbook_count: int = Field(ge=1)
    estimate_workbook_filename: str
    estimate_workbook_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    cv_workbook_filename: str
    cv_workbook_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    classification_reference_filename: str
    classification_reference_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    transformation_version: str
    occupation_classification: Literal["SOC 2020"]
    occupation_codes_verified: int = Field(ge=0)
    geography_level: Literal["GB work regions"]
    geographic_coverage: tuple[str, ...]
    selected_sheet: Literal["Full-Time"]
    selected_measure: Literal["Table 15.7a Annual pay - Gross; Median"]
    selected_variables: tuple[str, ...]
    workbook_data_rows_scanned: int = Field(ge=0)
    non_data_rows_classified: int = Field(ge=0)
    source_numeric_percentile_cells: int = Field(ge=0)
    validation_result: DataQualityResult
    value_status_counts: dict[str, int]
    validation_summary: dict[str, int]
    data_provenance: DataProvenance
    processed_dataset_filename: str
    processed_dataset_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    quality_report_filename: str

    @field_validator("ingested_at")
    @classmethod
    def ingestion_timestamp_is_aware(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("ingested_at must be timezone-aware")
        return value

    @model_validator(mode="after")
    def preserve_review_gate(self) -> "ASHERunManifest":
        if self.source_reuse_review_status != ReuseReviewStatus.REVIEW_REQUIRED:
            raise ValueError("ASHE preparation must preserve REVIEW_REQUIRED source status")
        if self.publication_eligible:
            raise ValueError("local preparation artifact cannot be marked publication eligible")
        return self
