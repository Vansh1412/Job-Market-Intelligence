from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MarketId(StrEnum):
    IN = "IN"
    US = "US"
    UK = "UK"
    AU = "AU"
    SG = "SG"


class CurrencyCode(StrEnum):
    INR = "INR"
    USD = "USD"
    GBP = "GBP"
    AUD = "AUD"
    SGD = "SGD"


class CapabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    UNAVAILABLE = "UNAVAILABLE"


class MarketCapability(StrEnum):
    SALARY_PREDICTION = "salary_prediction"
    SALARY_ANALYTICS = "salary_analytics"
    SKILLS_ANALYTICS = "skills_analytics"
    DEMAND_ANALYTICS = "demand_analytics"
    OCCUPATION_MAPPING = "occupation_mapping"
    EMPLOYER_INTELLIGENCE = "employer_intelligence"


class MarketConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_id: MarketId
    display_name: str = Field(min_length=2, max_length=80)
    iso_country_code: str = Field(pattern=r"^[A-Z]{2}$")
    primary_currency: CurrencyCode
    salary_reporting_convention: str = Field(min_length=4, max_length=240)
    occupational_classification: str = Field(min_length=3, max_length=160)
    occupational_classification_version: str | None = Field(default=None, max_length=80)
    capabilities: dict[MarketCapability, CapabilityStatus]
    data_availability: CapabilityStatus
    source_ids: tuple[str, ...] = ()
    last_successful_update: datetime | None = None

    @field_validator("source_ids")
    @classmethod
    def source_ids_are_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("source_ids must be unique")
        return value

    @field_validator("last_successful_update")
    @classmethod
    def update_timestamp_is_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("last_successful_update must include a timezone")
        return value

    @model_validator(mode="after")
    def all_capabilities_are_explicit(self) -> "MarketConfig":
        if set(self.capabilities) != set(MarketCapability):
            raise ValueError("capabilities must explicitly describe every supported capability")
        return self
