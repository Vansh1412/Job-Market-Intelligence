"""
Phase India-4 Reconciliation Script.
Cross-references every headline number in reports/india_phase4_modeling.md
against the underlying CSV and JSON artifacts.
"""
import json
import pandas as pd
import numpy as np

# Load artifacts
with open('models/india/final_evaluation.json', 'r', encoding='utf-8') as f:
    feval = json.load(f)
with open('models/india/final_model_metadata.json', 'r', encoding='utf-8') as f:
    fmeta = json.load(f)

df_holdout = pd.read_csv('reports/tables/india/holdout_model_results.csv')
df_base = pd.read_csv('reports/tables/india/baseline_improvement.csv')
df_raw_log = pd.read_csv('reports/tables/india/raw_vs_log_comparison.csv')
df_bv = pd.read_csv('reports/tables/india/bias_variance_metrics.csv')
df_role = pd.read_csv('reports/tables/india/error_by_role.csv')
df_city = pd.read_csv('reports/tables/india/error_by_city.csv')
df_exp = pd.read_csv('reports/tables/india/error_by_experience.csv')
df_sband = pd.read_csv('reports/tables/india/error_by_salary_band.csv')
df_hsal = pd.read_csv('reports/tables/india/high_salary_error.csv')
df_pi = pd.read_csv('reports/tables/india/permutation_importance.csv')
df_skill = pd.read_csv('reports/tables/india/skill_salary_association.csv')
df_cv = pd.read_csv('reports/tables/india/model_cv_summary.csv')

reconciliation = []

def add_check(metric, rep_val, art_val, src_art, tol=1e-4, notes=""):
    try:
        rep_f = float(str(rep_val).replace('₹', '').replace('LPA', '').replace('%', '').replace(',', '').strip())
        art_f = float(str(art_val).replace('₹', '').replace('LPA', '').replace('%', '').replace(',', '').strip())
        diff = abs(rep_f - art_f)
        status = 'PASS' if (diff <= tol or (art_f != 0 and diff / abs(art_f) <= 0.01)) else 'FAIL'
    except Exception:
        diff = 0.0 if str(rep_val).strip() == str(art_val).strip() else 1.0
        status = 'PASS' if diff == 0.0 else 'FAIL'
        
    reconciliation.append({
        'metric': metric,
        'report_value': rep_val,
        'artifact_value': art_val,
        'difference': diff,
        'status': status,
        'source_artifact': src_art,
        'notes': notes
    })

# Headline metrics
add_check('Cohort Sample Size (N)', '5859', str(fmeta['cohort_size']), 'final_model_metadata.json')
add_check('Training Sample Size', '4686', str(fmeta['train_samples']), 'final_model_metadata.json')
add_check('Holdout Sample Size', '1173', str(fmeta['holdout_samples']), 'final_model_metadata.json')
add_check('Candidate Predictors Count', '290', str(fmeta['feature_count']), 'final_model_metadata.json')
add_check('Dummy Holdout MAE (LPA)', '7.73', f"{df_holdout[df_holdout['model']=='Dummy']['holdout_mae_lpa'].values[0]:.2f}", 'holdout_model_results.csv')
add_check('Dummy Holdout RMSE (LPA)', '9.59', f"{df_holdout[df_holdout['model']=='Dummy']['holdout_rmse_lpa'].values[0]:.2f}", 'holdout_model_results.csv')
add_check('Winning Model Holdout MAE (INR)', '371473', f"{feval['holdout_metrics']['mae_inr']:.0f}", 'final_evaluation.json')
add_check('Winning Model Holdout MAE (LPA)', '3.71', f"{feval['holdout_metrics']['mae_lpa']:.2f}", 'final_evaluation.json')
add_check('Winning Model Holdout RMSE (INR)', '621881', f"{feval['holdout_metrics']['rmse_inr']:.0f}", 'final_evaluation.json')
add_check('Winning Model Holdout RMSE (LPA)', '6.22', f"{feval['holdout_metrics']['rmse_lpa']:.2f}", 'final_evaluation.json')
add_check('Winning Model Holdout R2', '0.5798', f"{feval['holdout_metrics']['r2']:.4f}", 'final_evaluation.json')
add_check('Winning Model Holdout Median AE (INR)', '207704', f"{feval['holdout_metrics']['median_ae_inr']:.0f}", 'final_evaluation.json')
add_check('Winning Model Holdout Median AE (LPA)', '2.08', f"{feval['holdout_metrics']['median_ae_lpa']:.2f}", 'final_evaluation.json')
add_check('Winning Model Holdout MAPE (%)', '35.22', f"{feval['holdout_metrics']['mape']:.2f}", 'final_evaluation.json')
add_check('Baseline MAE Improvement (%)', '51.92', f"{feval['baseline_improvement']['mae_improvement_pct']:.2f}", 'final_evaluation.json')

# Model Comparisons
h_xgb_tuned_log = df_holdout[(df_holdout['model']=='XGBoost_tuned') & (df_holdout['target_type']=='log')]
add_check('XGBoost Tuned Log Holdout MAE (LPA)', '3.76', f"{h_xgb_tuned_log['holdout_mae_lpa'].values[0]:.2f}", 'holdout_model_results.csv')

h_xgb_tuned_raw = df_holdout[(df_holdout['model']=='XGBoost_tuned') & (df_holdout['target_type']=='raw')]
add_check('XGBoost Tuned Raw Holdout RMSE (LPA)', '6.11', f"{h_xgb_tuned_raw['holdout_rmse_lpa'].values[0]:.2f}", 'holdout_model_results.csv')
add_check('XGBoost Tuned Raw Holdout R2', '0.5945', f"{h_xgb_tuned_raw['holdout_r2'].values[0]:.4f}", 'holdout_model_results.csv')

h_ridge_log = df_holdout[(df_holdout['model']=='Ridge_alpha10') & (df_holdout['target_type']=='log')]
add_check('Ridge Log Holdout MAE (LPA)', '4.17', f"{h_ridge_log['holdout_mae_lpa'].values[0]:.2f}", 'holdout_model_results.csv')

h_ridge_raw = df_holdout[(df_holdout['model']=='Ridge_alpha10') & (df_holdout['target_type']=='raw')]
add_check('Ridge Raw Holdout MAE (LPA)', '4.20', f"{h_ridge_raw['holdout_mae_lpa'].values[0]:.2f}", 'holdout_model_results.csv')

# Upper tail error
hsal_20 = df_hsal[df_hsal['cutoff_threshold']=='>= 20.0 LPA']
add_check('High-Salary >= 20 LPA Holdout MAE (LPA)', '8.06', f"{hsal_20['mae_lpa'].values[0]:.2f}", 'high_salary_error.csv')
add_check('High-Salary >= 20 LPA Bias / Mean Error (LPA)', '7.56', f"{hsal_20['mean_residual_lpa (bias)'].values[0]:.2f}", 'high_salary_error.csv')

hsal_40 = df_hsal[df_hsal['cutoff_threshold']=='>= 40.0 LPA']
add_check('High-Salary >= 40 LPA Holdout MAE (LPA)', '31.12', f"{hsal_40['mae_lpa'].values[0]:.2f}", 'high_salary_error.csv')
add_check('High-Salary >= 40 LPA Bias / Mean Error (LPA)', '31.12', f"{hsal_40['mean_residual_lpa (bias)'].values[0]:.2f}", 'high_salary_error.csv')

# Experience Subgroups
exp_entry = df_exp[df_exp['experience_band'].str.startswith('0-2')]
add_check('Entry Experience (0-2y) Holdout MAE (LPA)', '0.84', f"{exp_entry['mae_lpa'].values[0]:.2f}", 'error_by_experience.csv', notes="Corrected from initial draft typo (1.62 -> 0.84 LPA)")

exp_mid = df_exp[df_exp['experience_band'].str.startswith('3-5')]
add_check('Mid Experience (3-5y) Holdout MAE (LPA)', '2.55', f"{exp_mid['mae_lpa'].values[0]:.2f}", 'error_by_experience.csv', notes="Corrected from initial draft typo (2.74 -> 2.55 LPA)")

exp_senior = df_exp[df_exp['experience_band'].str.startswith('6-10')]
add_check('Senior Experience (6-10y) Holdout MAE (LPA)', '4.50', f"{exp_senior['mae_lpa'].values[0]:.2f}", 'error_by_experience.csv', notes="Corrected from initial draft typo (4.87 -> 4.50 LPA)")

# Salary Band Subgroups
sband_low = df_sband[df_sband['salary_band']=='1.2-5 LPA']
add_check('Salary Band 1.2-5 LPA Holdout MAE (LPA)', '1.31', f"{sband_low['mae_lpa'].values[0]:.2f}", 'error_by_salary_band.csv')

sband_mid = df_sband[df_sband['salary_band']=='10-20 LPA']
add_check('Salary Band 10-20 LPA Holdout MAE (LPA)', '3.33', f"{sband_mid['mae_lpa'].values[0]:.2f}", 'error_by_salary_band.csv')
add_check('Salary Band 10-20 LPA Bias (LPA)', '0.38', f"{sband_mid['mean_residual_lpa'].values[0]:.2f}", 'error_by_salary_band.csv')

# Role Subgroups
role_de = df_role[df_role['role']=='Data Engineer']
add_check('Data Engineer Holdout MAE (LPA)', '3.13', f"{role_de['mae_lpa'].values[0]:.2f}", 'error_by_role.csv')

role_se = df_role[df_role['role']=='Software Engineer']
add_check('Software Engineer Holdout MAE (LPA)', '4.12', f"{role_se['mae_lpa'].values[0]:.2f}", 'error_by_role.csv')

role_other = df_role[df_role['role']=='Other Technology']
add_check('Other Technology Holdout MAE (LPA)', '3.37', f"{role_other['mae_lpa'].values[0]:.2f}", 'error_by_role.csv')

# Save table
df_rec = pd.DataFrame(reconciliation)
df_rec.to_csv('reports/tables/india/phase4_reconciliation.csv', index=False)
print(f"Reconciliation table generated with {len(df_rec)} metrics audited.")
print(f"Pass count: {(df_rec['status'] == 'PASS').sum()} / {len(df_rec)}")
