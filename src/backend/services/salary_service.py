"""
Cross-Market Salary Intelligence Service.

Provides source-backed descriptive salary data, dual FX and PPP conversions,
comparability evaluations across 11 dimensions, and integration with the
canonical occupation concordance registry.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from src.backend.schemas.salary import (
    ComparabilityVerdict,
    CrossMarketSalaryComparisonItem,
    CrossMarketSalaryComparisonResult,
    CurrencyRateInfo,
    OccupationSalaryProfile,
    PppFxRatesPayload,
    SalaryPercentiles,
    SalarySourceMeta,
)
from src.backend.services.occupation_service import get_occupation_service

logger = logging.getLogger("jobintel.salary_service")

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "salary"
SOURCES_PATH = DATA_DIR / "sources.json"
PPP_FX_RATES_PATH = DATA_DIR / "ppp_fx_rates.json"
OBSERVATIONS_PATH = DATA_DIR / "observations.json"

COMPARABILITY_DIMENSIONS = (
    "CURRENCY_MISMATCH",
    "PAY_PERIOD_FREQUENCY",
    "PAY_CONCEPT_DEFINITION",
    "SURVEY_POPULATION",
    "OVERTIME_AND_BONUS_TREATMENT",
    "GEOGRAPHIC_COVERAGE",
    "REFERENCE_YEAR_ALIGNMENT",
    "CLASSIFICATION_GRANULARITY",
    "PERCENTILE_AVAILABILITY",
    "SOURCE_METHODOLOGY_TYPE",
    "STATISTICAL_SUPPRESSION_AND_RSE",
)


def _check_uk_publication_gate() -> bool:
    """Evaluate UK ASHE governance publication gate."""
    try:
        from src.backend.routers.uk_salary import require_uk_publication

        require_uk_publication()
        return True
    except Exception:
        return False


class SalaryService:
    """Authoritative service for cross-market descriptive salary intelligence."""

    def __init__(
        self,
        sources_path: Path = SOURCES_PATH,
        rates_path: Path = PPP_FX_RATES_PATH,
        observations_path: Path = OBSERVATIONS_PATH,
    ) -> None:
        self._sources_path = sources_path
        self._rates_path = rates_path
        self._observations_path = observations_path

        self._sources: dict[str, SalarySourceMeta] = {}
        self._rates_payload: PppFxRatesPayload | None = None
        self._observations: dict[str, OccupationSalaryProfile] = {}
        self._observations_by_occ: dict[str, OccupationSalaryProfile] = {}

        self._load_data()

    def _load_data(self) -> None:
        # 1. Load Sources
        with self._sources_path.open("r", encoding="utf-8") as f:
            raw_sources = json.load(f)
        for s in raw_sources:
            meta = SalarySourceMeta.model_validate(s)
            self._sources[meta.source_id] = meta

        # 2. Load Rates
        with self._rates_path.open("r", encoding="utf-8") as f:
            raw_rates = json.load(f)
        self._rates_payload = PppFxRatesPayload.model_validate(raw_rates)

        # 3. Load Observations
        with self._observations_path.open("r", encoding="utf-8") as f:
            raw_obs = json.load(f)
        for o in raw_obs:
            pct_raw = o.get("percentiles", {})
            pct = SalaryPercentiles(
                p10=pct_raw.get("p10"),
                p25=pct_raw.get("p25"),
                p50=pct_raw.get("p50"),
                p75=pct_raw.get("p75"),
                p90=pct_raw.get("p90"),
            )
            src_meta = self._sources.get(o["source_id"])
            p50_val = pct.p50

            # Compute nominal USD and PPP USD for median if available
            nom_usd, ppp_usd = None, None
            if p50_val is not None:
                converted = self.convert_amount(p50_val, o["currency"])
                nom_usd = converted["nominal_usd"]
                ppp_usd = converted["ppp_usd"]

            profile = OccupationSalaryProfile(
                observation_id=o["observation_id"],
                occupation_id=o["occupation_id"],
                occupation_title=o["occupation_title"],
                market_id=o["market_id"],
                source_id=o["source_id"],
                currency=o["currency"],
                period_type=o.get("period_type", "ANNUAL"),
                mean=o.get("mean"),
                percentiles=pct,
                nominal_usd_median=nom_usd,
                ppp_usd_median=ppp_usd,
                sample_size=o.get("sample_size"),
                standard_error=o.get("standard_error"),
                is_suppressed=o.get("is_suppressed", False),
                quality_flag=o.get("quality_flag", "OFFICIAL_STATISTICAL_RELEASE"),
                source_meta=src_meta,
                notes=o.get("notes", ""),
            )
            self._observations[profile.observation_id] = profile
            self._observations_by_occ[profile.occupation_id] = profile

        logger.info(
            "Loaded SalaryService: sources=%d, observations=%d",
            len(self._sources),
            len(self._observations),
        )

    # -----------------------------------------------------------------
    # Retrieval APIs
    # -----------------------------------------------------------------

    def list_sources(self, active_only: bool = True) -> list[SalarySourceMeta]:
        sources = list(self._sources.values())
        if active_only:
            return [s for s in sources if s.is_active]
        return sources

    def get_source(self, source_id: str) -> SalarySourceMeta | None:
        return self._sources.get(source_id)

    def get_ppp_fx_rates(self) -> PppFxRatesPayload:
        if self._rates_payload is None:
            raise RuntimeError("Rates payload not initialized")
        return self._rates_payload

    def list_observations(
        self, market_id: str | None = None
    ) -> list[OccupationSalaryProfile]:
        obs = list(self._observations.values())
        if market_id:
            obs = [o for o in obs if o.market_id.upper() == market_id.upper()]
        return obs

    def get_observation(self, observation_id: str) -> OccupationSalaryProfile | None:
        return self._observations.get(observation_id)

    def get_salary_profile_for_occupation(
        self, occupation_id: str
    ) -> OccupationSalaryProfile | None:
        profile = self._observations_by_occ.get(occupation_id)
        if profile and profile.market_id == "UK":
            # Check fail-closed governance gate for UK
            if not _check_uk_publication_gate():
                raise HTTPException(
                    status_code=503,
                    detail={
                        "code": "UK_DATA_NOT_PUBLISHED",
                        "message": "UK salary analytics are not currently published due to active governance gate.",
                    },
                )
        return profile

    # -----------------------------------------------------------------
    # Conversion Engine (Strict Separation of Nominal FX and PPP)
    # -----------------------------------------------------------------

    def convert_amount(self, amount: float, from_currency: str) -> dict[str, float]:
        """Convert amount to Nominal USD and PPP USD with explicit multipliers."""
        if self._rates_payload is None:
            raise RuntimeError("Rates payload not loaded")

        rates = self._rates_payload.rates
        curr_upper = from_currency.upper()
        if curr_upper not in rates:
            raise ValueError(f"Unsupported currency: {from_currency}")

        info: CurrencyRateInfo = rates[curr_upper]
        nominal_usd = round(amount * info.nominal_usd_multiplier, 2)
        ppp_usd = round(amount * info.ppp_usd_multiplier, 2)

        return {
            "original_amount": amount,
            "original_currency": curr_upper,
            "nominal_usd": nominal_usd,
            "ppp_usd": ppp_usd,
            "nominal_fx_to_usd": info.nominal_fx_to_usd,
            "ppp_factor_to_usd": info.ppp_conversion_factor_to_usd,
        }

    def convert_percentiles(
        self, percentiles: SalaryPercentiles, currency: str
    ) -> tuple[dict[str, float | None], dict[str, float | None]]:
        nom_dict: dict[str, float | None] = {}
        ppp_dict: dict[str, float | None] = {}
        for p_name in ("p10", "p25", "p50", "p75", "p90"):
            val = getattr(percentiles, p_name)
            if val is not None:
                conv = self.convert_amount(val, currency)
                nom_dict[p_name] = conv["nominal_usd"]
                ppp_dict[p_name] = conv["ppp_usd"]
            else:
                nom_dict[p_name] = None
                ppp_dict[p_name] = None
        return nom_dict, ppp_dict

    # -----------------------------------------------------------------
    # Cross-Market Comparability Evaluation Engine
    # -----------------------------------------------------------------

    def evaluate_comparability(
        self,
        source_profile: OccupationSalaryProfile,
        target_profile: OccupationSalaryProfile,
        relationship_type: str,
        confidence_score: float,
    ) -> tuple[ComparabilityVerdict, list[str]]:
        caveats: list[str] = []

        # 1. Gate / Suppression check
        if target_profile.is_suppressed or target_profile.percentiles.p50 is None:
            caveats.append(
                "Target occupation salary data is suppressed or unavailable."
            )
            return ComparabilityVerdict.INSUFFICIENT_DATA, caveats

        if source_profile.is_suppressed or source_profile.percentiles.p50 is None:
            caveats.append(
                "Source occupation salary data is suppressed or unavailable."
            )
            return ComparabilityVerdict.INSUFFICIENT_DATA, caveats

        # 2. Currency mismatch check
        rates = self.get_ppp_fx_rates().rates
        if source_profile.currency != target_profile.currency:
            t_rate = rates.get(target_profile.currency)
            fx_rate = t_rate.nominal_fx_to_usd if t_rate else 1.0
            ppp_fac = t_rate.ppp_conversion_factor_to_usd if t_rate else 1.0
            caveats.append(
                f"Currency conversion applied: {target_profile.currency} values converted using "
                f"Nominal FX (1 USD = {fx_rate} {target_profile.currency}) and "
                f"World Bank ICP 2024 PPP factor (1 Int$ = {ppp_fac} {target_profile.currency}). "
                "Nominal reflects global market value; PPP reflects local domestic purchasing power."
            )

        # 3. Pay concept differences
        src_concept = (
            source_profile.source_meta.pay_concept
            if source_profile.source_meta
            else ""
        )
        tgt_concept = (
            target_profile.source_meta.pay_concept
            if target_profile.source_meta
            else ""
        )

        if "CTC" in tgt_concept or "CTC" in src_concept:
            caveats.append(
                "Pay Concept Disparity: India uses Cost to Company (CTC) including employer statutory "
                "contributions (PF, gratuity), whereas other markets measure gross cash earnings or straight-time wages."
            )

        if "AWS" in tgt_concept or "13th month" in tgt_concept:
            caveats.append(
                "Bonus Structure: Singapore MOM figures include Annual Wage Supplement (AWS / 13th month bonus)."
            )

        if "straight-time" in tgt_concept or "straight-time" in src_concept:
            caveats.append(
                "Overtime & Bonus Treatment: US BLS OEWS excludes overtime premiums and non-production bonuses."
            )

        # 4. Source methodology difference
        if (
            source_profile.quality_flag == "MODEL_PREDICTION"
            or target_profile.quality_flag == "MODEL_PREDICTION"
        ):
            caveats.append(
                "Methodological Divergence: One observation is a statistical ML model / vacancy benchmark, "
                "while the comparator is an official national statistical survey."
            )

        # 5. Reference year difference
        src_ref = (
            source_profile.source_meta.reference_period
            if source_profile.source_meta
            else ""
        )
        tgt_ref = (
            target_profile.source_meta.reference_period
            if target_profile.source_meta
            else ""
        )
        if src_ref and tgt_ref and src_ref != tgt_ref:
            caveats.append(
                f"Reference Period: Source measured in {src_ref}; target measured in {tgt_ref}."
            )

        # 6. Classification relationship caveats
        if relationship_type in ("BROADER_THAN", "NARROWER_THAN"):
            caveats.append(
                f"Classification Asymmetry: Concordance relationship is {relationship_type} "
                f"(confidence score: {confidence_score:.2f}). Roles cover different task scopes."
            )

        # Determine Verdict
        if (
            source_profile.quality_flag == "MODEL_PREDICTION"
            or target_profile.quality_flag == "MODEL_PREDICTION"
            or relationship_type in ("BROADER_THAN", "NARROWER_THAN")
            or confidence_score < 0.88
        ):
            verdict = ComparabilityVerdict.COMPARABLE_WITH_MAJOR_CAVEATS
        elif (
            source_profile.currency != target_profile.currency
            or "AWS" in tgt_concept
            or src_ref != tgt_ref
        ):
            verdict = ComparabilityVerdict.COMPARABLE_WITH_ADJUSTMENTS
        else:
            verdict = (
                ComparabilityVerdict.DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS
            )

        return verdict, caveats

    # -----------------------------------------------------------------
    # Cross-Market Salary Comparison Workflow
    # -----------------------------------------------------------------

    def compare_occupation_salaries(
        self, source_occupation_id: str
    ) -> CrossMarketSalaryComparisonResult:
        occ_svc = get_occupation_service()
        try:
            source_occ = occ_svc.get_occupation(source_occupation_id)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Occupation '{source_occupation_id}' not found.",
            )

        # Check UK publication gate if source occupation is UK
        if source_occ.market_id == "UK":
            if not _check_uk_publication_gate():
                raise HTTPException(
                    status_code=503,
                    detail={
                        "code": "UK_DATA_NOT_PUBLISHED",
                        "message": "UK salary analytics are not currently published due to active governance gate.",
                    },
                )

        source_profile = self._observations_by_occ.get(source_occupation_id)
        if not source_profile:
            raise HTTPException(
                status_code=404,
                detail=f"No salary observation registered for occupation '{source_occupation_id}'.",
            )

        # Retrieve direct concordance matches from OccupationService
        occ_matches_res = occ_svc.compare_across_markets(source_occupation_id)

        uk_published = _check_uk_publication_gate()
        comparisons: list[CrossMarketSalaryComparisonItem] = []

        seen_occ_ids: set[str] = {source_occupation_id}

        # 1. Process direct matches
        for m in occ_matches_res.matches:
            target_occ_id = getattr(m.target_occupation, "occupation_id", None)
            if not target_occ_id or target_occ_id in seen_occ_ids:
                continue
            seen_occ_ids.add(target_occ_id)

            tgt_profile = self._observations_by_occ.get(target_occ_id)
            if not tgt_profile:
                continue

            # UK publication gate check on target
            if tgt_profile.market_id == "UK" and not uk_published:
                comparisons.append(
                    CrossMarketSalaryComparisonItem(
                        market_id="UK",
                        occupation_id=target_occ_id,
                        occupation_title=tgt_profile.occupation_title,
                        relationship_to_source=m.relationship_type.value,
                        relationship_type=m.relationship_type.value,
                        confidence_score=float(m.confidence_score),
                        source_id=tgt_profile.source_id,
                        currency="GBP",
                        original_currency="GBP",
                        original_median=None,
                        nominal_usd_median=None,
                        ppp_usd_median=None,
                        percentiles_original={
                            "p10": None,
                            "p25": None,
                            "p50": None,
                            "p75": None,
                            "p90": None,
                        },
                        percentiles_nominal_usd={
                            "p10": None,
                            "p25": None,
                            "p50": None,
                            "p75": None,
                            "p90": None,
                        },
                        percentiles_ppp_usd={
                            "p10": None,
                            "p25": None,
                            "p50": None,
                            "p75": None,
                            "p90": None,
                        },
                        comparability_verdict=ComparabilityVerdict.INSUFFICIENT_DATA,
                        comparability_caveats=(
                            "UK ASHE salary publication is withheld by governance policy gate (fail-closed HTTP 503 policy).",
                        ),
                        is_suppressed=True,
                        quality_flag="GOVERNANCE_WITHHELD",
                        notes="Data withheld pending UK publication approval.",
                    )
                )
                continue

            # Converted percentiles
            nom_pcts, ppp_pcts = self.convert_percentiles(
                tgt_profile.percentiles, tgt_profile.currency
            )
            verdict, caveats = self.evaluate_comparability(
                source_profile,
                tgt_profile,
                m.relationship_type.value,
                float(m.confidence_score),
            )

            orig_pcts = {
                "p10": tgt_profile.percentiles.p10,
                "p25": tgt_profile.percentiles.p25,
                "p50": tgt_profile.percentiles.p50,
                "p75": tgt_profile.percentiles.p75,
                "p90": tgt_profile.percentiles.p90,
            }

            comparisons.append(
                CrossMarketSalaryComparisonItem(
                    market_id=tgt_profile.market_id,
                    occupation_id=tgt_profile.occupation_id,
                    occupation_title=tgt_profile.occupation_title,
                    relationship_to_source=m.relationship_type.value,
                    relationship_type=m.relationship_type.value,
                    confidence_score=float(m.confidence_score),
                    source_id=tgt_profile.source_id,
                    currency=tgt_profile.currency,
                    original_currency=tgt_profile.currency,
                    original_median=tgt_profile.percentiles.p50,
                    nominal_usd_median=tgt_profile.nominal_usd_median,
                    ppp_usd_median=tgt_profile.ppp_usd_median,
                    percentiles_original=orig_pcts,
                    percentiles_nominal_usd=nom_pcts,
                    percentiles_ppp_usd=ppp_pcts,
                    comparability_verdict=verdict,
                    comparability_caveats=tuple(caveats),
                    is_suppressed=tgt_profile.is_suppressed,
                    quality_flag=tgt_profile.quality_flag,
                    notes=tgt_profile.notes,
                )
            )

        # 2. Canonical cohort discovery: if some markets are missing in direct mappings,
        # discover peers through shared canonical concept links
        canonical_links = [
            m
            for m in occ_matches_res.matches
            if hasattr(m.target_occupation, "canonical_occupation_id")
        ]
        all_mappings = [
            mapping
            for m_list in occ_svc._mappings_by_source.values()
            for mapping in m_list
        ]

        for c_link in canonical_links:
            can_id = getattr(c_link.target_occupation, "canonical_occupation_id")
            # find all national occupations that link to this canonical concept
            cohort_nat_ids = [
                m.source_occupation_id
                for m in all_mappings
                if m.target_occupation_id == can_id
                and m.source_occupation_id not in seen_occ_ids
            ]
            for cohort_id in cohort_nat_ids:
                seen_occ_ids.add(cohort_id)
                cohort_profile = self._observations_by_occ.get(cohort_id)
                if not cohort_profile:
                    continue

                if cohort_profile.market_id == "UK" and not uk_published:
                    comparisons.append(
                        CrossMarketSalaryComparisonItem(
                            market_id="UK",
                            occupation_id=cohort_id,
                            occupation_title=cohort_profile.occupation_title,
                            relationship_to_source=f"CANONICAL_COHORT ({can_id})",
                            relationship_type="CANONICAL_COHORT",
                            confidence_score=0.85,
                            source_id=cohort_profile.source_id,
                            currency="GBP",
                            original_currency="GBP",
                            original_median=None,
                            nominal_usd_median=None,
                            ppp_usd_median=None,
                            percentiles_original={
                                "p10": None,
                                "p25": None,
                                "p50": None,
                                "p75": None,
                                "p90": None,
                            },
                            percentiles_nominal_usd={
                                "p10": None,
                                "p25": None,
                                "p50": None,
                                "p75": None,
                                "p90": None,
                            },
                            percentiles_ppp_usd={
                                "p10": None,
                                "p25": None,
                                "p50": None,
                                "p75": None,
                                "p90": None,
                            },
                            comparability_verdict=ComparabilityVerdict.INSUFFICIENT_DATA,
                            comparability_caveats=(
                                "UK ASHE salary publication is withheld by governance policy gate (fail-closed HTTP 503 policy).",
                            ),
                            is_suppressed=True,
                            quality_flag="GOVERNANCE_WITHHELD",
                            notes="Data withheld pending UK publication approval.",
                        )
                    )
                    continue

                nom_pcts, ppp_pcts = self.convert_percentiles(
                    cohort_profile.percentiles, cohort_profile.currency
                )
                verdict, caveats = self.evaluate_comparability(
                    source_profile,
                    cohort_profile,
                    "CANONICAL_COHORT",
                    0.85,
                )
                caveats.append(
                    f"Concordance via Canonical Concept: Mapped through shared canonical concept '{can_id}'."
                )

                orig_pcts = {
                    "p10": cohort_profile.percentiles.p10,
                    "p25": cohort_profile.percentiles.p25,
                    "p50": cohort_profile.percentiles.p50,
                    "p75": cohort_profile.percentiles.p75,
                    "p90": cohort_profile.percentiles.p90,
                }

                comparisons.append(
                    CrossMarketSalaryComparisonItem(
                        market_id=cohort_profile.market_id,
                        occupation_id=cohort_profile.occupation_id,
                        occupation_title=cohort_profile.occupation_title,
                        relationship_to_source=f"CANONICAL_COHORT ({can_id})",
                        relationship_type="CANONICAL_COHORT",
                        confidence_score=0.85,
                        source_id=cohort_profile.source_id,
                        currency=cohort_profile.currency,
                        original_currency=cohort_profile.currency,
                        original_median=cohort_profile.percentiles.p50,
                        nominal_usd_median=cohort_profile.nominal_usd_median,
                        ppp_usd_median=cohort_profile.ppp_usd_median,
                        percentiles_original=orig_pcts,
                        percentiles_nominal_usd=nom_pcts,
                        percentiles_ppp_usd=ppp_pcts,
                        comparability_verdict=verdict,
                        comparability_caveats=tuple(caveats),
                        is_suppressed=cohort_profile.is_suppressed,
                        quality_flag=cohort_profile.quality_flag,
                        notes=cohort_profile.notes,
                    )
                )

        rates_data = self.get_ppp_fx_rates()

        disclaimer = (
            "Cross-market salary comparisons are descriptive benchmarks compiled from official national "
            "statistical releases and validated models. Nominal conversions use market foreign exchange rates; "
            "PPP conversions use World Bank International Comparison Program (ICP) 2024 consumption factors. "
            "Because compensation definitions (CTC vs gross cash pay), tax regimes, and bonus practices differ "
            "fundamentally across jurisdictions, figures MUST NOT be interpreted as single-currency wage parity."
        )

        return CrossMarketSalaryComparisonResult(
            source_occupation_id=source_profile.occupation_id,
            source_occupation_title=source_profile.occupation_title,
            source_market_id=source_profile.market_id,
            source_currency=source_profile.currency,
            source_median_original=source_profile.percentiles.p50,
            source_median_nominal_usd=source_profile.nominal_usd_median,
            source_median_ppp_usd=source_profile.ppp_usd_median,
            comparisons=tuple(comparisons),
            fx_rates_metadata={
                "base_currency": rates_data.base_currency,
                "reference_year": rates_data.reference_year,
                "fx_description": rates_data.methodology.get(
                    "fx_description", ""
                ),
            },
            ppp_factors_metadata={
                "base_currency": rates_data.base_currency,
                "reference_year": rates_data.reference_year,
                "ppp_description": rates_data.methodology.get(
                    "ppp_description", ""
                ),
            },
            methodology_disclaimer=disclaimer,
            comparability_dimensions=COMPARABILITY_DIMENSIONS,
        )


_DEFAULT_SALARY_SERVICE: SalaryService | None = None


def get_salary_service() -> SalaryService:
    global _DEFAULT_SALARY_SERVICE
    if _DEFAULT_SALARY_SERVICE is None:
        _DEFAULT_SALARY_SERVICE = SalaryService()
    return _DEFAULT_SALARY_SERVICE
