from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator


class UKWorkRegion(StrEnum):
    EAST = "East"
    EAST_MIDLANDS = "East Midlands"
    LONDON = "London"
    NORTH_EAST = "North East"
    NORTH_WEST = "North West"
    SCOTLAND = "Scotland"
    SOUTH_EAST = "South East"
    SOUTH_WEST = "South West"
    WALES = "Wales"
    WEST_MIDLANDS = "West Midlands"
    YORKSHIRE_AND_THE_HUMBER = "Yorkshire and The Humber"


class UKValueStatus(StrEnum):
    REPORTED = "REPORTED"
    SUPPRESSED_QUALITY = "SUPPRESSED_QUALITY"
    SUPPRESSED_DISCLOSURE = "SUPPRESSED_DISCLOSURE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NIL_OR_NEGLIGIBLE = "NIL_OR_NEGLIGIBLE"
    BLANK_UNKNOWN = "BLANK_UNKNOWN"


class UKSalaryContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_id: Literal["UK"] = "UK"
    source_id: Literal["uk.ons.ashe"] = "uk.ons.ashe"
    reference_period: Literal["Tax year ending 5 April 2025"]
    measure: Literal["Full-time annual gross pay median (ONS Table 15.7a)"]
    population_definition: str = Field(min_length=10, max_length=300)
    occupation_classification: Literal["SOC 2020 unit group"]
    geography_coverage: tuple[UKWorkRegion, ...]
    transformation_version: Literal["ashe-table15-2025r-v1.0.2"]
    data_quality_status: Literal["VALIDATED"]
    publication_status: Literal["PUBLISHED", "NOT_PUBLISHED"]
    source_attribution: str = Field(min_length=10, max_length=300)


class UKAPIErrorDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: Literal["UK_DATA_NOT_PUBLISHED", "UK_DATA_UNAVAILABLE"]
    message: str = Field(min_length=1, max_length=160)


class UKAPIErrorEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    detail: UKAPIErrorDetail


class UKRegionObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    region_label: UKWorkRegion
    value_status: UKValueStatus
    annual_gross_median_gbp: Decimal | None = Field(default=None, gt=Decimal("0"), max_digits=12, decimal_places=2)
    original_ons_median_cell: str = Field(max_length=64)
    cv_percent: Decimal | None = Field(default=None, ge=Decimal("0"), max_digits=8, decimal_places=4)
    original_ons_cv_cell: str | None = Field(default=None, max_length=64)
    cv_quality_band: str = Field(min_length=2, max_length=48)

    @model_validator(mode="after")
    def preserve_source_status(self) -> "UKRegionObservation":
        if self.value_status == UKValueStatus.REPORTED:
            if self.annual_gross_median_gbp is None or self.cv_percent is None:
                raise ValueError("reported observations require a numeric median and CV")
            if self.cv_percent > Decimal("20"):
                raise ValueError("reported observations must meet the ONS CV threshold")
        elif self.annual_gross_median_gbp is not None:
            raise ValueError("unavailable observations cannot contain a salary value")
        if self.value_status == UKValueStatus.SUPPRESSED_QUALITY and self.original_ons_median_cell != "x":
            raise ValueError("quality-suppressed observations must preserve the source marker")
        if self.value_status == UKValueStatus.BLANK_UNKNOWN and self.original_ons_median_cell != "":
            raise ValueError("blank observations must preserve the empty source cell")
        return self


class UKCoverage(BaseModel):
    model_config = ConfigDict(frozen=True)

    reported_count: int = Field(ge=0)
    suppressed_count: int = Field(ge=0)
    blank_count: int = Field(ge=0)
    expected_count: int = Field(gt=0)
    reported_coverage_ratio: Decimal = Field(ge=Decimal("0"), le=Decimal("1"), max_digits=6, decimal_places=4)

    @model_validator(mode="after")
    def counts_and_ratio_agree(self) -> "UKCoverage":
        if self.reported_count + self.suppressed_count + self.blank_count != self.expected_count:
            raise ValueError("coverage status counts must equal the expected denominator")
        expected_ratio = (Decimal(self.reported_count) / Decimal(self.expected_count)).quantize(Decimal("0.0001"))
        if self.reported_coverage_ratio != expected_ratio:
            raise ValueError("reported coverage ratio does not match its counts")
        return self


class UKOccupationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    soc_code: str = Field(pattern=r"^[0-9]{4}$")
    official_title: str = Field(min_length=1, max_length=200)
    source_description: str = Field(min_length=1, max_length=200)
    reported_region_count: int = Field(ge=0, le=11)
    suppressed_region_count: int = Field(ge=0, le=11)
    blank_region_count: int = Field(ge=0, le=11)
    expected_region_count: Literal[11] = 11

    @model_validator(mode="after")
    def region_counts_are_complete(self) -> "UKOccupationSummary":
        if self.reported_region_count + self.suppressed_region_count + self.blank_region_count != self.expected_region_count:
            raise ValueError("occupation region counts must equal the complete region denominator")
        return self


class UKOccupationPage(BaseModel):
    model_config = ConfigDict(frozen=True)

    context: UKSalaryContext
    items: tuple[UKOccupationSummary, ...]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_count: int = Field(ge=0)
    has_next: bool
    coverage: UKCoverage


class UKOccupationDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    context: UKSalaryContext
    occupation: UKOccupationSummary
    regions: tuple[UKRegionObservation, ...] = Field(min_length=11, max_length=11)
    coverage: UKCoverage


class UKRegionComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    context: UKSalaryContext
    soc_code: str = Field(pattern=r"^[0-9]{4}$")
    official_title: str = Field(min_length=1, max_length=200)
    observations: tuple[UKRegionObservation, ...] = Field(min_length=11, max_length=11)
    reported_regions_count: int = Field(ge=0, le=11)
    expected_regions_count: Literal[11] = 11
    coverage_ratio: Decimal = Field(ge=Decimal("0"), le=Decimal("1"), max_digits=6, decimal_places=4)
    coverage_warning: str | None = Field(default=None, max_length=240)


class UKRegionOccupationItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    soc_code: str = Field(pattern=r"^[0-9]{4}$")
    official_title: str = Field(min_length=1, max_length=200)
    source_description: str = Field(min_length=1, max_length=200)
    observation: UKRegionObservation


class UKRegionOccupationPage(BaseModel):
    model_config = ConfigDict(frozen=True)

    context: UKSalaryContext
    region_label: UKWorkRegion
    items: tuple[UKRegionOccupationItem, ...]
    value_status_filter: UKValueStatus
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_count: int = Field(ge=0)
    has_next: bool
    coverage: UKCoverage


class UKSalaryMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    context: UKSalaryContext
    dataset_version: Literal["2025 revised"]
    source_reference: AnyHttpUrl
    source_archive_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    processed_dataset_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    occupation_count: int = Field(gt=0)
    region_count: int = Field(gt=0)
    observation_count: int = Field(gt=0)
    status_counts: dict[UKValueStatus, int]
    ingested_at: datetime
