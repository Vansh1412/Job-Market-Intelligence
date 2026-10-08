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
