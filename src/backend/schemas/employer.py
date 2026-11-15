from datetime import datetime
from enum import StrEnum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from src.backend.schemas.market import MarketId


class EmployerCategory(StrEnum):
    INDIAN_HEADQUARTERED = "INDIAN_HEADQUARTERED"
    MULTINATIONAL_OPERATING_IN_INDIA = "MULTINATIONAL_OPERATING_IN_INDIA"
    OTHER_INTERNATIONAL = "OTHER_INTERNATIONAL"


class EmployerVerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VERIFIED = "VERIFIED"


class EmployerLocationType(StrEnum):
    HEADQUARTERS = "HEADQUARTERS"
    OFFICE = "OFFICE"
    RESEARCH = "RESEARCH"
    OTHER = "OTHER"


class EmployerSourceReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_name: str = Field(min_length=2, max_length=160)
    source_organization: str = Field(min_length=2, max_length=160)
    source_reference: AnyHttpUrl
    collected_at: datetime | None = None

    @field_validator("collected_at")
    @classmethod
    def collection_timestamp_is_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("collected_at must include a timezone")
        return value


class EmployerLocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    city: str = Field(min_length=1, max_length=120)
    state_or_region: str | None = Field(default=None, max_length=120)
    country_code: str = Field(pattern=r"^[A-Z]{2}$")
    location_type: EmployerLocationType
    verification_status: EmployerVerificationStatus = EmployerVerificationStatus.REVIEW_REQUIRED
    verification_source: EmployerSourceReference
    verified_at: datetime | None = None

    @field_validator("verified_at")
    @classmethod
    def verification_timestamp_is_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("verified_at must include a timezone")
        return value

    @model_validator(mode="after")
    def verified_location_has_evidence(self) -> "EmployerLocation":
        if self.verification_status == EmployerVerificationStatus.VERIFIED:
            if self.verification_source is None or self.verified_at is None:
                raise ValueError("verified locations require a verification source and timestamp")
        return self


class EmployerProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    company_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{1,119}$")
    company_name: str = Field(min_length=2, max_length=180)
    headquarters_country: str = Field(pattern=r"^[A-Z]{2}$")
    company_category: EmployerCategory
    industry: str | None = Field(default=None, max_length=160)
    official_website: AnyHttpUrl | None = None
    operating_markets: tuple[MarketId, ...] = ()
    source_references: tuple[EmployerSourceReference, ...] = Field(min_length=1)
    verification_status: EmployerVerificationStatus = EmployerVerificationStatus.REVIEW_REQUIRED
    verified_at: datetime | None = None
    locations: tuple[EmployerLocation, ...] = ()

    @field_validator("operating_markets")
    @classmethod
    def operating_markets_are_unique(cls, value: tuple[MarketId, ...]) -> tuple[MarketId, ...]:
        if len(value) != len(set(value)):
            raise ValueError("operating_markets must be unique")
        return value

    @field_validator("verified_at")
    @classmethod
    def verification_timestamp_is_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("verified_at must include a timezone")
        return value

    @model_validator(mode="after")
    def employer_classification_has_evidence(self) -> "EmployerProfile":
        if self.company_category == EmployerCategory.INDIAN_HEADQUARTERED and self.headquarters_country != "IN":
            raise ValueError("Indian-headquartered employers must have IN headquarters_country")
        if self.company_category == EmployerCategory.MULTINATIONAL_OPERATING_IN_INDIA:
            if self.headquarters_country == "IN" or MarketId.IN not in self.operating_markets:
                raise ValueError("multinationals operating in India require non-IN headquarters and IN operating market")
        if self.verification_status == EmployerVerificationStatus.VERIFIED and self.verified_at is None:
            raise ValueError("verified employers require verified_at")
        return self
