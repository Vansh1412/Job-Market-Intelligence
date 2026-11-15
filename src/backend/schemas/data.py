import re
from datetime import datetime
from enum import StrEnum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceCategory(StrEnum):
    OFFICIAL_STATISTICS = "OFFICIAL_STATISTICS"
    COMPANY_DISCLOSURE = "COMPANY_DISCLOSURE"
    COMPANY_CAREER_PAGE = "COMPANY_CAREER_PAGE"
    PERMITTED_JOB_POSTING = "PERMITTED_JOB_POSTING"
    EXISTING_PROJECT_DATA = "EXISTING_PROJECT_DATA"


class ReuseReviewStatus(StrEnum):
    APPROVED = "APPROVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class ValidationStatus(StrEnum):
    NOT_COLLECTED = "NOT_COLLECTED"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class DataSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    source_name: str = Field(min_length=2, max_length=160)
    source_organization: str = Field(min_length=2, max_length=160)
    source_reference: AnyHttpUrl | None = None
    canonical_publication_url: AnyHttpUrl | None = None
    acquisition_url: AnyHttpUrl | None = None
    artifact_download_url: AnyHttpUrl | None = None
    source_category: SourceCategory
    reuse_review_status: ReuseReviewStatus
    dataset_description: str = Field(min_length=4, max_length=600)
    geographic_coverage: tuple[str, ...] = ()
    update_frequency: str | None = Field(default=None, max_length=100)
    reference_period: str | None = Field(default=None, max_length=32)
    collected_at: datetime | None = None
    validation_status: ValidationStatus = ValidationStatus.NOT_COLLECTED

    @field_validator("reference_period")
    @classmethod
    def source_period_is_supported(cls, value: str | None) -> str | None:
        if value is not None:
            validate_reference_period(value)
        return value

    @field_validator("collected_at")
    @classmethod
    def collection_timestamp_is_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("collected_at must include a timezone")
        return value


class DataProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    collected_at: datetime
    reference_period: str
    geographic_coverage: tuple[str, ...] = ()
    dataset_description: str = Field(min_length=4, max_length=600)
    validation_status: ValidationStatus

    @field_validator("reference_period")
    @classmethod
    def provenance_period_is_supported(cls, value: str) -> str:
        validate_reference_period(value)
        return value

    @field_validator("collected_at")
    @classmethod
    def collection_timestamp_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("collected_at must include a timezone")
        return value


class DataQualityIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_index: int = Field(ge=0)
    code: str = Field(min_length=2, max_length=80)
    field: str | None = Field(default=None, max_length=120)
    message: str = Field(min_length=2, max_length=200)


class RejectedRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_index: int = Field(ge=0)
    reason_codes: tuple[str, ...] = Field(min_length=1)


class DataQualityResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    rows_seen: int = Field(ge=0)
    rows_accepted: int = Field(ge=0)
    rows_rejected: int = Field(ge=0)
    issues: tuple[DataQualityIssue, ...] = ()
    rejected_rows: tuple[RejectedRow, ...] = ()

    @model_validator(mode="after")
    def counts_are_consistent(self) -> "DataQualityResult":
        if self.rows_seen != self.rows_accepted + self.rows_rejected:
            raise ValueError("rows_seen must equal rows_accepted plus rows_rejected")
        if len(self.rejected_rows) != self.rows_rejected:
            raise ValueError("rejected_rows must describe each rejected input row")
        return self


def validate_reference_period(value: str) -> str:
    patterns = (
        r"\d{4}",
        r"\d{4}-(0[1-9]|1[0-2])",
        r"\d{4}-Q[1-4]",
    )
    if not any(re.fullmatch(pattern, value) for pattern in patterns):
        raise ValueError("reference period must be YYYY, YYYY-MM, or YYYY-Qn")
    return value
