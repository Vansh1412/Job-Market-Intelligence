from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

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


class ComparabilityVerdict(StrEnum):
    DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS = "DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS"
    COMPARABLE_WITH_ADJUSTMENTS = "COMPARABLE_WITH_ADJUSTMENTS"
    COMPARABLE_WITH_MAJOR_CAVEATS = "COMPARABLE_WITH_MAJOR_CAVEATS"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SalaryPercentiles(BaseModel):
    model_config = ConfigDict(frozen=True)

    p10: float | None = None
    p25: float | None = None
    p50: float | None = None
    p75: float | None = None
    p90: float | None = None


class SalarySourceMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    market_id: str
    authority: str
    publication_name: str
    reference_period: str
    release_date: str
    license: str
    currency: str
    pay_concept: str
    frequency: str
    sample_coverage: str
    source_url: str
    is_active: bool = True
    governance_gate: str | None = None


class CurrencyRateInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    market_id: str
    nominal_fx_to_usd: float
    nominal_usd_multiplier: float
    ppp_conversion_factor_to_usd: float
    ppp_usd_multiplier: float
    fx_source: str
    ppp_source: str


class PppFxRatesPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    base_currency: str
    reference_year: str
    methodology: dict[str, str]
    rates: dict[str, CurrencyRateInfo]


class OccupationSalaryProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    observation_id: str
    occupation_id: str
    occupation_title: str
    market_id: str
    source_id: str
    currency: str
    period_type: str = "ANNUAL"
    mean: float | None = None
    percentiles: SalaryPercentiles
    nominal_usd_median: float | None = None
    ppp_usd_median: float | None = None
    sample_size: int | None = None
    standard_error: float | None = None
    is_suppressed: bool = False
    quality_flag: str
    source_meta: SalarySourceMeta | None = None
    notes: str


class CrossMarketSalaryComparisonItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_id: str
    occupation_id: str
    occupation_title: str
    relationship_to_source: str
    relationship_type: str
    confidence_score: float
    source_id: str
    currency: str
    original_currency: str
    original_median: float | None
    nominal_usd_median: float | None
    ppp_usd_median: float | None
    percentiles_original: dict[str, float | None]
    percentiles_nominal_usd: dict[str, float | None]
    percentiles_ppp_usd: dict[str, float | None]
    comparability_verdict: ComparabilityVerdict
    comparability_caveats: tuple[str, ...]
    is_suppressed: bool = False
    quality_flag: str
    notes: str


class CrossMarketSalaryComparisonResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_occupation_id: str
    source_occupation_title: str
    source_market_id: str
    source_currency: str
    source_median_original: float | None
    source_median_nominal_usd: float | None
    source_median_ppp_usd: float | None
    comparisons: tuple[CrossMarketSalaryComparisonItem, ...]
    fx_rates_metadata: dict[str, Any]
    ppp_factors_metadata: dict[str, Any]
    methodology_disclaimer: str
    comparability_dimensions: tuple[str, ...]


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
