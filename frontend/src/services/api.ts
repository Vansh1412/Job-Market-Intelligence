import {
  KPIData,
  FunnelStage,
  DataFlowItem,
  ResearchQuestion,
  RoleSalary,
  SenioritySalary,
  LocationSalary,
  ComparatorResult,
  SkillLandscapePoint,
  ArchetypeItem,
  PredictionOptions,
  PredictionResult,
  FeatureSet,
  FeatureImportance,
  ArchetypeError,
  PipelineStage,
  CrossMarketSummary,
} from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, options);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error (${res.status}): ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Core / System
  getHealth: () => fetchJson<{ status: string; registry: any }>('/health'),
  getMeta: () => fetchJson<any>('/meta'),

  // USA Market Endpoints
  getUsaOptions: () => fetchJson<PredictionOptions>('/usa/options'),
  predictUsaSalary: (profile: {
    role_family: string;
    seniority: string;
    city_clean: string;
    is_remote: boolean;
    selected_skills: string[];
  }) =>
    fetchJson<PredictionResult>('/usa/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    }),
  getUsaArchetypes: () => fetchJson<ArchetypeItem[]>('/usa/archetypes'),
  getUsaMarketSummary: (params?: { role?: string; seniority?: string; location?: string; skill?: string }) => {
    const qs = new URLSearchParams();
    if (params?.role && params.role !== 'All') qs.append('role', params.role);
    if (params?.seniority && params.seniority !== 'All') qs.append('seniority', params.seniority);
    if (params?.location && params.location !== 'All') qs.append('location', params.location);
    if (params?.skill && params.skill.trim()) qs.append('skill', params.skill.trim());
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return fetchJson<any>(`/usa/market-summary${query}`);
  },
  getUsaSkills: () => fetchJson<{ country: string; skills: any[] }>('/usa/skills'),

  // India Market Endpoints
  getIndiaOptions: () => fetchJson<PredictionOptions>('/india/options'),
  predictIndiaSalary: (profile: {
    normalized_role: string;
    experience_midpoint_years: number;
    experience_range_years: number;
    city_grouped: string;
    work_mode: string;
    selected_skills: string[];
  }) =>
    fetchJson<PredictionResult>('/india/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    }),
  getIndiaArchetypes: () => fetchJson<ArchetypeItem[]>('/india/archetypes'),
  getIndiaMarketSummary: (params?: { role?: string; experience?: string; location?: string; skill?: string }) => {
    const qs = new URLSearchParams();
    if (params?.role && params.role !== 'All') qs.append('role', params.role);
    if (params?.experience && params.experience !== 'All') qs.append('experience', params.experience);
    if (params?.location && params.location !== 'All') qs.append('location', params.location);
    if (params?.skill && params.skill.trim()) qs.append('skill', params.skill.trim());
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return fetchJson<any>(`/india/market-summary${query}`);
  },
  getIndiaSkills: () => fetchJson<{ country: string; currency: string; total_skills: number; skills: any[] }>('/india/skills'),
  getIndiaSkillDetail: (skillName: string) => fetchJson<any>(`/india/skills/${encodeURIComponent(skillName)}`),


  // Cross-Market Comparative Analytics
  getCrossMarketSummary: () => fetchJson<CrossMarketSummary>('/cross-market/summary'),

  // Legacy Compatibility (Routes mapped to existing backend endpoints)
  getOverviewKPIs: () => fetchJson<Record<string, KPIData>>('/overview/kpis'),
  getFunnel: () => fetchJson<FunnelStage[]>('/overview/funnel'),
  getDataFlow: () => fetchJson<DataFlowItem[]>('/overview/data-flow'),
  getResearchQuestions: () => fetchJson<ResearchQuestion[]>('/overview/research-questions'),

  getSalarySummary: () => fetchJson<any[]>('/salary/summary'),
  getSalaryByRole: () => fetchJson<RoleSalary[]>('/salary/by-role'),
  getSalaryBySeniority: () => fetchJson<SenioritySalary[]>('/salary/by-seniority'),
  getSalaryByLocation: () => fetchJson<LocationSalary[]>('/salary/by-location'),
  getComparator: (role: string, seniority: string, city: string) =>
    fetchJson<ComparatorResult>(
      `/salary/comparator?role=${encodeURIComponent(role)}&seniority=${encodeURIComponent(seniority)}&city=${encodeURIComponent(city)}`
    ),

  getSkillFrequency: () => fetchJson<any[]>('/skills/frequency'),
  getSkillLandscape: () => fetchJson<SkillLandscapePoint[]>('/skills/landscape'),
  getSkillDetail: (skillName: string) => fetchJson<any>(`/skills/detail/${encodeURIComponent(skillName)}`),

  getArchetypesList: () => fetchJson<ArchetypeItem[]>('/archetypes/list'),
  getArchetypeRoleProfile: (clusterId: number) => fetchJson<any[]>(`/archetypes/role-profiles/${clusterId}`),

  getPredictionOptions: () => fetchJson<PredictionOptions>('/predict/options'),
  estimateSalary: (profile: {
    role_family: string;
    seniority: string;
    city_clean: string;
    is_remote: boolean;
    selected_skills: string[];
  }) =>
    fetchJson<PredictionResult>('/predict/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    }),

  getModelBenchmarks: () =>
    fetchJson<{ cv_comparison: any[]; test_results: any[]; best_model: any }>('/models/benchmarks'),
  getFeatureSets: () => fetchJson<FeatureSet[]>('/models/feature-sets'),
  getFeatureImportance: () => fetchJson<FeatureImportance[]>('/models/feature-importance'),

  getArchetypeErrors: () => fetchJson<ArchetypeError[]>('/error-analysis/archetype-breakdown'),
  getStatisticalTest: () => fetchJson<any>('/error-analysis/statistical-test'),
  getHypotheses: () => fetchJson<any[]>('/error-analysis/hypotheses'),

  getPipelineStages: () => fetchJson<PipelineStage[]>('/methodology/pipeline-stages'),
  getLeakageControls: () => fetchJson<any[]>('/methodology/leakage-controls'),
  getLimitations: () => fetchJson<{ id: number; title: string; body: string }[]>('/methodology/limitations'),
};
