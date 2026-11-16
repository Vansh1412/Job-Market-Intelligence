export type MarketType = 'USA' | 'India';

export interface KPIData {
  value: string | number;
  label: string;
  sub?: string;
  delta?: string;
  accent: string;
  num?: number;
}

export interface FunnelStage {
  Stage: string;
  Count: number;
  Pct_Total: number;
  Pct_Previous: number;
  Notes: string;
}

export interface DataFlowItem {
  stage: string;
  count: number;
  pct: string;
  desc: string;
  color: string;
}

export interface ResearchQuestion {
  id: string;
  number: string;
  title: string;
  question: string;
  status: string;
  color: string;
  finding: string;
  metrics: { label: string; value: string }[];
}

export interface RoleSalary {
  Role_Family?: string;
  role?: string;
  Postings?: number;
  postings?: number;
  Median_Salary?: number;
  median_salary?: number;
  median_salary_lpa?: number;
  Mean_Salary?: number;
  mean_salary?: number;
  mean_salary_lpa?: number;
  Std_Dev?: number;
  IQR?: number;
  Min_Salary?: number;
  min_salary_lpa?: number;
  Max_Salary?: number;
  max_salary_lpa?: number;
  Q1?: number;
  Q3?: number;
}

export interface SenioritySalary {
  Seniority?: string;
  seniority?: string;
  experience_band?: string;
  Postings?: number;
  postings?: number;
  Median_Salary?: number;
  median_salary?: number;
  median_salary_lpa?: number;
  Mean_Salary?: number;
  mean_salary?: number;
  mean_salary_lpa?: number;
  Q1?: number;
  Q3?: number;
  Std_Dev?: number;
}

export interface LocationSalary {
  City?: string;
  city?: string;
  Postings?: number;
  postings?: number;
  pct_of_total?: number;
  Median_Salary?: number;
  median_salary?: number;
  Mean_Salary?: number;
  mean_salary?: number;
  Q1?: number;
  Q3?: number;
  Std_Dev?: number;
}

export interface ComparatorResult {
  benchmark: number;
  role: { name: string; median: number; delta_vs_benchmark: number; pct_vs_benchmark: number };
  seniority: { name: string; median: number; delta_vs_benchmark: number; pct_vs_benchmark: number };
  location: { name: string; median: number; delta_vs_benchmark: number; pct_vs_benchmark: number };
}

export interface SkillItem {
  id?: string;
  name: string;
  raw_key?: string;
  category?: string;
  color?: string;
  postings?: number;
  prevalence_pct?: number;
}

export interface SkillLandscapePoint {
  skill: string;
  category: string;
  color: string;
  prevalence_pct: number;
  median_salary: number;
  postings: number;
  delta_vs_median: number;
}

export interface SkillDetail {
  skill: string;
  display_name?: string;
  category?: string;
  color?: string;
  postings?: number;
  posting_count?: number;
  prevalence_pct?: number;
  prevalence?: number;
  demand_percentage?: number;
  median_salary?: number;
  median_with?: number;
  observed_median_salary_lpa?: number;
  median_with_lpa?: number;
  delta_vs_cohort?: number;
  delta?: number;
  observed_salary_difference_lpa?: number;
  delta_lpa?: number;
  roles?: string[];
  associated_roles?: string[];
  archetypes?: string[];
  associated_archetypes?: string[];
  companions?: ({ skill: string; cooccurrences: number } | string)[];
  combos?: string[];
  cooccurring_skills?: string[];
}

export interface ArchetypeItem {
  id?: number;
  archetype_id?: string;
  raw_cluster_id?: number;
  rank?: number;
  code?: string;
  name: string;
  definition?: string;
  description?: string;
  desc?: string;
  color: string;
  count?: number;
  postings?: number;
  cohort_size?: number;
  share_pct?: number;
  pct_cohort?: number;
  median_salary?: number;
  median_salary_lpa?: number;
  typical_mae?: number;
  typical_mae_lpa?: number;
  typical_rmse_lpa?: number;
  rel_error?: number;
  relative_mae_pct?: number;
  typical_salary?: number;
  key_skills?: string[];
  signature_skills?: string[];
  top_skills?: string[];
  top_roles?: string[];
}

export interface PredictionOptions {
  country?: string;
  currency?: string;
  currency_symbol?: string;
  scale?: string;
  roles: string[];
  seniority_tiers?: string[];
  work_modes?: string[];
  experience_presets?: { label: string; midpoint: number; range: number }[];
  cities: string[];
  locations?: string[];
  skills: SkillItem[];
  default_profile: any;
  baseline?: any;
}

export interface PredictionResult {
  country?: string;
  currency?: string;
  currency_symbol?: string;
  predicted_salary?: number;
  predicted_salary_lpa?: number;
  predicted_salary_inr?: number;
  predicted_salary_display: string;
  predicted_salary_inr_display?: string;
  confidence_interval?: {
    lower?: number;
    upper?: number;
    lower_lpa?: number;
    upper_lpa?: number;
    display: string;
    margin_mae?: number;
    margin_mae_lpa?: number;
  };
  baseline_salary?: number;
  baseline_salary_lpa?: number;
  baseline_salary_inr?: number;
  delta_vs_baseline?: number;
  delta_vs_baseline_lpa?: number;
  pct_vs_baseline: number;
  cluster_id?: number;
  archetype_available?: boolean;
  archetype: {
    archetype_id?: string;
    code?: string;
    name: string;
    definition?: string;
    desc?: string;
    color: string;
    archetype_available?: boolean;
    typical_mae?: number;
    typical_mae_lpa?: number;
    rel_error?: number;
    relative_mae_pct?: number;
    rank?: number;
  };
  num_skills: number;
  input_summary: any;
  distribution_context: {
    label: string;
    salary?: number;
    salary_lpa?: number;
    salary_inr?: number;
    is_user?: boolean;
  }[];
  model_metadata?: any;
}

export interface ModelBenchmark {
  Model: string;
  MAE: number;
  RMSE: number;
  R2: number;
  Baseline_Reduction: number;
}

export interface FeatureSet {
  id: string;
  name: string;
  features_count: number;
  mae: number;
  r2: number;
  composition: string;
  color: string;
  is_best: boolean;
  delta_vs_a: string;
}

export interface FeatureImportance {
  Feature: string;
  Importance: number;
  Category?: string;
}

export interface ArchetypeError {
  cluster_id: number;
  code: string;
  name: string;
  color: string;
  mae: number;
  rmse: number;
  r2: number;
  rel_error_pct: number;
  count: number;
}

export interface PipelineStage {
  id: string;
  title: string;
  badge: string;
  desc: string;
  color: string;
}

export interface CrossMarketSummary {
  title: string;
  methodology_note: string;
  usa_overview: {
    cohort_size: number;
    disclosed_pct: number;
    median_salary_display: string;
    mean_salary_display: string;
    iqr_display: string;
  };
  india_overview: {
    cohort_size: number;
    disclosed_pct: number;
    median_salary_display: string;
    mean_salary_display: string;
    iqr_display: string;
  };
  shared_skills_prevalence: {
    skill: string;
    usa_pct: number;
    india_pct: number;
  }[];
  role_demand_comparison: {
    role: string;
    usa_share_pct: number;
    india_share_pct: number;
  }[];
  model_comparison: {
    usa: {
      model_name: string;
      feature_count: number;
      n_samples: number;
      holdout_mae: string;
      holdout_rmse: string;
      r2_score: number;
      target: string;
      archetypes_k: number;
    };
    india: {
      model_name: string;
      feature_count: number;
      n_samples: number;
      holdout_mae: string;
      holdout_rmse: string;
      r2_score: number;
      target: string;
      archetypes_k: number;
    };
  };
}

export interface ClassificationSystem {
  classification_id: string;
  market_id: string;
  official_title: string;
  version_edition: string;
  issuing_authority: string;
  code_format: string;
  hierarchy_levels: string[];
  is_active: boolean;
  source_reference: string;
  license_attribution: string;
}

export interface NationalOccupation {
  occupation_id: string;
  classification_id: string;
  market_id: string;
  occupation_code: string;
  occupation_title: string;
  official_definition: string;
  tasks: string[];
  entry_qualifications?: string | null;
  hierarchy_level: string;
  parent_code?: string | null;
  is_leaf: boolean;
  alternate_titles: string[];
  task_provenance?: 'OFFICIAL_VERBATIM' | 'OFFICIALLY_DERIVED' | 'JOBINTEL_CURATED';
}

export interface CanonicalOccupation {
  canonical_occupation_id: string;
  preferred_title: string;
  concept_family: string;
  description: string;
  core_competencies: string[];
  status: 'ACTIVE' | 'DEPRECATED' | 'PROVISIONAL';
}

export interface OccupationMapping {
  mapping_id: string;
  source_occupation_id: string;
  target_occupation_id: string;
  target_type: 'NATIONAL' | 'CANONICAL';
  relationship_type: string;
  confidence_score: number | string;
  review_status: string;
  methodology: string;
  evidence_sources: string[];
  notes_and_limitations: string;
  reviewer: string;
  effective_date: string;
  created_at: string;
}

export interface CrossMarketMatchItem {
  target_occupation: NationalOccupation | CanonicalOccupation;
  target_type: 'NATIONAL' | 'CANONICAL';
  target_market_id: string;
  relationship_type: string;
  confidence_score: number | string;
  review_status: string;
  methodology: string;
  evidence_sources: string[];
  notes_and_limitations: string;
  approximation_warning?: string | null;
  task_similarity?: number | null;
}

export interface CrossMarketComparisonResult {
  source_occupation: NationalOccupation;
  matches: CrossMarketMatchItem[];
  unmapped_markets: string[];
  total_matches: number;
}

export interface ConcordanceCoverageStats {
  total_national_occupations: number;
  mapped_national_occupations: number;
  unmapped_national_occupations: number;
  total_international_references?: number;
  mapped_international_references?: number;
  unmapped_international_references?: number;
  total_catalog_occupations?: number;
  total_canonical_concepts: number;
  linked_canonical_concepts: number;
  unlinked_canonical_concepts: number;
  mappings_by_relationship: Record<string, number>;
  mappings_by_review_status: Record<string, number>;
  official_mappings_count: number;
  expert_reviewed_mappings_count: number;
  total_mappings: number;
}

// =====================================================================
// Cross-Market Salary Intelligence Types (Sprint 3B.1)
// =====================================================================

export interface SalaryPercentiles {
  p10: number | null;
  p25: number | null;
  p50: number | null;
  p75: number | null;
  p90: number | null;
}

export interface SalarySourceMeta {
  source_id: string;
  market_id: string;
  authority: string;
  publication_name: string;
  reference_period: string;
  release_date: string;
  license: string;
  currency: string;
  pay_concept: string;
  frequency: string;
  sample_coverage: string;
  source_url: string;
  is_active: boolean;
  governance_gate?: string;
}

export interface CurrencyRateInfo {
  currency: string;
  market_id: string;
  nominal_fx_to_usd: number;
  nominal_usd_multiplier: number;
  ppp_conversion_factor_to_usd: number;
  ppp_usd_multiplier: number;
  fx_source: string;
  ppp_source: string;
}

export interface PppFxRatesPayload {
  base_currency: string;
  reference_year: string;
  methodology: Record<string, string>;
  rates: Record<string, CurrencyRateInfo>;
}

export interface OccupationSalaryProfile {
  observation_id: string;
  occupation_id: string;
  occupation_title: string;
  market_id: string;
  source_id: string;
  currency: string;
  period_type: string;
  mean: number | null;
  percentiles: SalaryPercentiles;
  nominal_usd_median: number | null;
  ppp_usd_median: number | null;
  sample_size: number | null;
  standard_error: number | null;
  is_suppressed: boolean;
  quality_flag: string;
  source_meta?: SalarySourceMeta;
  notes: string;
}

export type ComparabilityVerdict =
  | 'DIRECTLY_COMPARABLE_WITHIN_SOURCE_LIMITATIONS'
  | 'COMPARABLE_WITH_ADJUSTMENTS'
  | 'COMPARABLE_WITH_MAJOR_CAVEATS'
  | 'NOT_COMPARABLE'
  | 'INSUFFICIENT_DATA';

export interface CrossMarketSalaryComparisonItem {
  market_id: string;
  occupation_id: string;
  occupation_title: string;
  relationship_to_source: string;
  relationship_type: string;
  confidence_score: number;
  source_id: string;
  currency: string;
  original_currency: string;
  original_median: number | null;
  nominal_usd_median: number | null;
  ppp_usd_median: number | null;
  percentiles_original: Record<string, number | null>;
  percentiles_nominal_usd: Record<string, number | null>;
  percentiles_ppp_usd: Record<string, number | null>;
  comparability_verdict: ComparabilityVerdict;
  comparability_caveats: string[];
  is_suppressed: boolean;
  quality_flag: string;
  notes: string;
}

export interface CrossMarketSalaryComparisonResult {
  source_occupation_id: string;
  source_occupation_title: string;
  source_market_id: string;
  source_currency: string;
  source_median_original: number | null;
  source_median_nominal_usd: number | null;
  source_median_ppp_usd: number | null;
  comparisons: CrossMarketSalaryComparisonItem[];
  fx_rates_metadata: Record<string, any>;
  ppp_factors_metadata: Record<string, any>;
  methodology_disclaimer: string;
  comparability_dimensions: string[];
}

export interface SalaryConversionResult {
  original_amount: number;
  original_currency: string;
  nominal_usd: number;
  ppp_usd: number;
  nominal_fx_to_usd: number;
  ppp_factor_to_usd: number;
}


