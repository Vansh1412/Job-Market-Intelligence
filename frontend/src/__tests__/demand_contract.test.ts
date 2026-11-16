import { describe, it, expect } from 'vitest';
import {
  DemandMetricType,
  DemandTrendDirection,
  ShortageStatus,
  DemandComparabilityVerdict,
  DemandProvenance,
  OccupationDemandProfile,
  SkillGapAnalysisResult,
} from '../types';

describe('Demand Intelligence Contract & Enums', () => {
  it('defines valid DemandMetricType values', () => {
    const validTypes: DemandMetricType[] = [
      'OBSERVED_JOB_ADVERTISEMENTS',
      'OBSERVED_VACANCIES',
      'ANNUAL_JOB_OPENINGS',
      'EMPLOYMENT_LEVEL',
      'EMPLOYMENT_CHANGE',
      'PROJECTED_EMPLOYMENT_CHANGE',
      'SHORTAGE_INDICATOR',
      'SKILL_REQUIREMENT',
    ];
    expect(validTypes).toHaveLength(8);
  });

  it('defines valid DemandTrendDirection values', () => {
    const validDirections: DemandTrendDirection[] = [
      'STRONG_GROWTH',
      'MODERATE_GROWTH',
      'STABLE',
      'MODERATE_DECLINE',
      'STRONG_DECLINE',
      'INSUFFICIENT_DATA',
    ];
    expect(validDirections).toHaveLength(6);
  });

  it('defines valid ShortageStatus values', () => {
    const validStatuses: ShortageStatus[] = [
      'NATIONAL_SHORTAGE',
      'REGIONAL_SHORTAGE',
      'NO_SHORTAGE',
      'NOT_ASSESSED',
    ];
    expect(validStatuses).toHaveLength(4);
  });

  it('defines valid DemandComparabilityVerdict values', () => {
    const validVerdicts: DemandComparabilityVerdict[] = [
      'DIRECTLY_COMPARABLE',
      'DIRECTIONALLY_COMPARABLE',
      'METHODOLOGICALLY_DISTINCT',
      'NOT_COMPARABLE',
      'INSUFFICIENT_DATA',
    ];
    expect(validVerdicts).toHaveLength(5);
  });

  it('defines valid DemandProvenance values', () => {
    const validProvenance: DemandProvenance[] = [
      'OFFICIAL_PUBLISHED',
      'OFFICIALLY_DERIVED',
      'JOBINTEL_CURATED',
      'JOBINTEL_MODEL_ESTIMATE',
      'SYNTHETIC_TEST_FIXTURE',
      'UNVERIFIED',
    ];
    expect(validProvenance).toHaveLength(6);
  });

  it('verifies OccupationDemandProfile contract with publication gate and disclosures', () => {
    const mockProfile: OccupationDemandProfile = {
      occupation_id: 'UK_SOC_2020:2134',
      occupation_title: 'Programmers and software development professionals',
      market_id: 'UK',
      primary_metric_type: 'OBSERVED_JOB_ADVERTISEMENTS',
      primary_metric_value: null,
      primary_metric_unit: 'Online Job Advert Index (Base=100)',
      reference_period: '2024-Q3',
      trend_direction: 'INSUFFICIENT_DATA',
      trend_time_series: [],
      regional_distribution: [],
      top_skills: [],
      shortage_status: 'NATIONAL_SHORTAGE',
      entry_requirements: {},
      source_attributions: [],
      methodology_disclaimers: ['UK demand data is currently withheld pending review.'],
      provenance: 'OFFICIALLY_DERIVED',
      provenance_label: 'Derived from official data',
      provenance_description: 'Experimental ONS/Textkernel index.',
      publication_gate_active: true,
      publication_gate_code: 'UK_DEMAND_DATA_NOT_PUBLISHED',
      publication_gate_message: 'UK demand data is currently withheld pending source-use and redistribution review.',
    };
    expect(mockProfile.publication_gate_active).toBe(true);
    expect(mockProfile.provenance).toBe('OFFICIALLY_DERIVED');
    expect(mockProfile.primary_metric_value).toBeNull();
  });

  it('distinguishes between null withheld metric and genuine measured zero', () => {
    const gatedProfile: Partial<OccupationDemandProfile> = {
      primary_metric_value: null,
      publication_gate_active: true,
      publication_gate_code: 'UK_DEMAND_DATA_NOT_PUBLISHED',
    };
    const zeroProfile: Partial<OccupationDemandProfile> = {
      primary_metric_value: 0.0,
      publication_gate_active: false,
    };
    expect(gatedProfile.primary_metric_value).toBeNull();
    expect(zeroProfile.primary_metric_value).toBe(0.0);
    expect(gatedProfile.primary_metric_value).not.toBe(zeroProfile.primary_metric_value);
  });

  it('verifies SkillGapAnalysisResult contract with formula breakdown', () => {
    const mockGapResult: SkillGapAnalysisResult = {
      target_occupation_id: '15-1252',
      target_occupation_title: 'Software Developers',
      market_id: 'US',
      user_skills_submitted: ['Python', 'SQL'],
      matched_skills: ['Python', 'SQL'],
      missing_critical_skills: [],
      missing_secondary_skills: [],
      match_percentage: 100.0,
      matched_skill_weight: 185.0,
      total_required_weight: 185.0,
      formula_explanation: 'Skill Coverage (%) = (Matched Skill Weight / Total Required Skill Weight) * 100',
      methodology_notes: 'Skill coverage measures alignment between candidate skills and employer-requested competencies.',
      readiness_level: 'HIGH',
      recommendations: ['Market Alignment: Your current profile aligns 100%.'],
    };
    expect(mockGapResult.matched_skill_weight).toBe(185.0);
    expect(mockGapResult.total_required_weight).toBe(185.0);
    expect(mockGapResult.formula_explanation).toContain('Skill Coverage (%)');
  });
});
