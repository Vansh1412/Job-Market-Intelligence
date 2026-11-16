# JOBINTEL 2.0 — SPRINT 3B.2
## SPRINT 3B.2 DATA DICTIONARY: GLOBAL JOB DEMAND INTELLIGENCE

**Document ID:** `SPRINT3B2_DATA_DICTIONARY`  
**Milestone:** Sprint 3B.2 — Phase 2 Data Modeling & Schema Specification  
**Date:** 2026-11-16  
**Auditor / Authors:** Principal Data Scientist, Data Governance Architect, Backend Architect  
**Target Branch:** `staging/sprint2c3`  
**Baseline Commit:** `58974134e56b4c3ec6b6119b7b4739e9cce857f3`  

---

### 1. OVERVIEW

This data dictionary formalizes the entities, data structures, fields, constraints, and relationships supporting the Global Job Demand Intelligence subsystem in JOBINTEL 2.0.

The design strictly reflects the principles established in Sprint 3B.2 Phase 0 and Phase 1:
- Demand metrics from different national statistical sources represent fundamentally different economic phenomena.
- All entities support provenance tracking, uncertainty representation, and strict non-collapsibility.

---

### 2. CORE ENUMERATIONS

#### 2.1 `DemandMetricType`
Classifies the underlying measurement instrument.

| Enum Value | Description | Typical Source | Unit of Measurement |
| :--- | :--- | :--- | :--- |
| `OBSERVED_JOB_ADVERTISEMENTS` | Online job advert postings or advert index collected via web scraping/job boards. | AU JSA IVI, UK ONS Labour Demand, IN Tech Postings | Adverts / Index |
| `OBSERVED_VACANCIES` | Active, unfilled positions reported by employer establishment surveys. | SG MOM Job Vacancies | Vacancies (Count) |
| `ANNUAL_JOB_OPENINGS` | Projected average annual openings from employment expansion plus net replacements/transfers. | US BLS Employment Projections | Annual Openings |
| `EMPLOYMENT_LEVEL` | Total employed headcount or percentage share in an occupational category. | IN MOSPI PLFS, US BLS Base Emp | Persons / Percentage |
| `EMPLOYMENT_CHANGE` | Historical net change in total employed persons over a defined observation window. | Statistical census/survey | Persons / Percentage |
| `PROJECTED_EMPLOYMENT_CHANGE` | Estimated net percentage growth or decline in total employment over a projection horizon. | US BLS 10-Year Projections | Percentage Change |
| `SHORTAGE_INDICATOR` | Official government assessment of labour market tightness or recruitment bottlenecks. | AU JSA SPL, UK Immigration Salary List | Categorical Rating |
| `SKILL_REQUIREMENT` | Relative importance, posting frequency, or proficiency level of a skill in an occupation. | US O*NET, SG SSG, Job Postings | Importance (0-100) / % |

#### 2.2 `DemandTrendDirection`
Directional classification computed from time-series points or projection rates.

| Enum Value | Criterion | Description |
| :--- | :--- | :--- |
| `STRONG_GROWTH` | Change > +10.0% | High expansion / rapid increase in demand volume |
| `MODERATE_GROWTH` | +2.0% ≤ Change ≤ +10.0% | Steady, positive demand expansion |
| `STABLE` | -2.0% ≤ Change < +2.0% | Demand remains flat or within normal variance |
| `MODERATE_DECLINE` | -10.0% ≤ Change < -2.0% | Contraction in demand volumes or projections |
| `STRONG_DECLINE` | Change < -10.0% | Severe demand contraction |
| `INSUFFICIENT_DATA` | < 2 data points or uncomputable | Cannot establish a reliable trend direction |

#### 2.3 `ShortageStatus`
Official administrative shortage designations.

| Enum Value | Description |
| :--- | :--- |
| `NATIONAL_SHORTAGE` | Officially certified as in acute nationwide shortage / recruitment difficulty. |
| `REGIONAL_SHORTAGE` | Shortage recognized in specific geographic states or territories only. |
| `NO_SHORTAGE` | Sufficient domestic labour supply identified; no shortage rating. |
| `NOT_ASSESSED` | Occupation not evaluated in the national shortage assessment cycle. |

#### 2.4 `DemandComparabilityVerdict`
Overall verdict emitted by the 11-dimension comparability engine.

| Verdict | Meaning | Recommended UI Treatment |
| :--- | :--- | :--- |
| `DIRECTLY_COMPARABLE` | Same metric type, compatible taxonomy, aligned time window, similar methodology. | Direct numeric side-by-side comparison permitted. |
| `DIRECTIONALLY_COMPARABLE` | Different instruments, but directional trends (growth/decline) can be contrasted. | Compare trend arrows and percentages; highlight metric difference. |
| `METHODOLOGICALLY_DISTINCT` | Distinct constructs (e.g. 10-year openings vs monthly job advert index). | Side-by-side with prominent methodology badge; no combined math. |
| `NOT_COMPARABLE` | Incompatible classifications, unmatched timeframes, or non-overlapping constructs. | Do not compare; display separate isolated cards. |
| `INSUFFICIENT_DATA` | One or both markets lack valid demand observations for the selected role. | Display data gap notice. |

#### 2.5 `SkillCategory`
Classification of occupational skills for gap analysis.

| Category | Description | Examples |
| :--- | :--- | :--- |
| `PROGRAMMING_LANGUAGE` | Core languages used in software, data, or scripting | Python, Java, TypeScript, C++, Go, Rust |
| `FRAMEWORK_LIBRARY` | Application frameworks and runtimes | React, FastAPI, Spring Boot, PyTorch, Angular |
| `CLOUD_DEVOPS` | Cloud platforms, containerization, CI/CD | AWS, Azure, GCP, Docker, Kubernetes, Terraform |
| `DATABASE_DATA` | Relational, NoSQL, and data processing engines | PostgreSQL, MongoDB, Redis, Snowflake, Spark |
| `ARCHITECTURE_SYSTEM_DESIGN` | High-level system design and patterns | Distributed Systems, Microservices, API Design |
| `SECURITY_COMPLIANCE` | Security, identity, and compliance protocols | OWASP, OAuth 2.0, Zero Trust, Cryptography |
| `CORE_ENGINEERING_PRACTICE` | Methodologies and engineering hygiene | Agile, CI/CD, Unit Testing, Code Review |
| `SOFT_SKILL_MANAGEMENT` | Interpersonal, communication, and leadership skills | Stakeholder Management, Mentorship, Problem Solving |

---

### 3. SCHEMA DEFINITIONS

#### 3.1 `DemandMetricDefinition`
Defines the metadata and constraints for a demand metric type.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `metric_type` | `DemandMetricType` | Yes | Enum identifier of the metric type |
| `display_name` | `string` | Yes | Human-readable title for UI headers |
| `unit` | `string` | Yes | Measurement unit (e.g., "Annual Openings", "Index (Base=100)") |
| `description` | `string` | Yes | High-level summary of the metric |
| `underlying_construct` | `string` | Yes | What the instrument actually measures |
| `limitations` | `list[string]` | Yes | Key caveats, biases, and exclusions |
| `comparability_class` | `string` | Yes | Grouping class for comparability evaluation |

#### 3.2 `DemandTimeSeriesPoint`
Represents an individual point in an occupational demand series.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `period` | `string` | Yes | Period label (e.g. "2023-01", "2024-Q3", "2023-2033") |
| `value` | `float` | Yes | Metric value for this period |
| `lower_bound` | `float` | No | Lower confidence/uncertainty interval (if published) |
| `upper_bound` | `float` | No | Upper confidence/uncertainty interval (if published) |
| `is_projected` | `boolean` | Yes | True if estimated via projection model rather than observed |

#### 3.3 `RegionalDemandPoint`
Represents geographic demand distribution within a market.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `region_code` | `string` | Yes | ISO or administrative region code (e.g. "NSW", "CA", "ENG-LON") |
| `region_name` | `string` | Yes | Full geographic region name (e.g. "New South Wales", "California") |
| `value` | `float` | Yes | Demand volume, index, or sample count in this region |
| `share_percentage` | `float` | No | Percentage of national total represented by this region |
| `index_vs_national` | `float` | No | Relative concentration index (100 = national average) |

#### 3.4 `SkillDemandItem`
Represents a skill requirement associated with an occupation.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `skill_name` | `string` | Yes | Normalized skill title (e.g. "Python", "Cloud Computing") |
| `category` | `SkillCategory` | Yes | Skill domain classification |
| `importance_score` | `float` | Yes | Score on 0.0 to 100.0 scale reflecting importance |
| `frequency_percentage`| `float` | No | Percentage of postings requiring this skill (0.0 to 100.0) |
| `growth_rate` | `float` | No | Historical or projected growth in skill mentions |
| `is_hot_skill` | `boolean` | Yes | Flag indicating rapid emerging demand |

#### 3.5 `DemandObservation`
Atomic record linking a national occupation to an empirical demand observation.

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `observation_id` | `string` | Yes | Unique observation identifier (e.g. `dmd-us-15-1252-2024`) |
| `market_id` | `MarketId` | Yes | Market code (`US`, `AU`, `UK`, `SG`, `IN`) |
| `occupation_id` | `string` | Yes | National occupation code (e.g. `15-1252`, `261313`, `2134`) |
| `canonical_id` | `string` | No | Canonical occupation ID (e.g. `swe`, `data-eng`) |
| `source_id` | `string` | Yes | Referenced data catalog source ID (e.g. `us.bls.ep`) |
| `metric_type` | `DemandMetricType` | Yes | Demand metric classification |
| `metric_unit` | `string` | Yes | Measurement unit |
| `value` | `float` | Yes | Primary observed or projected value |
| `reference_period` | `string` | Yes | Official publication reference period (e.g. `2023-2033`) |
| `geographic_scope` | `string` | Yes | Geographic coverage (e.g. `National`, `England`) |
| `time_series` | `list[Point]` | Yes | Time-series points for trend analysis |
| `regional_breakdown` | `list[Region]`| Yes | Sub-national geographic breakdown |
| `shortage_status` | `ShortageStatus` | Yes | Official shortage status rating |
| `future_demand_rating`| `string` | No | Qualitative demand rating (e.g. "Strong", "Moderate") |
| `percent_unfilled_over_6_months` | `float` | No | Singapore MOM hard-to-fill indicator (%) |
| `typical_education` | `string` | No | Typical entry-level education (e.g. "Bachelor's degree") |
| `work_experience_required` | `string` | No | Typical work experience required |
| `data_quality_grade`| `string` | Yes | Grade (`OFFICIAL_STATISTICS`, `CALIBRATED_BENCHMARK`) |
| `notes` | `string` | No | Governance notes and methodology qualifications |

---

### 4. STORAGE DESIGN AND PERSISTENCE STRATEGY

To accommodate Render Free Tier filesystem ephemerality while ensuring full reproducibility and git versioning:

1. **Versioned JSON Data Files:**
   All datasets are stored as structured JSON records within the repository:
   - `src/backend/data/demand/metrics.json`: Metric type definitions and limitations.
   - `src/backend/data/demand/sources.json`: Provenance metadata for demand sources.
   - `src/backend/data/demand/observations.json`: Observations for national occupations.
   - `src/backend/data/demand/skill_demands.json`: Skill requirements by occupation.
   - `src/backend/data/demand/shortage_indicators.json`: Shortage and recruitment tightness data.
2. **In-Memory Service Registry:**
   On application startup, `DemandService` loads all JSON files into memory, validates records against Pydantic models, builds indexes (by market, national occupation ID, canonical ID, metric type), and caches calculations.
3. **Immutability & Integrity:**
   Observations are immutable (`frozen=True` in Pydantic models). Updates require committing new versioned records to git.
