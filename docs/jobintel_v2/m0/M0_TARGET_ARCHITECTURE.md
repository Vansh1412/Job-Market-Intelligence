# M0 Target Architecture Proposal

This is a proposal only. It preserves current India and USA behavior behind adapters and introduces new modules additively. It does not authorize implementation.

## Target system

```mermaid
flowchart LR
  Sources[Official sources / licensed job data] --> Ingest[Market-specific ingestion adapters]
  Ingest --> Raw[Immutable source snapshots + provenance]
  Raw --> Validate[Schema, coverage, quality, suppression checks]
  Validate --> Normalize[Market-native definitions + unit normalization]
  Normalize --> OccMap[Versioned occupation crosswalk + mapping confidence]
  Normalize --> Publish[Curated market aggregates / distributions]
  OccMap --> Publish
  Publish --> Salary[Salary distributions and comparison]
  Publish --> Demand[Demand/shortage/projection indicators]
  Publish --> Skills[Skill prevalence and trend service]
  Salary --> API[Versioned API /v1]
  Demand --> API
  Skills --> API
  API --> Web[Frontend market modules and source/methodology views]
  API --> Scenario[Scenario engine, evidence-bounded]
  Registry[Market registry + model/evidence readiness] --> API
  Eval[Monitoring, freshness, mapping QA, model evaluation] --- Publish
  Eval --- API
```

## Proposed modules

| Module | Responsibility / input → output | Dependencies / interactions / risk |
|---|---|---|
| Market registry | Market ID, currency, locale, occupation scheme, capabilities, readiness → market metadata | New `src/backend/markets/registry.py`; interacts with API and UI. Risk: treats market presence as capability. Keep feature flags/capability status separate. No dependency required. |
| Market adapters | Source-specific files/API → source-native normalized tables | `src/backend/markets/{au,uk,sg}/`; ingestion scripts/workflows. Dependencies depend on CSV/XLSX/API format; avoid new dependency until source choice. Risk: licensing/update drift. |
| Provenance/source registry | Source ID, URL, license/access, publisher, vintage, retrieved date, schema → lineage records | New `src/backend/data/provenance.py` and versioned source metadata. Risk: metadata omitted during derived transformations. |
| Validation/quality | Raw schemas, counts, suppression, units, duplicates → quality report/accept/reject | `src/backend/data/validation.py`; test fixtures. Risk: silently accepting incompatible new release. |
| Occupation crosswalk | Source code/version → canonical occupation candidates, confidence, method → linked occupation records | `src/backend/occupations/`; may use official correspondences, no probabilistic NLP dependency initially. Risk: false equivalence. |
| Salary normalization | Native pay definition, period, currency, employment population → source-native plus normalized comparable metrics | `src/backend/intelligence/salary.py`; preserve raw values and annotate assumptions. Risk: false precision from annualization/FX. |
| Distribution service | Market/occupation/region/time → counts, percentiles, intervals, quality flags | Uses curated aggregates; never infers percentiles from a single median. |
| Comparison service | Canonical occupations, aligned reference period, compatible population → side-by-side local currencies/optional FX | New service; current `market_service.py` may remain for compatibility. Risk: population and currency comparability. |
| Skill intelligence | Jobs/official skills where supported → skills, prevalence, evidence/source windows | New module; do not infer missing skills from wage tables. |
| Demand intelligence | Vacancy ads, vacancy surveys, shortage lists, projections → distinct indicator series | Keep different concepts separate. Risk: a shortage score can be misrepresented as vacancy volume. |
| Scenario service | User-declared changes + empirical transitions/evidence → scenario ranges with uncertainty | Only after adequate longitudinal/transition evidence. Avoid causal salary uplift claims. |
| API versioning | Market/readiness/capabilities and intelligence payloads → `/api/v1/...` contracts | Keep current routes and consumers during compatibility window; additive versioned routers. |
| Frontend modules | Selected market capability → explorer, salary, demand, skills, scenario, methodology pages | Market selector consumes registry; pages show definitions, date, source, limitations, quality. Avoid implying predictions in descriptive-only markets. |
| Monitoring/evaluation | Ingestion health, freshness, source version, map coverage, drift, model validity → release gates | CI and runtime observability; thresholds require approval. |

## Backend module view

```mermaid
flowchart TB
  RoutersV1[routers/v1] --> Registry[markets.registry]
  RoutersV1 --> Salary[services/salary_distributions]
  RoutersV1 --> Compare[services/cross_market]
  RoutersV1 --> Skills[services/skills]
  RoutersV1 --> Demand[services/demand]
  RoutersV1 --> Scenario[services/scenario]
  Salary --> Data[validated curated tables]
  Compare --> Occ[occupation crosswalk]
  Compare --> Data
  Skills --> Data
  Demand --> Data
  Scenario --> Salary
  Adapters[market adapters] --> Provenance[source registry]
  Adapters --> Validation[validation / quality]
  Validation --> Data
  ModelRegistry[existing ModelRegistry] --> Registry
```

## Frontend and API dependency view

```mermaid
flowchart LR
  Select[Market selector] --> Caps[GET /api/v1/markets]
  Caps --> Explore[Market explorer]
  Explore --> Dist[GET distribution]
  Explore --> Compare[GET compare]
  Skills[Skill explorer] --> SkillAPI[GET skills / evidence]
  Demand[Demand explorer] --> DemandAPI[GET vacancy/shortage/projection]
  Scenario[Scenario UI] --> ScenarioAPI[POST scenarios]
  Method[Sources and methodology] --> SourceAPI[GET sources / data quality]
```

## Deployment/data flow/model lifecycle

Keep Vercel SPA + Render FastAPI while current product requirements and measured resource limits fit. Backend remains stateless; curated aggregates and model artifacts are built/released as versioned files, with checksum and provenance. Private row data must not enter frontend build artifacts. Ingestion should be separate from request-time service; API reads validated aggregate snapshots. Existing India/USA serialized artifacts remain frozen and tested by legacy parity. New models (if ever approved) require per-market training/evaluation, provenance, independent test, manifest publication, rollout and rollback. New country features need not imply new models.

## Explicit unknowns

Exact storage/vendor choices, refresh cadence, data licensing, regional units, source-specific publication permissions, FX policy, canonical ontology granularity, predictive launch bar, and Render capacity require approval/research. No new runtime dependency is required for the conceptual design, but source formats may require parsers/API clients; defer until sources and deployment impact are selected.

## Deployment diagram

```mermaid
flowchart LR
  Git[GitHub master] -->|build/static assets| Vercel[Vercel SPA / CDN]
  Git -->|Python build + start| Render[Render web service]
  Browser -->|HTTPS| Vercel
  Browser -->|API HTTPS, VITE_API_BASE_URL| Render
  Render -->|optional artifact sync| ObjectStore[S3-compatible store, conditional]
  Render -->|read-only tracked models/aggregates| Image[Runtime filesystem]
  Render -->|health probe /api/ready| Probe[Render readiness]
```

## Model artifact lifecycle

```mermaid
flowchart LR
  Train[Research notebooks/scripts] --> Freeze[Frozen model + preprocessing + metadata]
  Freeze --> Manifest[Python SHA table + JSON manifest]
  Manifest --> Package[Git / deployment image or optional object sync]
  Package --> Verify[SHA-256 verification]
  Verify --> Deserialize[joblib / pickle load]
  Deserialize --> Inference[Market-specific prediction service]
  Verify --> Ready[/ready status]
  Inference --> QA[Golden / parity / holdout regression]
```

The apparent SHA match at this checkout is verified by local hashing; storage sync and deployed artifact equality are not.
