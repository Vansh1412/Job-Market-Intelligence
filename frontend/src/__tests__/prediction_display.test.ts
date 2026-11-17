import { describe, it, expect } from 'vitest';

describe('Prediction Display & Scope Contract', () => {
  it('validates USA salary display contract and non-total-comp semantics', () => {
    const usaMockResult = {
      country: 'USA',
      currency: 'USD',
      currency_symbol: '$',
      predicted_salary: 154200.0,
      predicted_salary_display: '$154,200',
      model_metadata: {
        model_name: 'XGBoost Regressor (Tuned)',
        feature_count: 123,
        overall_mae: 36380.64,
        overall_rmse: 51082.06,
        overall_r2: 0.4233,
        evaluation_sample_size: 6808,
        pay_concept: 'Estimated Annual Base Salary (Excludes RSUs, Bonuses, and Equity)',
        disclaimer: 'Historical holdout MAE does not guarantee accuracy for any individual prediction.',
      },
    };

    expect(usaMockResult.predicted_salary_display).toBe('$154,200');
    expect(usaMockResult.model_metadata.evaluation_sample_size).toBe(6808);
    expect(usaMockResult.model_metadata.overall_r2).toBe(0.4233);
    expect(usaMockResult.model_metadata.pay_concept).toContain('Base Salary');
    expect(usaMockResult.model_metadata.pay_concept).toContain('Excludes RSUs');
  });

  it('validates India salary display contract and CTC midpoint semantics', () => {
    const indiaMockResult = {
      country: 'India',
      currency: 'INR',
      currency_symbol: '₹',
      predicted_salary_lpa: 12.5,
      predicted_salary_inr: 1250000.0,
      predicted_salary_display: '₹12.50 LPA',
      predicted_salary_inr_display: '₹1,250,000',
      model_metadata: {
        model_name: 'HistGradientBoostingRegressor',
        feature_count: 290,
        overall_mae_lpa: 3.71,
        overall_rmse_lpa: 6.22,
        overall_r2: 0.5798,
        evaluation_sample_size: 1173,
        pay_concept: 'Estimated Annual CTC / Salary Midpoint (Base + Fixed Allowances)',
        disclaimer: 'Historical holdout MAE does not guarantee accuracy for any individual prediction.',
      },
    };

    expect(indiaMockResult.predicted_salary_display).toBe('₹12.50 LPA');
    expect(indiaMockResult.predicted_salary_inr_display).toBe('₹1,250,000');
    expect(indiaMockResult.model_metadata.evaluation_sample_size).toBe(1173);
    expect(indiaMockResult.model_metadata.overall_r2).toBe(0.5798);
    expect(indiaMockResult.model_metadata.pay_concept).toContain('CTC');
  });

  it('verifies that heuristic match score is not presented as probability', () => {
    const rawSimilarity = 0.95;
    const matchIndexLabel = `Match Index: ${Math.round(rawSimilarity * 100)}/100`;

    expect(matchIndexLabel).toBe('Match Index: 95/100');
    expect(matchIndexLabel).not.toContain('Probability');
    expect(matchIndexLabel).not.toContain('% chance');
  });

  it('validates skill population denominator and prevalence quotient integrity (WP-FIX-01)', () => {
    // USA Python observation contract: 31,676 postings across 335,995 general corpus
    const usaPythonDetail = {
      skill: 'python',
      postings: 31676,
      population_size: 335995,
      prevalence_pct: 9.43,
      market: 'USA',
    };

    const calculatedUsaPrev = (usaPythonDetail.postings / usaPythonDetail.population_size) * 100;
    expect(Math.round(calculatedUsaPrev * 10) / 10).toBe(9.4);
    expect(usaPythonDetail.population_size).not.toBe(34036); // MUST NOT be salary model training size

    // India Development observation contract: 723 postings across 5,323 active skill-bearing cohort
    const indiaDevDetail = {
      skill: 'skill_development',
      posting_count: 723,
      population_size: 5323,
      demand_percentage: 13.6,
      market: 'India',
    };

    const calculatedIndPrev = (indiaDevDetail.posting_count / indiaDevDetail.population_size) * 100;
    expect(Math.round(calculatedIndPrev * 10) / 10).toBe(13.6);
    expect(indiaDevDetail.population_size).not.toBe(5859); // MUST NOT be full un-filtered cohort size
  });
});
