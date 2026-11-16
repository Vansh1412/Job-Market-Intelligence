"""Job Demand Intelligence Pydantic schemas and contract definitions.

Supports multi-market occupational demand observations, metric metadata,
trend calculations, regional breakdowns, skill requirements, comparability,
and skill gap analysis across US, UK, AU, SG, and IN.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.backend.schemas.market import MarketId


class DemandMetricType(StrEnum):
    """Classification of the underlying demand measurement instrument.

    Heterogeneous demand instruments measure distinct economic constructs and
    must never be combined into a single collapsed score.
    """

    OBSERVED_JOB_ADVERTISEMENTS = "OBSERVED_JOB_ADVERTISEMENTS"
    OBSERVED_VACANCIES = "OBSERVED_VACANCIES"
    ANNUAL_JOB_OPENINGS = "ANNUAL_JOB_OPENINGS"
    EMPLOYMENT_LEVEL = "EMPLOYMENT_LEVEL"
    EMPLOYMENT_CHANGE = "EMPLOYMENT_CHANGE"
    PROJECTED_EMPLOYMENT_CHANGE = "PROJECTED_EMPLOYMENT_CHANGE"
    SHORTAGE_INDICATOR = "SHORTAGE_INDICATOR"
    SKILL_REQUIREMENT = "SKILL_REQUIREMENT"


class DemandProvenance(StrEnum):
    """Semantic classification of observation provenance."""

    OFFICIAL_PUBLISHED = "OFFICIAL_PUBLISHED"
    OFFICIALLY_DERIVED = "OFFICIALLY_DERIVED"
    JOBINTEL_CURATED = "JOBINTEL_CURATED"
    JOBINTEL_MODEL_ESTIMATE = "JOBINTEL_MODEL_ESTIMATE"
    SYNTHETIC_TEST_FIXTURE = "SYNTHETIC_TEST_FIXTURE"
    UNVERIFIED = "UNVERIFIED"


PROVENANCE_METADATA: dict[DemandProvenance, dict[str, str]] = {
    DemandProvenance.OFFICIAL_PUBLISHED: {
        "label": "Official statistic",
        "description": "Directly extracted from official government statistical agency releases or statutory censuses with no computational transformation.",
    },
    DemandProvenance.OFFICIALLY_DERIVED: {
        "label": "Derived from official data",
        "description": "Produced through reproducible calculation, annualization, employment-weighting, or taxonomy concordance from verified official input statistics.",
    },
    DemandProvenance.JOBINTEL_CURATED: {
        "label": "JobIntel research benchmark",
        "description": "Curated research benchmark compiled and validated by JobIntel Research Labs from empirical industry posting samples.",
    },
    DemandProvenance.JOBINTEL_MODEL_ESTIMATE: {
        "label": "Model-derived estimate",
        "description": "Econometric or machine learning model estimate based on multi-source feature modeling.",
    },
    DemandProvenance.SYNTHETIC_TEST_FIXTURE: {
        "label": "Test data",
        "description": "Synthetically generated test fixture for system validation. Not for real-world interpretation.",
    },
    DemandProvenance.UNVERIFIED: {
        "label": "Verification pending",
        "description": "Source provenance or licensing verification is currently pending review.",
    },
}


class PublicationStatus(StrEnum):
    """Source licensing and publication gate status."""

    PUBLISHED = "PUBLISHED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    WITHHELD = "WITHHELD"


class DemandTrendDirection(StrEnum):
    """Directional trend classification for an occupational demand series."""

    STRONG_GROWTH = "STRONG_GROWTH"        # > +10%
    MODERATE_GROWTH = "MODERATE_GROWTH"    # +2% to +10%
    STABLE = "STABLE"                      # -2% to +2%
    MODERATE_DECLINE = "MODERATE_DECLINE"  # -10% to -2%
    STRONG_DECLINE = "STRONG_DECLINE"      # < -10%
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ShortageStatus(StrEnum):
    """Official government shortage or recruitment difficulty rating."""

    NATIONAL_SHORTAGE = "NATIONAL_SHORTAGE"
    REGIONAL_SHORTAGE = "REGIONAL_SHORTAGE"
    NO_SHORTAGE = "NO_SHORTAGE"
    NOT_ASSESSED = "NOT_ASSESSED"


class DemandComparabilityVerdict(StrEnum):
    """Verdict on cross-market comparability between two demand observations."""

    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"
    DIRECTIONALLY_COMPARABLE = "DIRECTIONALLY_COMPARABLE"
    METHODOLOGICALLY_DISTINCT = "METHODOLOGICALLY_DISTINCT"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SkillCategory(StrEnum):
    """Categorisation of skills for demand profiling and gap analysis."""

    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    FRAMEWORK_LIBRARY = "FRAMEWORK_LIBRARY"
    CLOUD_DEVOPS = "CLOUD_DEVOPS"
    DATABASE_DATA = "DATABASE_DATA"
    ARCHITECTURE_SYSTEM_DESIGN = "ARCHITECTURE_SYSTEM_DESIGN"
    SECURITY_COMPLIANCE = "SECURITY_COMPLIANCE"
    CORE_ENGINEERING_PRACTICE = "CORE_ENGINEERING_PRACTICE"
    SOFT_SKILL_MANAGEMENT = "SOFT_SKILL_MANAGEMENT"


class DemandMetricDefinition(BaseModel):
    """Metadata describing a specific demand metric type."""

    model_config = ConfigDict(frozen=True)

    metric_type: DemandMetricType
    display_name: str
    unit: str
    description: str
    underlying_construct: str
    limitations: list[str]
    comparability_class: str


class DemandTimeSeriesPoint(BaseModel):
    """Single point in an occupational demand time-series or projection."""

    model_config = ConfigDict(frozen=True)

    period: str
    value: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    is_projected: bool = False


class RegionalDemandPoint(BaseModel):
    """Geographic or state/territory breakdown of demand for an occupation."""

    model_config = ConfigDict(frozen=True)

    region_code: str
    region_name: str
    value: float
    share_percentage: float | None = None
    index_vs_national: float | None = None
    is_derived: bool = False
    derivation_method: str | None = None
    disclosure_label: str | None = None


class SkillDemandItem(BaseModel):
    """Demand profile for a specific skill within an occupation."""

    model_config = ConfigDict(frozen=True)

    skill_name: str
    category: SkillCategory
    importance_score: float = Field(ge=0.0, le=100.0)
    frequency_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    growth_rate: float | None = None
    is_hot_skill: bool = False


class DemandObservation(BaseModel):
    """Individual demand observation grounded in an official statistical source."""

    model_config = ConfigDict(frozen=True)

    observation_id: str
    market_id: MarketId
    occupation_id: str
    canonical_id: str | None = None
    source_id: str
    metric_type: DemandMetricType
    metric_unit: str
    value: float | None = None
    reference_period: str
    geographic_scope: str = "National"
    time_series: list[DemandTimeSeriesPoint] = Field(default_factory=list)
    regional_breakdown: list[RegionalDemandPoint] = Field(default_factory=list)
    shortage_status: ShortageStatus = ShortageStatus.NOT_ASSESSED
    future_demand_rating: str | None = None
    percent_unfilled_over_6_months: float | None = None
    typical_education: str | None = None
    work_experience_required: str | None = None
    data_quality_grade: str = "OFFICIAL_STATISTICS"
    notes: str | None = None
    provenance: DemandProvenance = DemandProvenance.OFFICIALLY_DERIVED
    provenance_label: str = "Derived from official data"
    provenance_description: str = ""
    transformation_method: str | None = None
    derivation_summary: str | None = None


class OccupationDemandProfile(BaseModel):
    """Aggregated demand profile for an occupation within a national market."""

    model_config = ConfigDict(frozen=True)

    occupation_id: str
    occupation_title: str
    market_id: MarketId
    canonical_id: str | None = None
    canonical_title: str | None = None
    primary_metric_type: DemandMetricType
    primary_metric_value: float | None = None
    primary_metric_unit: str
    reference_period: str
    trend_direction: DemandTrendDirection
    trend_percentage_change: float | None = None
    trend_time_series: list[DemandTimeSeriesPoint] = Field(default_factory=list)
    regional_distribution: list[RegionalDemandPoint] = Field(default_factory=list)
    top_skills: list[SkillDemandItem] = Field(default_factory=list)
    shortage_status: ShortageStatus = ShortageStatus.NOT_ASSESSED
    future_demand_rating: str | None = None
    unfilled_rate_over_6_months: float | None = None
    entry_requirements: dict[str, str] = Field(default_factory=dict)
    source_attributions: list[dict[str, Any]] = Field(default_factory=list)
    methodology_disclaimers: list[str] = Field(default_factory=list)
    provenance: DemandProvenance = DemandProvenance.OFFICIALLY_DERIVED
    provenance_label: str = "Derived from official data"
    provenance_description: str = ""
    transformation_method: str | None = None
    derivation_summary: str | None = None
    regional_disclosure: str | None = None
    occupation_inheritance_disclosure: str | None = None
    benchmark_disclosure: str | None = None
    publication_gate_active: bool = False
    publication_gate_code: str | None = None
    publication_gate_message: str | None = None


class DemandComparabilityDimensionResult(BaseModel):
    """Evaluation result for one of the 11 comparability dimensions."""

    model_config = ConfigDict(frozen=True)

    dimension: str
    market_a_value: str
    market_b_value: str
    match: bool
    severity: str  # "NONE", "LOW", "MODERATE", "CRITICAL"
    comment: str


class DemandComparisonResult(BaseModel):
    """Detailed comparability verdict and breakdown between two national observations."""

    model_config = ConfigDict(frozen=True)

    canonical_id: str
    canonical_title: str
    market_a: MarketId
    market_b: MarketId
    occupation_a_id: str
    occupation_b_id: str
    verdict: DemandComparabilityVerdict
    verdict_summary: str
    dimension_evaluations: list[DemandComparabilityDimensionResult]
    warnings: list[str] = Field(default_factory=list)
    metric_a: dict[str, Any]
    metric_b: dict[str, Any]


class SkillGapAnalysisRequest(BaseModel):
    """User request to analyze skill gaps against a target occupation profile."""

    model_config = ConfigDict(frozen=True)

    target_occupation_id: str
    market_id: MarketId
    user_skills: list[str]


class SkillGapItem(BaseModel):
    """Detail of a single missing skill."""

    model_config = ConfigDict(frozen=True)

    skill_name: str
    category: SkillCategory
    importance_score: float
    frequency_percentage: float | None = None
    priority: str  # "CRITICAL", "HIGH", "NICE_TO_HAVE"


class SkillGapAnalysisResult(BaseModel):
    """Result of skill gap analysis with actionable learning recommendations."""

    model_config = ConfigDict(frozen=True)

    target_occupation_id: str
    target_occupation_title: str
    market_id: MarketId
    user_skills_submitted: list[str]
    matched_skills: list[str]
    missing_critical_skills: list[SkillGapItem] = Field(default_factory=list)
    missing_secondary_skills: list[SkillGapItem] = Field(default_factory=list)
    match_percentage: float
    matched_skill_weight: float = 0.0
    total_required_weight: float = 0.0
    formula_explanation: str = "Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100"
    methodology_notes: str = (
        "Skill coverage measures alignment between candidate skills and employer-requested "
        "competencies for the occupation. It is not an employability probability, hiring "
        "probability, or placement guarantee."
    )
    readiness_level: str  # "HIGH", "MODERATE", "EMERGING", "FOUNDATIONAL"
    recommendations: list[str] = Field(default_factory=list)
