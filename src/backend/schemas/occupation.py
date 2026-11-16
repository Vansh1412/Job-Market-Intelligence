from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from src.backend.schemas.market import MarketId


class ClassificationId(StrEnum):
    UK_SOC_2020 = "UK_SOC_2020"
    US_SOC_2018 = "US_SOC_2018"
    AU_OSCA_2024 = "AU_OSCA_2024"
    AU_ANZSCO_2022 = "AU_ANZSCO_2022"
    SG_SSOC_2024 = "SG_SSOC_2024"
    SG_SSOC_2020 = "SG_SSOC_2020"
    IN_NCO_2015 = "IN_NCO_2015"
    INT_ISCO_08 = "INT_ISCO_08"


class RelationshipType(StrEnum):
    EXACT_MATCH = "EXACT_MATCH"
    CLOSE_MATCH = "CLOSE_MATCH"
    BROADER_THAN = "BROADER_THAN"
    NARROWER_THAN = "NARROWER_THAN"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"
    NO_SUPPORTED_MAPPING = "NO_SUPPORTED_MAPPING"


class MappingMethodology(StrEnum):
    OFFICIAL_CROSSWALK = "OFFICIAL_CROSSWALK"
    EXPERT_ASSESSMENT = "EXPERT_ASSESSMENT"
    CALIBRATED_TASK_OVERLAP = "CALIBRATED_TASK_OVERLAP"


class ReviewStatus(StrEnum):
    VERIFIED_OFFICIAL = "VERIFIED_OFFICIAL"
    VERIFIED_REVIEWED = "VERIFIED_REVIEWED"
    DERIVED_HIGH_CONFIDENCE = "DERIVED_HIGH_CONFIDENCE"
    DERIVED_MEDIUM_CONFIDENCE = "DERIVED_MEDIUM_CONFIDENCE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNMAPPED = "UNMAPPED"
    REJECTED = "REJECTED"


class TargetType(StrEnum):
    NATIONAL = "NATIONAL"
    CANONICAL = "CANONICAL"


class ClassificationSystem(BaseModel):
    model_config = ConfigDict(frozen=True)

    classification_id: str = Field(min_length=3, max_length=40)
    market_id: str = Field(min_length=2, max_length=10)
    official_title: str = Field(min_length=3, max_length=160)
    version_edition: str = Field(min_length=2, max_length=60)
    issuing_authority: str = Field(min_length=3, max_length=120)
    code_format: str = Field(min_length=3, max_length=60)
    hierarchy_levels: tuple[str, ...] = Field(min_length=1, max_length=8)
    is_active: bool = True
    source_reference: AnyHttpUrl
    license_attribution: str = Field(min_length=3, max_length=240)


class NationalOccupation(BaseModel):
    model_config = ConfigDict(frozen=True)

    occupation_id: str = Field(min_length=3, max_length=60)
    classification_id: str = Field(min_length=3, max_length=40)
    market_id: str = Field(min_length=2, max_length=10)
    occupation_code: str = Field(min_length=1, max_length=30)
    occupation_title: str = Field(min_length=2, max_length=240)
    official_definition: str = Field(min_length=10, max_length=3000)
    tasks: tuple[str, ...] = ()
    entry_qualifications: str | None = Field(default=None, max_length=800)
    hierarchy_level: str = Field(min_length=2, max_length=60)
    parent_code: str | None = Field(default=None, max_length=30)
    is_leaf: bool = True
    alternate_titles: tuple[str, ...] = ()
    task_provenance: Literal["OFFICIAL_VERBATIM", "OFFICIALLY_DERIVED", "JOBINTEL_CURATED"] = "OFFICIAL_VERBATIM"

    @model_validator(mode="after")
    def validate_occupation_id(self) -> NationalOccupation:
        expected_prefix = f"{self.classification_id}:"
        if not self.occupation_id.startswith(expected_prefix):
            raise ValueError(f"occupation_id must start with '{expected_prefix}'")
        return self


class CanonicalOccupation(BaseModel):
    model_config = ConfigDict(frozen=True)

    canonical_occupation_id: str = Field(pattern=r"^CAN_OCC_[A-Z0-9_]+$")
    preferred_title: str = Field(min_length=3, max_length=120)
    concept_family: str = Field(min_length=3, max_length=80)
    description: str = Field(min_length=15, max_length=3000)
    core_competencies: tuple[str, ...] = Field(min_length=1)
    status: Literal["ACTIVE", "DEPRECATED", "PROVISIONAL"] = "ACTIVE"


class OccupationMapping(BaseModel):
    model_config = ConfigDict(frozen=True)

    mapping_id: str = Field(min_length=3, max_length=80)
    source_occupation_id: str = Field(min_length=3, max_length=60)
    target_occupation_id: str = Field(min_length=3, max_length=60)
    target_type: TargetType
    relationship_type: RelationshipType
    confidence_score: Decimal = Field(ge=Decimal("0.0"), le=Decimal("1.0"), max_digits=4, decimal_places=2)
    review_status: ReviewStatus
    methodology: MappingMethodology
    evidence_sources: tuple[str, ...] = Field(min_length=1)
    notes_and_limitations: str = Field(max_length=1500)
    reviewer: str = Field(min_length=2, max_length=100)
    effective_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    created_at: str = Field(min_length=10, max_length=40)

    @model_validator(mode="after")
    def validate_confidence_policy(self) -> OccupationMapping:
        # Rule: synthetic 1.00 is only permitted for VERIFIED_OFFICIAL
        if self.confidence_score == Decimal("1.0") and self.review_status != ReviewStatus.VERIFIED_OFFICIAL:
            raise ValueError("confidence_score of 1.0 is strictly reserved for VERIFIED_OFFICIAL mappings")
        # Rule: UNMAPPED and REJECTED must have 0.0 confidence
        if self.review_status in (ReviewStatus.UNMAPPED, ReviewStatus.REJECTED) and self.confidence_score != Decimal("0.0"):
            raise ValueError("UNMAPPED or REJECTED mappings must have confidence_score 0.0")
        if self.relationship_type == RelationshipType.NO_SUPPORTED_MAPPING and self.confidence_score != Decimal("0.0"):
            raise ValueError("NO_SUPPORTED_MAPPING relationships must have confidence_score 0.0")
        return self


class OccupationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    occupation_id: str
    classification_id: str
    market_id: str
    occupation_code: str
    occupation_title: str
    hierarchy_level: str
    is_leaf: bool


class OccupationPage(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: tuple[NationalOccupation, ...]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_count: int = Field(ge=0)
    has_next: bool


class CrossMarketMatchItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_occupation: NationalOccupation | CanonicalOccupation
    target_type: TargetType
    target_market_id: str
    relationship_type: RelationshipType
    confidence_score: Decimal
    review_status: ReviewStatus
    methodology: MappingMethodology
    evidence_sources: tuple[str, ...]
    notes_and_limitations: str
    approximation_warning: str | None = None
    task_similarity: float | None = None


class CrossMarketComparisonResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_occupation: NationalOccupation
    matches: tuple[CrossMarketMatchItem, ...]
    unmapped_markets: tuple[str, ...]
    total_matches: int


class ConcordanceCoverageStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_national_occupations: int
    mapped_national_occupations: int
    unmapped_national_occupations: int
    total_canonical_concepts: int
    linked_canonical_concepts: int
    unlinked_canonical_concepts: int
    mappings_by_relationship: dict[str, int]
    mappings_by_review_status: dict[str, int]
    official_mappings_count: int
    expert_reviewed_mappings_count: int
    total_mappings: int


class TaskSimilarityPayload(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    target_id: str
    source_title: str
    target_title: str
    source_task_count: int
    target_task_count: int
    jaccard_similarity: float
    tfidf_cosine_similarity: float
    metric_type: str = "UNSUPERVISED_LEXICAL_SIMILARITY"
    calibration_status: str = "UNEMPIRICAL_HEURISTIC_SEPARATE_METRIC"
    limitations: str = (
        "Unsupervised lexical overlap metric based on word frequencies. "
        "Does NOT constitute empirical probability or calibrated confidence of occupational interchangeability."
    )

