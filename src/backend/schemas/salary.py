from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.backend.schemas.data import validate_reference_period
from src.backend.schemas.market import CurrencyCode, MarketId


class SalaryPeriod(StrEnum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"
    OTHER = "OTHER"


class SalaryObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    observation_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,119}$")
    market_id: MarketId
    occupation_id: str = Field(min_length=1, max_length=120)
    occupational_classification: str = Field(min_length=2, max_length=160)
    occupational_classification_version: str = Field(min_length=1, max_length=80)
    geographic_region: str | None = Field(default=None, max_length=160)
    salary_value: Decimal = Field(gt=Decimal("0"), max_digits=20, decimal_places=4)
    currency: CurrencyCode
    salary_period: SalaryPeriod
    compensation_definition: str = Field(min_length=3, max_length=300)
    reference_period: str
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,95}$")
    collected_at: datetime

    @field_validator("salary_value", mode="before")
    @classmethod
    def salary_is_finite_and_positive(cls, value: object) -> Decimal:
        try:
            amount = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("salary_value must be a finite positive decimal") from exc
        if not amount.is_finite() or amount <= 0:
            raise ValueError("salary_value must be a finite positive decimal")
        return amount

    @field_validator("reference_period")
    @classmethod
    def salary_period_is_supported(cls, value: str) -> str:
        validate_reference_period(value)
        return value

    @field_validator("collected_at")
    @classmethod
    def collection_timestamp_is_timezone_aware(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("collected_at must include a timezone")
        return value
