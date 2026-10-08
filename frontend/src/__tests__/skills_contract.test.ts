import { describe, it, expect } from 'vitest';
import { SkillDetail } from '../types';

describe('SkillDetail Contract & Normalization', () => {
  it('correctly maps canonical USA skill detail response fields', () => {
    const rawUsaResponse: SkillDetail = {
      skill: 'python',
      display_name: 'Python',
      category: 'Languages',
      color: '#3B82F6',
      postings: 13410,
      prevalence_pct: 39.4,
      median_salary: 138500,
      delta_vs_cohort: 18500,
      combos: ['SQL', 'AWS', 'Spark'],
      companions: ['SQL', 'AWS', 'Spark'],
      roles: ['Data Scientist', 'Machine Learning Engineer', 'Data Engineer'],
      archetypes: ['A2: Machine Learning & Modeling', 'A1: Cloud Infrastructure & DevOps'],
    };

    // Test canonical field resolution
    const median = rawUsaResponse.median_salary ?? rawUsaResponse.median_with ?? 0;
    const prevalence = rawUsaResponse.prevalence_pct ?? rawUsaResponse.prevalence ?? 0;
    const delta = rawUsaResponse.delta_vs_cohort ?? rawUsaResponse.delta ?? 0;
    const roles = rawUsaResponse.roles ?? rawUsaResponse.associated_roles ?? [];
    const archetypes = rawUsaResponse.archetypes ?? rawUsaResponse.associated_archetypes ?? [];

    expect(median).toBe(138500);
    expect(prevalence).toBe(39.4);
    expect(delta).toBe(18500);
    expect(roles).toHaveLength(3);
    expect(roles[0]).toBe('Data Scientist');
    expect(archetypes).toHaveLength(2);
    expect(archetypes[0]).toContain('Machine Learning');
  });

  it('correctly resolves India skill detail with LPA and associated arrays', () => {
    const rawIndiaResponse: SkillDetail = {
      skill: 'python',
      display_name: 'Python',
      category: 'Languages',
      postings: 710,
      prevalence_pct: 12.1,
      observed_median_salary_lpa: 14.5,
      observed_salary_difference_lpa: 3.2,
      associated_roles: ['Data Scientist', 'AI Engineer'],
      associated_archetypes: ['IND-A1: Enterprise Core Development'],
      companions: ['SQL', 'Django'],
    };

    const medianLpa = rawIndiaResponse.observed_median_salary_lpa ?? rawIndiaResponse.median_salary ?? 0;
    const deltaLpa = rawIndiaResponse.observed_salary_difference_lpa ?? rawIndiaResponse.delta_vs_cohort ?? 0;
    const roles = rawIndiaResponse.associated_roles ?? rawIndiaResponse.roles ?? [];
    const archetypes = rawIndiaResponse.associated_archetypes ?? rawIndiaResponse.archetypes ?? [];

    expect(medianLpa).toBe(14.5);
    expect(deltaLpa).toBe(3.2);
    expect(roles).toEqual(['Data Scientist', 'AI Engineer']);
    expect(archetypes).toEqual(['IND-A1: Enterprise Core Development']);
  });

  it('does not produce NaN or unhandled nulls when fallback fields are accessed', () => {
    const emptyDetail: SkillDetail = {
      skill: 'unknown_skill',
    };

    const median = emptyDetail.median_salary ?? emptyDetail.median_with ?? 0;
    const prevalence = emptyDetail.prevalence_pct ?? emptyDetail.prevalence ?? 0;
    const delta = emptyDetail.delta_vs_cohort ?? emptyDetail.delta ?? 0;
    const roles = emptyDetail.roles ?? emptyDetail.associated_roles ?? [];

    expect(Number.isNaN(median)).toBe(false);
    expect(median).toBe(0);
    expect(prevalence).toBe(0);
    expect(delta).toBe(0);
    expect(roles).toEqual([]);
  });
});
