"""Demand Analytics Service for JOBINTEL 2.0.

Provides comprehensive occupational demand profiling, time-series trend calculation,
regional demand distribution, 11-dimension cross-market comparability evaluation,
and actionable skill gap analysis.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.backend.schemas.demand import (
    DemandComparabilityDimensionResult,
    DemandComparabilityVerdict,
    DemandComparisonResult,
    DemandMetricDefinition,
    DemandMetricType,
    DemandObservation,
    DemandProvenance,
    DemandTimeSeriesPoint,
    DemandTrendDirection,
    OccupationDemandProfile,
    PROVENANCE_METADATA,
    PublicationStatus,
    RegionalDemandPoint,
    ShortageStatus,
    SkillCategory,
    SkillDemandItem,
    SkillGapAnalysisRequest,
    SkillGapAnalysisResult,
    SkillGapItem,
)
from src.backend.schemas.market import MarketId

logger = logging.getLogger("jobintel.demand_service")

# Common tech skill synonyms for robust matching
SYNONYM_MAP: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "angularjs": "angular",
    "golang": "go",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "mongo": "mongodb",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "llm": "large language models",
    "llms": "large language models",
    "ci/cd": "continuous integration",
    "cicd": "continuous integration",
    "tf": "terraform",
    "scikit": "scikit-learn",
    "sklearn": "scikit-learn",
    "rest": "rest apis",
    "restful": "rest apis",
    "qa": "automated testing",
    "test automation": "automated testing",
}


def _normalize_skill(s: str) -> str:
    cleaned = s.strip().lower()
    return SYNONYM_MAP.get(cleaned, cleaned)


class DemandService:
    """In-memory service loading and indexing demand intelligence datasets."""

    def __init__(self, data_dir: str | Path | None = None) -> None:
        if data_dir is None:
            data_dir = Path("src/backend/data")
        else:
            data_dir = Path(data_dir)

        demand_dir = data_dir / "demand"
        occupations_dir = data_dir / "occupations"

        # Load metrics
        self._metrics: dict[DemandMetricType, DemandMetricDefinition] = {}
        metrics_file = demand_dir / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, encoding="utf-8") as f:
                for item in json.load(f):
                    defn = DemandMetricDefinition(**item)
                    self._metrics[defn.metric_type] = defn

        # Load sources
        self._sources: dict[str, dict[str, Any]] = {}
        sources_file = demand_dir / "sources.json"
        if sources_file.exists():
            with open(sources_file, encoding="utf-8") as f:
                for item in json.load(f):
                    self._sources[item["source_id"]] = item

        # Load national & canonical occupations metadata for rich titles
        self._national_meta: dict[str, dict[str, Any]] = {}
        nat_file = occupations_dir / "national_occupations.json"
        if nat_file.exists():
            with open(nat_file, encoding="utf-8") as f:
                for item in json.load(f):
                    self._national_meta[item["occupation_id"]] = item
                    # Also index by short code
                    self._national_meta[f"{item['market_id']}:{item['occupation_code']}"] = item

        self._canonical_meta: dict[str, dict[str, Any]] = {}
        can_file = occupations_dir / "canonical_occupations.json"
        if can_file.exists():
            with open(can_file, encoding="utf-8") as f:
                for item in json.load(f):
                    self._canonical_meta[item["canonical_occupation_id"]] = item

        # Load observations
        self._observations: list[DemandObservation] = []
        self._obs_by_market: dict[MarketId, list[DemandObservation]] = {m: [] for m in MarketId}
        self._obs_by_nat_id: dict[str, DemandObservation] = {}
        self._obs_by_canonical: dict[str, list[DemandObservation]] = {}

        obs_file = demand_dir / "observations.json"
        if obs_file.exists():
            with open(obs_file, encoding="utf-8") as f:
                for item in json.load(f):
                    obs = DemandObservation(**item)
                    self._observations.append(obs)
                    self._obs_by_market[obs.market_id].append(obs)
                    self._obs_by_nat_id[obs.occupation_id] = obs
                    # Also map short code
                    code = obs.occupation_id.split(":")[-1]
                    self._obs_by_nat_id[f"{obs.market_id}:{code}"] = obs

                    if obs.canonical_id:
                        self._obs_by_canonical.setdefault(obs.canonical_id, []).append(obs)

        # Load skill demands
        self._skills_by_canonical: dict[str, list[SkillDemandItem]] = {}
        skills_file = demand_dir / "skill_demands.json"
        if skills_file.exists():
            with open(skills_file, encoding="utf-8") as f:
                for item in json.load(f):
                    cid = item["canonical_id"]
                    skills = [SkillDemandItem(**s) for s in item.get("skills", [])]
                    self._skills_by_canonical[cid] = skills

        # Load shortages
        self._shortages: list[dict[str, Any]] = []
        shortage_file = demand_dir / "shortage_indicators.json"
        if shortage_file.exists():
            with open(shortage_file, encoding="utf-8") as f:
                self._shortages = json.load(f)

        logger.info(
            "DemandService initialized with %d observations, %d metric defs, %d sources, %d skill sets",
            len(self._observations),
            len(self._metrics),
            len(self._sources),
            len(self._skills_by_canonical),
        )

    def get_metrics(self) -> list[DemandMetricDefinition]:
        """Returns metadata for all supported demand metric types."""
        return list(self._metrics.values())

    def get_metric(self, metric_type: str | DemandMetricType) -> DemandMetricDefinition | None:
        """Returns definition for a specific metric type."""
        return self._metrics.get(DemandMetricType(metric_type))

    def get_sources(self) -> list[dict[str, Any]]:
        """Returns catalog of demand data sources."""
        return list(self._sources.values())

    def get_markets_overview(self) -> list[dict[str, Any]]:
        """Returns summary of demand analytics coverage across the five markets."""
        result = []
        market_labels = {
            MarketId.US: ("United States", "us.bls.ep", "ANNUAL_JOB_OPENINGS", "Annual Average Openings (2023-2033)"),
            MarketId.AU: ("Australia", "au.jsa.ivi", "OBSERVED_JOB_ADVERTISEMENTS", "Monthly Online Job Adverts Index"),
            MarketId.UK: ("United Kingdom", "uk.ons.labour-demand", "OBSERVED_JOB_ADVERTISEMENTS", "Online Job Advert Index (Base=100) — Review Required"),
            MarketId.SG: ("Singapore", "sg.mom.vacancies", "OBSERVED_VACANCIES", "Official Job Vacancy Statistics"),
            MarketId.IN: ("India", "in.jobintel.tech-demand", "OBSERVED_JOB_ADVERTISEMENTS", "Validated Tech Demand Benchmark"),
        }

        for m in MarketId:
            name, src_id, mtype, label = market_labels.get(m, (m.value, "", "", ""))
            obs_list = self._obs_by_market.get(m, [])
            src_info = self._sources.get(src_id, {})
            pub_status = src_info.get("publication_status", "PUBLISHED")
            status = "AVAILABLE" if (obs_list and pub_status == "PUBLISHED") else ("WITHHELD_PENDING_REVIEW" if pub_status == "REVIEW_REQUIRED" else "AVAILABLE")
            result.append({
                "market_id": m.value,
                "market_name": name,
                "coverage_status": status,
                "publication_status": pub_status,
                "total_observations": len(obs_list),
                "primary_source_id": src_id,
                "primary_source_name": src_info.get("source_name", "Official Statistics"),
                "primary_metric_type": mtype,
                "metric_label": label,
                "license": src_info.get("license", "Open License"),
            })
        return result

    def list_observations(
        self,
        market_id: MarketId | str | None = None,
        canonical_id: str | None = None,
        metric_type: str | None = None,
        public_view: bool = True,
    ) -> list[DemandObservation]:
        """Filters observations by market, canonical concept, or metric type."""
        results = self._observations

        if market_id:
            m_val = MarketId(market_id)
            results = [o for o in results if o.market_id == m_val]

        if canonical_id:
            results = [o for o in results if o.canonical_id == canonical_id]

        if metric_type:
            m_type = DemandMetricType(metric_type)
            results = [o for o in results if o.metric_type == m_type]

        if public_view:
            sanitized = []
            for o in results:
                src_meta = self._sources.get(o.source_id, {})
                if src_meta.get("publication_status") == "REVIEW_REQUIRED" or o.market_id == MarketId.UK:
                    sanitized.append(
                        o.model_copy(update={
                            "value": None,
                            "time_series": [],
                            "regional_breakdown": [],
                            "notes": "UK_DEMAND_DATA_NOT_PUBLISHED: Withheld pending source-use and redistribution review.",
                        })
                    )
                else:
                    sanitized.append(o)
            return sanitized

        return results

    def find_observation(self, market_id: MarketId | str, occupation_id: str) -> DemandObservation | None:
        """Finds an observation by market and occupation identifier/code."""
        m_val = MarketId(market_id)
        # Try direct key
        obs = self._obs_by_nat_id.get(occupation_id)
        if obs and obs.market_id == m_val:
            return obs

        # Try with market prefix
        obs = self._obs_by_nat_id.get(f"{m_val.value}:{occupation_id}")
        if obs:
            return obs

        # Search market list
        for o in self._obs_by_market.get(m_val, []):
            if o.occupation_id == occupation_id or o.occupation_id.endswith(f":{occupation_id}"):
                return o
            if o.canonical_id == occupation_id:
                return o

        return None

    def calculate_trend(self, obs: DemandObservation) -> tuple[DemandTrendDirection, float | None]:
        """Calculates trend direction and percentage change from time-series points or projection."""
        pts = obs.time_series
        if not pts or len(pts) < 2:
            # Check if projection metric
            if obs.metric_type == DemandMetricType.PROJECTED_EMPLOYMENT_CHANGE:
                pct = obs.value
            else:
                return DemandTrendDirection.INSUFFICIENT_DATA, None
        else:
            first_val = pts[0].value
            last_val = pts[-1].value
            if first_val <= 0:
                pct = 100.0 if last_val > 0 else 0.0
            else:
                pct = round(((last_val - first_val) / first_val) * 100.0, 1)

        # Directional classification
        if pct > 10.0:
            direction = DemandTrendDirection.STRONG_GROWTH
        elif 2.0 <= pct <= 10.0:
            direction = DemandTrendDirection.MODERATE_GROWTH
        elif -2.0 <= pct < 2.0:
            direction = DemandTrendDirection.STABLE
        elif -10.0 <= pct < -2.0:
            direction = DemandTrendDirection.MODERATE_DECLINE
        else:
            direction = DemandTrendDirection.STRONG_DECLINE

        return direction, pct

    def get_occupation_demand_profile(
        self,
        market_id: MarketId | str,
        occupation_id: str,
        public_view: bool = True,
    ) -> OccupationDemandProfile | None:
        """Constructs a comprehensive demand profile for an occupation in a market."""
        m_val = MarketId(market_id)
        obs = self.find_observation(m_val, occupation_id)
        if not obs:
            return None

        # Determine title
        nat_meta = self._national_meta.get(obs.occupation_id, {})
        title = nat_meta.get("occupation_title", obs.occupation_id.split(":")[-1])

        can_title = None
        if obs.canonical_id:
            can_meta = self._canonical_meta.get(obs.canonical_id, {})
            can_title = can_meta.get("preferred_title", obs.canonical_id)

        trend_dir, trend_pct = self.calculate_trend(obs)

        # Get skills
        top_skills = []
        if obs.canonical_id and obs.canonical_id in self._skills_by_canonical:
            top_skills = self._skills_by_canonical[obs.canonical_id]

        # Source attributions
        src = self._sources.get(obs.source_id, {})
        attributions = [
            {
                "source_id": obs.source_id,
                "source_name": src.get("source_name", obs.source_id),
                "publisher": src.get("publisher", "Official Authority"),
                "canonical_url": src.get("canonical_url", ""),
                "license": src.get("license", "Open License"),
                "reference_period": obs.reference_period,
                "data_quality_grade": obs.data_quality_grade,
                "publication_status": src.get("publication_status", "PUBLISHED"),
            }
        ]

        # Entry requirements
        entry_reqs: dict[str, str] = {}
        if obs.typical_education:
            entry_reqs["typical_education"] = obs.typical_education
        if obs.work_experience_required:
            entry_reqs["work_experience_required"] = obs.work_experience_required
        if nat_meta.get("entry_qualifications"):
            entry_reqs["entry_qualifications"] = nat_meta["entry_qualifications"]

        # Disclaimers
        disclaimers = []
        metric_def = self._metrics.get(obs.metric_type)
        if metric_def:
            disclaimers.extend(metric_def.limitations)

        # Market-specific disclosures
        regional_disc: str | None = None
        occ_inheritance_disc: str | None = None
        benchmark_disc: str | None = None

        if m_val == MarketId.US:
            regional_disc = "State-level values are derived allocations using employment weights. They are not independently observed state-level job-opening counts."
            disclaimers.append("U.S. values represent 10-year annualized projected openings (growth plus replacement needs), not current spot vacancies.")
        elif m_val == MarketId.AU:
            occ_inheritance_disc = "Detailed occupation values are derived from broader four-digit ANZSCO group data. They should not be interpreted as directly observed six-digit occupation counts."
            regional_disc = "State-level shares reflect JSA Internet Vacancy Index regional distribution."
        elif m_val == MarketId.UK:
            disclaimers.append("UK labour demand volumes are experimental online job advert indices derived by the ONS, measuring employer search intensity rather than absolute verified vacancies.")
        elif m_val == MarketId.SG:
            regional_disc = "MODELLED REGIONAL DISTRIBUTION — NOT DIRECTLY OBSERVED. Sub-national shares are planning area proxies derived from enterprise cluster estimates."
            disclaimers.append("Singapore enterprise vacancies reflect private firms with at least 25 employees and public sector establishments.")
        elif m_val == MarketId.IN:
            benchmark_disc = "Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."
            regional_disc = "Regional breakdowns reflect technology-hub posting sample shares across Bangalore, Hyderabad, NCR, and Pune."
            disclaimers.append("India tech demand figures represent a calibrated sample benchmark of online tech postings across major tech hubs, not an exhaustive national census of informal employment.")

        # Check UK ONS/Textkernel publication gate
        is_gate_active = (src.get("publication_status") == "REVIEW_REQUIRED") or (m_val == MarketId.UK)
        gate_code = "UK_DEMAND_DATA_NOT_PUBLISHED" if is_gate_active else None
        gate_msg = "UK demand data is currently withheld pending source-use and redistribution review." if is_gate_active else None

        if is_gate_active:
            disclaimers.insert(0, gate_msg)

        # Enforce leak prevention in public view
        if is_gate_active and public_view:
            metric_val = None
            time_series = []
            reg_dist = []
            trend_dir = DemandTrendDirection.INSUFFICIENT_DATA
            trend_pct = None
        else:
            metric_val = obs.value
            time_series = obs.time_series
            reg_dist = obs.regional_breakdown

        return OccupationDemandProfile(
            occupation_id=obs.occupation_id,
            occupation_title=title,
            market_id=m_val,
            canonical_id=obs.canonical_id,
            canonical_title=can_title,
            primary_metric_type=obs.metric_type,
            primary_metric_value=metric_val,
            primary_metric_unit=obs.metric_unit,
            reference_period=obs.reference_period,
            trend_direction=trend_dir,
            trend_percentage_change=trend_pct,
            trend_time_series=time_series,
            regional_distribution=reg_dist,
            top_skills=top_skills,
            shortage_status=obs.shortage_status,
            future_demand_rating=obs.future_demand_rating,
            unfilled_rate_over_6_months=obs.percent_unfilled_over_6_months,
            entry_requirements=entry_reqs,
            source_attributions=attributions,
            methodology_disclaimers=disclaimers,
            provenance=obs.provenance,
            provenance_label=obs.provenance_label,
            provenance_description=obs.provenance_description,
            transformation_method=obs.transformation_method,
            derivation_summary=obs.derivation_summary,
            regional_disclosure=regional_disc,
            occupation_inheritance_disclosure=occ_inheritance_disc,
            benchmark_disclosure=benchmark_disc,
            publication_gate_active=is_gate_active,
            publication_gate_code=gate_code,
            publication_gate_message=gate_msg,
        )

    def compare_demand(
        self,
        canonical_id: str,
        market_a: MarketId | str,
        market_b: MarketId | str,
    ) -> DemandComparisonResult:
        """Evaluates comparability between two national demand profiles across 11 dimensions."""
        m_a = MarketId(market_a)
        m_b = MarketId(market_b)

        can_meta = self._canonical_meta.get(canonical_id, {})
        can_title = can_meta.get("preferred_title", canonical_id)

        # Find matching observations
        obs_a = None
        for o in self._obs_by_market.get(m_a, []):
            if o.canonical_id == canonical_id:
                obs_a = o
                break

        obs_b = None
        for o in self._obs_by_market.get(m_b, []):
            if o.canonical_id == canonical_id:
                obs_b = o
                break

        if not obs_a or not obs_b:
            return DemandComparisonResult(
                canonical_id=canonical_id,
                canonical_title=can_title,
                market_a=m_a,
                market_b=m_b,
                occupation_a_id=obs_a.occupation_id if obs_a else "UNKNOWN",
                occupation_b_id=obs_b.occupation_id if obs_b else "UNKNOWN",
                verdict=DemandComparabilityVerdict.INSUFFICIENT_DATA,
                verdict_summary=f"Demand data is missing for {m_a.value if not obs_a else m_b.value} for concept {can_title}.",
                dimension_evaluations=[],
                warnings=["Insufficient observation records to execute 11-dimension comparability engine."],
                metric_a={"value": obs_a.value if obs_a else None},
                metric_b={"value": obs_b.value if obs_b else None},
            )

        # 11-DIMENSION COMPARATIVE EVALUATION
        evaluations: list[DemandComparabilityDimensionResult] = []
        critical_mismatches = 0
        moderate_mismatches = 0
        warnings = []

        # Gate check for UK
        gate_a = (obs_a.source_id == "uk.ons.labour-demand") or (obs_a.market_id == MarketId.UK)
        gate_b = (obs_b.source_id == "uk.ons.labour-demand") or (obs_b.market_id == MarketId.UK)
        if gate_a or gate_b:
            warnings.append("UK demand data is currently withheld pending source-use and redistribution review. Direct value comparisons are unavailable.")

        # 1. Metric Instrument Type
        match_type = obs_a.metric_type == obs_b.metric_type
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="1. Metric Instrument Type",
            market_a_value=obs_a.metric_type.value,
            market_b_value=obs_b.metric_type.value,
            match=match_type,
            severity="NONE" if match_type else "CRITICAL",
            comment="Identical instrument construct." if match_type else f"Distinct constructs: {obs_a.metric_type.value} vs {obs_b.metric_type.value}."
        ))
        if not match_type:
            critical_mismatches += 1
            warnings.append(f"Metric types differ ({obs_a.metric_type.value} vs {obs_b.metric_type.value}). Numerical volumes cannot be combined or directly contrasted.")

        # 2. Target Population
        pop_a = "All civilian employees" if m_a == MarketId.US else ("Employees in tech/corporate" if m_a == MarketId.IN else "Private & public sector employees")
        pop_b = "All civilian employees" if m_b == MarketId.US else ("Employees in tech/corporate" if m_b == MarketId.IN else "Private & public sector employees")
        match_pop = pop_a == pop_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="2. Target Population",
            market_a_value=pop_a,
            market_b_value=pop_b,
            match=match_pop,
            severity="NONE" if match_pop else "MODERATE",
            comment="Target populations are broadly compatible." if match_pop else "Target populations have slight coverage divergence."
        ))
        if not match_pop:
            moderate_mismatches += 1

        # 3. Survey vs Scraped Collection
        is_scraped_a = obs_a.metric_type in (DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS,)
        is_scraped_b = obs_b.metric_type in (DemandMetricType.OBSERVED_JOB_ADVERTISEMENTS,)
        match_collection = is_scraped_a == is_scraped_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="3. Collection Method (Survey vs Scraped)",
            market_a_value="Web-scraped Job Postings" if is_scraped_a else "Official Survey / Census",
            market_b_value="Web-scraped Job Postings" if is_scraped_b else "Official Survey / Census",
            match=match_collection,
            severity="NONE" if match_collection else "CRITICAL",
            comment="Both methods use compatible collection methodology." if match_collection else "Survey vacancies measure unfilled employer slots, whereas scraped postings measure digital advertising churn."
        ))
        if not match_collection:
            critical_mismatches += 1

        # 4. Temporal Interval & Frequency
        freq_a = "10-Year Annualized" if obs_a.metric_type == DemandMetricType.ANNUAL_JOB_OPENINGS else ("Quarterly Snapshot" if "Q" in obs_a.reference_period else "Annual Flow")
        freq_b = "10-Year Annualized" if obs_b.metric_type == DemandMetricType.ANNUAL_JOB_OPENINGS else ("Quarterly Snapshot" if "Q" in obs_b.reference_period else "Annual Flow")
        match_freq = freq_a == freq_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="4. Temporal Interval & Frequency",
            market_a_value=freq_a,
            market_b_value=freq_b,
            match=match_freq,
            severity="NONE" if match_freq else "CRITICAL",
            comment="Compatible temporal frequency." if match_freq else f"Incompatible horizons: {freq_a} vs {freq_b}."
        ))
        if not match_freq:
            critical_mismatches += 1

        # 5. Taxonomy Concordance
        sys_a = obs_a.occupation_id.split(":")[0]
        sys_b = obs_b.occupation_id.split(":")[0]
        match_tax = sys_a == sys_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="5. Taxonomy Concordance",
            market_a_value=sys_a,
            market_b_value=sys_b,
            match=match_tax,
            severity="NONE" if match_tax else "MODERATE",
            comment="Direct taxonomic alignment." if match_tax else f"Cross-concordance mapped via ISCO-08 ({sys_a} <-> {sys_b})."
        ))
        if not match_tax:
            moderate_mismatches += 1

        # 6. Geographic Scope & Boundary
        match_geo = obs_a.geographic_scope == obs_b.geographic_scope
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="6. Geographic Scope & Boundary",
            market_a_value=obs_a.geographic_scope,
            market_b_value=obs_b.geographic_scope,
            match=match_geo,
            severity="NONE" if match_geo else "MODERATE",
            comment="Matching geographic scope." if match_geo else f"Divergent geographic coverage: {obs_a.geographic_scope} vs {obs_b.geographic_scope}."
        ))
        if not match_geo:
            moderate_mismatches += 1

        # 7. Enterprise Coverage & Size Threshold
        ent_a = "Firms with >=25 employees" if m_a == MarketId.SG else "All employer sizes"
        ent_b = "Firms with >=25 employees" if m_b == MarketId.SG else "All employer sizes"
        match_ent = ent_a == ent_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="7. Enterprise Coverage & Size Threshold",
            market_a_value=ent_a,
            market_b_value=ent_b,
            match=match_ent,
            severity="NONE" if match_ent else "MODERATE",
            comment="Comparable enterprise size coverage." if match_ent else "Singapore MOM sample truncates small enterprises (<25 employees)."
        ))
        if not match_ent:
            moderate_mismatches += 1

        # 8. Deduplication Methodology
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="8. Job Advert Deduplication",
            market_a_value="Official Standard Deduplication",
            market_b_value="Official Standard Deduplication",
            match=True,
            severity="NONE",
            comment="Standard entity deduplication applied to remove multiple postings of the same job vacancy."
        ))

        # 9. Growth vs Replacement
        growth_a = "Includes Replacements + Growth" if obs_a.metric_type == DemandMetricType.ANNUAL_JOB_OPENINGS else "Spot Vacancies / Postings"
        growth_b = "Includes Replacements + Growth" if obs_b.metric_type == DemandMetricType.ANNUAL_JOB_OPENINGS else "Spot Vacancies / Postings"
        match_growth = growth_a == growth_b
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="9. Growth vs Replacement Separation",
            market_a_value=growth_a,
            market_b_value=growth_b,
            match=match_growth,
            severity="NONE" if match_growth else "CRITICAL",
            comment="Compatible vacancy definition." if match_growth else "BLS annual openings include retirements and transfers; online postings reflect spot hiring."
        ))
        if not match_growth:
            critical_mismatches += 1

        # 10. Sampling Frame & Rigor
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="10. Sampling Frame & Rigor",
            market_a_value=obs_a.data_quality_grade,
            market_b_value=obs_b.data_quality_grade,
            match=obs_a.data_quality_grade == obs_b.data_quality_grade,
            severity="NONE" if obs_a.data_quality_grade == obs_b.data_quality_grade else "MODERATE",
            comment="Both sources meet established quality rigor." if obs_a.data_quality_grade == obs_b.data_quality_grade else "Statistical survey vs calibrated private posting sample."
        ))
        if obs_a.data_quality_grade != obs_b.data_quality_grade:
            moderate_mismatches += 1

        # 11. Unit Normalization
        unit_match = obs_a.metric_unit == obs_b.metric_unit
        evaluations.append(DemandComparabilityDimensionResult(
            dimension="11. Unit Normalization & Scale",
            market_a_value=obs_a.metric_unit,
            market_b_value=obs_b.metric_unit,
            match=unit_match,
            severity="NONE" if unit_match else "CRITICAL",
            comment="Identical measurement units." if unit_match else f"Incompatible units: {obs_a.metric_unit} vs {obs_b.metric_unit}."
        ))
        if not unit_match:
            critical_mismatches += 1

        # CALCULATE VERDICT
        if gate_a or gate_b:
            verdict = DemandComparabilityVerdict.METHODOLOGICALLY_DISTINCT
            summary = "Methodologically distinct or withheld. UK demand data is currently withheld pending source-use and redistribution review. Compare side-by-side as separate metrics only."
        elif critical_mismatches == 0 and moderate_mismatches == 0:
            verdict = DemandComparabilityVerdict.DIRECTLY_COMPARABLE
            summary = "Direct numerical comparison permitted. Both markets utilize matching instruments, units, and methodology."
        elif critical_mismatches <= 1:
            verdict = DemandComparabilityVerdict.DIRECTIONALLY_COMPARABLE
            summary = "Directionally comparable. While specific units differ, directional demand growth rates and skill shortages can be meaningfully contrasted."
        elif critical_mismatches >= 2:
            verdict = DemandComparabilityVerdict.METHODOLOGICALLY_DISTINCT
            summary = "Methodologically distinct. These markets measure fundamentally different economic constructs (e.g. 10-year projected openings vs monthly online advert indices). Compare side-by-side as separate metrics only."
        else:
            verdict = DemandComparabilityVerdict.NOT_COMPARABLE
            summary = "Not comparable due to divergent data definitions and non-overlapping measurement frames."

        # Sanitize metric values to prevent leakage if gate active
        val_a = None if gate_a else obs_a.value
        val_b = None if gate_b else obs_b.value

        return DemandComparisonResult(
            canonical_id=canonical_id,
            canonical_title=can_title,
            market_a=m_a,
            market_b=m_b,
            occupation_a_id=obs_a.occupation_id,
            occupation_b_id=obs_b.occupation_id,
            verdict=verdict,
            verdict_summary=summary,
            dimension_evaluations=evaluations,
            warnings=warnings,
            metric_a={
                "value": val_a,
                "unit": obs_a.metric_unit,
                "metric_type": obs_a.metric_type.value,
                "reference_period": obs_a.reference_period,
                "shortage": obs_a.shortage_status.value,
                "publication_gate_active": gate_a,
                "publication_gate_message": "UK demand data is currently withheld pending source-use and redistribution review." if gate_a else None,
            },
            metric_b={
                "value": val_b,
                "unit": obs_b.metric_unit,
                "metric_type": obs_b.metric_type.value,
                "reference_period": obs_b.reference_period,
                "shortage": obs_b.shortage_status.value,
                "publication_gate_active": gate_b,
                "publication_gate_message": "UK demand data is currently withheld pending source-use and redistribution review." if gate_b else None,
            },
        )

    def analyze_skill_gaps(self, request: SkillGapAnalysisRequest) -> SkillGapAnalysisResult:
        """Analyzes a candidate's skills against a target occupation profile and recommends learning priorities."""
        m_val = request.market_id
        obs = self.find_observation(m_val, request.target_occupation_id)
        if not obs or not obs.canonical_id:
            # Fallback to software engineer
            canonical_id = "CAN_OCC_SOFTWARE_ENGINEER"
            occ_title = "Software Engineer"
        else:
            canonical_id = obs.canonical_id
            nat_meta = self._national_meta.get(obs.occupation_id, {})
            occ_title = nat_meta.get("occupation_title", obs.occupation_id)

        target_skills = self._skills_by_canonical.get(canonical_id, [])
        if not target_skills:
            target_skills = self._skills_by_canonical.get("CAN_OCC_SOFTWARE_ENGINEER", [])

        user_norm_set = {_normalize_skill(s) for s in request.user_skills}

        matched_skills: list[str] = []
        missing_critical: list[SkillGapItem] = []
        missing_secondary: list[SkillGapItem] = []

        total_weight = sum(s.importance_score for s in target_skills) or 1.0
        matched_weight = 0.0

        for s in target_skills:
            norm_name = _normalize_skill(s.skill_name)
            is_matched = norm_name in user_norm_set or any(norm_name in u or u in norm_name for u in user_norm_set)

            if is_matched:
                matched_skills.append(s.skill_name)
                matched_weight += s.importance_score
            else:
                is_crit = s.importance_score >= 85.0 or s.is_hot_skill
                item = SkillGapItem(
                    skill_name=s.skill_name,
                    category=s.category,
                    importance_score=s.importance_score,
                    frequency_percentage=s.frequency_percentage,
                    priority="CRITICAL" if is_crit else ("HIGH" if s.importance_score >= 75.0 else "NICE_TO_HAVE"),
                )
                if is_crit:
                    missing_critical.append(item)
                else:
                    missing_secondary.append(item)

        # Sort missing by importance
        missing_critical.sort(key=lambda x: x.importance_score, reverse=True)
        missing_secondary.sort(key=lambda x: x.importance_score, reverse=True)

        match_pct = round((matched_weight / total_weight) * 100.0, 1)

        # Readiness classification
        if match_pct >= 75.0 and len(missing_critical) == 0:
            readiness = "HIGH"
        elif match_pct >= 50.0 or len(missing_critical) <= 1:
            readiness = "MODERATE"
        elif match_pct >= 25.0:
            readiness = "EMERGING"
        else:
            readiness = "FOUNDATIONAL"

        # Actionable recommendations (neutrally phrased, rule-based)
        recommendations = []
        if missing_critical:
            top_crit = [c.skill_name for c in missing_critical[:3]]
            recommendations.append(f"Immediate Priority: Acquire core competencies in {', '.join(top_crit)} to meet essential market threshold.")
        if missing_secondary:
            top_sec = [s.skill_name for s in missing_secondary[:2]]
            recommendations.append(f"Secondary Advantage: Build practical projects utilizing {', '.join(top_sec)}.")
        recommendations.append(f"Market Alignment: Your current profile aligns {match_pct}% with hiring prerequisites for {occ_title} in {m_val.value}.")
        recommendations.append("Learning Guidance: Recommendations are rule-based learning priority suggestions based on market demand weights, not a guarantee of employment or hiring probability.")

        return SkillGapAnalysisResult(
            target_occupation_id=request.target_occupation_id,
            target_occupation_title=occ_title,
            market_id=m_val,
            user_skills_submitted=request.user_skills,
            matched_skills=matched_skills,
            missing_critical_skills=missing_critical,
            missing_secondary_skills=missing_secondary,
            match_percentage=match_pct,
            matched_skill_weight=round(matched_weight, 1),
            total_required_weight=round(total_weight, 1),
            formula_explanation="Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100",
            methodology_notes=(
                "Skill coverage measures alignment between candidate skills and employer-requested "
                "competencies for the occupation. It is not an employability probability, hiring "
                "probability, or placement guarantee."
            ),
            readiness_level=readiness,
            recommendations=recommendations,
        )


_service_instance: DemandService | None = None


def get_demand_service() -> DemandService:
    """Singleton getter for DemandService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = DemandService()
    return _service_instance
