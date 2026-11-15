# M0 API Inventory

**VERIFIED FROM SOURCE CODE.** There are 43 domain router operations, each mounted at both `/api/...` and `/...` for backward compatibility. Main adds `/`, health, readiness, and metadata paths. The nominal count is 93 distinct URL paths when counting 43×2 plus 7 main paths; review generated OpenAPI for collision behavior before changing this design. No auth dependencies were found. Method/body/response details below are based on handler code; output schemas are generally untyped dictionaries/lists/DataFrame records rather than declared response models.

| Method/path suffix | Request/parameters | Response/service/data | Consumer / errors |
|---|---|---|---|
| GET `/india/options` | none | India options, 14 roles, cities, work modes, experience presets, feature skills; IndiaService | Predictor; 500 |
| POST `/india/predict` | `{normalized_role, experience_midpoint_years, experience_range_years=2, city_grouped, work_mode=Hybrid, selected_skills=[]}`; bounds/lengths in `IndiaPredictionRequest` | predicted INR/LPA and estimate context; IndiaService + model + archetype | Predictor; 400 |
| POST `/india/archetype` | `{selected_skills=[]}`, max 60 | archetype classification; IndiaService + ArchetypeService | No direct page consumer observed; 400 |
| GET `/india/market-summary` | optional `role, experience, location, skill` | filtered aggregate summary; MarketService | Explore; 500 |
| GET `/india/archetypes` | none | archetype list; ArchetypeService | Archetypes; 500 |
| GET `/india/skills` | none | India skill analytics JSON | Skills; 500 |
| GET `/india/skills/{skill_name}` | path string | one India skill profile | Skills; 404/500 |
| GET `/usa/options` | none | USA categories, skills, defaults; USAService | Predictor; 500 |
| POST `/usa/predict` | `{role_family, seniority, city_clean, is_remote=true, selected_skills=[]}`, max lengths/60 skills | USD salary prediction and error context | Predictor; 400 |
| POST `/usa/archetype` | `{selected_skills=[]}`, max 60 | cluster classification | No direct page consumer observed; 400 |
| GET `/usa/market-summary` | optional `role, seniority, location, skill` | filtered aggregate; MarketService | Explore; 500 |
| GET `/usa/archetypes` | none | archetype list | Archetypes; 500 |
| GET `/usa/skills` | none | skill frequency/prevalence from tables | Skills; 500 |
| GET `/cross-market/summary` | none | native-currency USA/India aggregates and matched skills/roles | CrossMarket; service fallback data possible |
| GET `/predict/options` | none | legacy USA options from static data frames | API client only; no current page call found |
| POST `/predict/estimate` | legacy `{role_family, seniority, city_clean, is_remote=true, selected_skills=[]}` | legacy USA prediction/distribution; inference_service | API client legacy; 400 |
| GET `/salary/summary` | none | USA aggregate records | Legacy client; no current page call found |
| GET `/salary/by-role` | none | USA role salary records | Legacy client |
| GET `/salary/by-seniority` | none | USA seniority records | Legacy client |
| GET `/salary/by-location` | none | USA location records | Legacy client |
| GET `/salary/comparator` | `role=ML / AI Engineer`, `seniority=Senior`, `city=San Francisco` | comparator native USD | Legacy client |
| GET `/skills/frequency` | none | USA skill frequency + category | Legacy client |
| GET `/skills/salary-association` | none | USA observed skill association | Legacy client |
| GET `/skills/landscape` | none | USA skill plotting data | Legacy client/API method |
| GET `/skills/cooccurrence` | none | USA skill co-occurrence | Legacy client |
| GET `/skills/detail/{skill_name}` | path string | USA skill detail | Legacy client |
| GET `/archetypes/list` | none | USA archetype list | Legacy client |
| GET `/archetypes/skill-lifts/{cluster_id}` | integer path | cluster skill lifts | Legacy client |
| GET `/archetypes/role-profiles/{cluster_id}` | integer path | role profile | Legacy client |
| GET `/archetypes/all-skill-lifts` | none | all USA skill lifts | Legacy client |
| GET `/models/benchmarks` | none | model metrics JSON/tables | Legacy client |
| GET `/models/feature-sets` | none | feature-set details | Legacy client |
| GET `/models/feature-importance` | none | feature importance records | Legacy client |
| GET `/error-analysis/archetype-breakdown` | none | archetype error data | Legacy client |
| GET `/error-analysis/statistical-test` | none | statistical test | Legacy client |
| GET `/error-analysis/hypotheses` | none | research hypothesis data | Legacy client |
| GET `/methodology/pipeline-stages` | none | pipeline-stage metadata | Methodology; API client |
| GET `/methodology/leakage-controls` | none | controls metadata | Methodology; API client |
| GET `/methodology/limitations` | none | limitation list | Methodology; API client |
| GET `/overview/kpis` | none | KPI summary | Legacy client |
| GET `/overview/funnel` | none | dataset funnel | Legacy client |
| GET `/overview/research-questions` | none | research metadata | Legacy client |
| GET `/overview/data-flow` | none | data-flow metadata | Legacy client |
| GET `/`, `/health`, `/api/health`, `/ready`, `/api/ready`, `/meta`, `/api/meta` | none | root status; liveness; readiness; metadata. Readiness returns 503 unless registry green | Render health check uses `/api/ready`; health aliases are not auth-protected |

`GET /usa/skills` obtains association data but response only includes frequency rows in the shown handler. Several described “legacy” routes still exist and are mirrored at both prefixes; their production/public status is **INFERRED** from unauthenticated registration, not a separate deployment policy.

## Frontend-consumer summary

Current page consumers: Predictor uses `/usa/options`, `/india/options`, `/usa/predict`, `/india/predict`; Explore uses both market-summary endpoints; Skills uses USA landscape/detail and India skills/detail; Archetypes uses USA/India archetype lists; CrossMarket uses `/cross-market/summary`. `MethodologyPage` and the client expose methodology calls; per-page invocation is visible in page sources. Older endpoints remain in `services/api.ts` but several have no current page caller identified by static search.
