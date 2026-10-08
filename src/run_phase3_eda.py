"""
INT234 Job Market Intelligence: Phase 3 Exploratory Data Analysis & Statistical Discovery
Execution Script:
  - Generates 10 analytical CSV tables in reports/tables/phase3/
  - Generates 10 publication-quality figures in reports/figures/phase3/
  - Computes exact statistical metrics saved to reports/tables/phase3/eda_metrics.json
  - STRICT COMPLIANCE: ZERO PCA, ZERO K-MEANS, ZERO REGRESSION, ZERO DATA FABRICATION.
"""

import os
import sys
import json
import itertools
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

# Set random seed
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Aesthetics & plotting styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16
sns.set_theme(style="whitegrid", palette="muted")

print("=" * 75)
print("INT234 JOB MARKET INTELLIGENCE — PHASE 3 EXPLORATORY DATA ANALYSIS")
print("=" * 75)

base_dir = r"e:\Job Market"
processed_dir = os.path.join(base_dir, "data", "processed")
fig_dir = os.path.join(base_dir, "reports", "figures", "phase3")
table_dir = os.path.join(base_dir, "reports", "tables", "phase3")

os.makedirs(fig_dir, exist_ok=True)
os.makedirs(table_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# STEP 1: LOAD VERIFIED DATASETS
# -----------------------------------------------------------------------------
print("\n[Step 1] Loading Phase 2.1 Processed Datasets...")
cleaned_jobs_path = os.path.join(processed_dir, "cleaned_jobs.parquet")
modeling_path = os.path.join(processed_dir, "modeling_dataset.parquet")
tech_matrix_path = os.path.join(processed_dir, "skill_matrix_technical.parquet")

df_corpus = pd.read_parquet(cleaned_jobs_path)
df_model = pd.read_parquet(modeling_path)
df_tech_skills = pd.read_parquet(tech_matrix_path)

n_corpus = len(df_corpus)
n_model = len(df_model)
print(f"  Deduplicated corpus: {n_corpus:,} rows, {df_corpus.shape[1]} columns")
print(f"  Modeling dataset:    {n_model:,} rows, {df_model.shape[1]} columns")
print(f"  Technical skills:    {df_tech_skills.shape[1]} skills across corpus")

# Standardize salary variable name alias
df_model['annual_salary_usd'] = df_model['salary_midpoint']

# -----------------------------------------------------------------------------
# STEP 2: DATASET POPULATION & SELECTION FUNNEL
# -----------------------------------------------------------------------------
print("\n[Step 2] Computing Dataset Selection Funnel & Bias Audit...")
n_raw = 394300
n_dedup = 335995
n_tech_corpus = int(df_corpus['is_tech_role'].sum())
n_tech_skills = int((df_corpus['num_skills'] > 0).sum())

has_usd_annual = (
    df_corpus['salary_min'].notnull() &
    df_corpus['salary_max'].notnull() &
    (df_corpus['salary_period'].astype(str).str.lower() == 'year') &
    (df_corpus['salary_currency'] == 'USD') &
    df_corpus['salary_is_valid']
)
n_disclosed_corpus = int(has_usd_annual.sum())
n_disclosed_tech = int((has_usd_annual & df_corpus['is_tech_role']).sum())
n_below_30k = int((has_usd_annual & df_corpus['is_tech_role'] & (df_corpus['salary_midpoint'] < 30000)).sum())
n_above_600k = int((has_usd_annual & df_corpus['is_tech_role'] & (df_corpus['salary_midpoint'] > 600000)).sum())

funnel_df = pd.DataFrame([
    {"Stage": "1. Raw ATS Ingestion", "Count": n_raw, "Retention_vs_Prior": 1.0, "Share_of_Raw": 1.0},
    {"Stage": "2. Casing Deduplication", "Count": n_dedup, "Retention_vs_Prior": n_dedup / n_raw, "Share_of_Raw": n_dedup / n_raw},
    {"Stage": "3. Verified Tech Postings (Corpus)", "Count": n_tech_corpus, "Retention_vs_Prior": n_tech_corpus / n_dedup, "Share_of_Raw": n_tech_corpus / n_raw},
    {"Stage": "4. Salary Disclosed (USD Annual)", "Count": n_disclosed_tech, "Retention_vs_Prior": n_disclosed_tech / n_tech_corpus, "Share_of_Raw": n_disclosed_tech / n_raw},
    {"Stage": "5. Final Modeling Cohort ($30k-$600k)", "Count": n_model, "Retention_vs_Prior": n_model / n_disclosed_tech, "Share_of_Raw": n_model / n_raw}
])
funnel_df.to_csv(os.path.join(table_dir, "dataset_selection_funnel.csv"), index=False)
print("  Selection funnel saved: dataset_selection_funnel.csv")

# -----------------------------------------------------------------------------
# STEP 3: SALARY TARGET & LOG-SALARY STATISTICAL PROFILE
# -----------------------------------------------------------------------------
print("\n[Step 3] Computing Salary Distribution Profiles (Raw vs Log)...")

sal = df_model['annual_salary_usd']
log_sal = np.log1p(sal)
df_model['log1p_salary'] = log_sal

def get_dist_stats(series, name):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return {
        "Variable": name,
        "N": len(series),
        "Mean": float(series.mean()),
        "Std_Dev": float(series.std()),
        "Variance": float(series.var()),
        "Median": float(series.median()),
        "Q1": float(q1),
        "Q3": float(q3),
        "IQR": float(iqr),
        "Min": float(series.min()),
        "Max": float(series.max()),
        "Skewness": float(series.skew()),
        "Kurtosis": float(series.kurtosis())
    }

salary_summary_df = pd.DataFrame([
    get_dist_stats(sal, "annual_salary_usd (Raw USD)"),
    get_dist_stats(df_model['log_salary'], "log_salary (ln(y))"),
    get_dist_stats(log_sal, "log1p_salary (ln(y+1))")
])
salary_summary_df.to_csv(os.path.join(table_dir, "salary_summary.csv"), index=False)
print("  Salary summary table saved: salary_summary.csv")

# FIGURE 01: Raw Salary Distribution
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(sal, kde=True, bins=60, color='#1f77b4', edgecolor='black', alpha=0.6, ax=ax)
ax.axvline(sal.median(), color='#d62728', linestyle='--', linewidth=2, label=f'Median: ${sal.median():,.0f}')
ax.axvline(sal.mean(), color='#2ca02c', linestyle='-', linewidth=2, label=f'Mean: ${sal.mean():,.0f}')
ax.axvline(sal.quantile(0.25), color='#7f7f7f', linestyle=':', linewidth=1.5, label=f'Q1 (25%): ${sal.quantile(0.25):,.0f}')
ax.axvline(sal.quantile(0.75), color='#7f7f7f', linestyle=':', linewidth=1.5, label=f'Q3 (75%): ${sal.quantile(0.75):,.0f}')
ax.set_title("Empirical Distribution of Annual Technology Salaries (USD)", pad=15, fontweight='bold')
ax.set_xlabel("Annual Salary Midpoint (USD)")
ax.set_ylabel("Frequency (Job Postings)")
ax.xaxis.set_major_formatter('${x:,.0f}')
ax.legend(frameon=True, facecolor='white', loc='upper right')
plt.tight_layout()
fig_01_path = os.path.join(fig_dir, "01_salary_distribution.png")
plt.savefig(fig_01_path)
plt.close()
print(f"  Figure saved: {fig_01_path}")

# FIGURE 02: Log Salary Distribution with Fitted Gaussian
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df_model['log_salary'], kde=True, bins=50, color='#2ca02c', stat='density', edgecolor='black', alpha=0.6, ax=ax)
# Overlay Gaussian curve
x_vals = np.linspace(df_model['log_salary'].min(), df_model['log_salary'].max(), 200)
pdf_vals = stats.norm.pdf(x_vals, df_model['log_salary'].mean(), df_model['log_salary'].std())
ax.plot(x_vals, pdf_vals, 'r--', linewidth=2.5, label=f'Theoretical Gaussian Fit (mu={df_model["log_salary"].mean():.2f}, sigma={df_model["log_salary"].std():.2f})')
ax.axvline(df_model['log_salary'].median(), color='#d62728', linestyle='-', linewidth=2, label=f'Median ln(y): {df_model["log_salary"].median():.2f}')
ax.set_title("Log-Transformed Salary Distribution: ln(Annual Salary USD)", pad=15, fontweight='bold')
ax.set_xlabel("Log Salary (ln(annual_salary_usd))")
ax.set_ylabel("Probability Density")
ax.legend(frameon=True, facecolor='white', loc='upper left')
plt.tight_layout()
fig_02_path = os.path.join(fig_dir, "02_log_salary_distribution.png")
plt.savefig(fig_02_path)
plt.close()
print(f"  Figure saved: {fig_02_path}")

# -----------------------------------------------------------------------------
# STEP 4: SENIORITY PROFILING & STATISTICAL COMPARISONS
# -----------------------------------------------------------------------------
print("\n[Step 4] Profiling Salary by Seniority...")

seniority_order = ['Intern', 'Junior / Entry', 'Mid / Unspecified', 'Senior', 'Lead / Principal / Executive']
sen_records = []
sen_groups = []

for sen in seniority_order:
    sub = df_model[df_model['seniority'] == sen]['annual_salary_usd']
    sen_groups.append(sub.values)
    sen_records.append({
        "Seniority": sen,
        "N": len(sub),
        "Share": len(sub) / n_model,
        "Median_Salary": float(sub.median()),
        "Mean_Salary": float(sub.mean()),
        "Std_Dev": float(sub.std()),
        "Q1": float(sub.quantile(0.25)),
        "Q3": float(sub.quantile(0.75)),
        "IQR": float(sub.quantile(0.75) - sub.quantile(0.25)),
        "Min": float(sub.min()),
        "Max": float(sub.max())
    })

salary_by_sen_df = pd.DataFrame(sen_records)
salary_by_sen_df.to_csv(os.path.join(table_dir, "salary_by_seniority.csv"), index=False)
print("  Salary by seniority table saved: salary_by_seniority.csv")

# Kruskal-Wallis H-test across seniority groups
h_stat_sen, p_val_sen = stats.kruskal(*sen_groups)
# Epsilon-squared effect size for Kruskal-Wallis: (H - k + 1) / (N - k)
k_sen = len(seniority_order)
eps2_sen = (h_stat_sen - k_sen + 1) / (n_model - k_sen)
print(f"  Seniority Kruskal-Wallis: H = {h_stat_sen:,.2f}, p = {p_val_sen:.2e}, eps^2 = {eps2_sen:.4f}")

# FIGURE 03: Salary by Seniority Boxplot + Violin
fig, ax = plt.subplots(figsize=(11, 6))
palette_sen = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594"]
sns.boxplot(data=df_model, x='seniority', y='annual_salary_usd', order=seniority_order,
            hue='seniority', palette=palette_sen, legend=False, showmeans=True,
            meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "white", "markersize": 7},
            ax=ax, flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.3})
ax.set_title("Annual Compensation by Seniority Tier (White Diamond = Group Mean)", pad=15, fontweight='bold')
ax.set_xlabel("Career Level / Seniority")
ax.set_ylabel("Annual Salary Midpoint (USD)")
ax.yaxis.set_major_formatter('${x:,.0f}')
# Add sample size labels
for idx, sen in enumerate(seniority_order):
    n_count = len(df_model[df_model['seniority'] == sen])
    med = df_model[df_model['seniority'] == sen]['annual_salary_usd'].median()
    ax.text(idx, 580000, f"N={n_count:,}\nMed: ${med/1000:.0f}k", ha='center', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#ccc'))
plt.tight_layout()
fig_03_path = os.path.join(fig_dir, "03_salary_by_seniority.png")
plt.savefig(fig_03_path)
plt.close()
print(f"  Figure saved: {fig_03_path}")

# -----------------------------------------------------------------------------
# STEP 5: ROLE FAMILY PROFILING & STATISTICAL COMPARISONS
# -----------------------------------------------------------------------------
print("\n[Step 5] Profiling Salary by Role Family...")

rf_records = []
rf_groups = []
rf_names = []

for rf, sub_df in df_model.groupby('role_family'):
    sals = sub_df['annual_salary_usd']
    rf_groups.append(sals.values)
    rf_names.append(rf)
    rf_records.append({
        "Role_Family": rf,
        "N": len(sals),
        "Share": len(sals) / n_model,
        "Median_Salary": float(sals.median()),
        "Mean_Salary": float(sals.mean()),
        "Std_Dev": float(sals.std()),
        "Q1": float(sals.quantile(0.25)),
        "Q3": float(sals.quantile(0.75)),
        "IQR": float(sals.quantile(0.75) - sals.quantile(0.25)),
        "Min": float(sals.min()),
        "Max": float(sals.max())
    })

salary_by_rf_df = pd.DataFrame(rf_records).sort_values(by="Median_Salary", ascending=False)
salary_by_rf_df.to_csv(os.path.join(table_dir, "salary_by_role_family.csv"), index=False)
print("  Salary by role family table saved: salary_by_role_family.csv")

h_stat_rf, p_val_rf = stats.kruskal(*rf_groups)
k_rf = len(rf_names)
eps2_rf = (h_stat_rf - k_rf + 1) / (n_model - k_rf)
print(f"  Role Family Kruskal-Wallis: H = {h_stat_rf:,.2f}, p = {p_val_rf:.2e}, eps^2 = {eps2_rf:.4f}")

# FIGURE 04: Salary by Role Family (Horizontal Bar of Medians with IQR error bars)
sorted_rf = salary_by_rf_df.sort_values(by="Median_Salary", ascending=True)
fig, ax = plt.subplots(figsize=(12, 8))
y_pos = np.arange(len(sorted_rf))

# Bar of medians
bars = ax.barh(y_pos, sorted_rf['Median_Salary'], color='#4a7c59', alpha=0.85, edgecolor='black')
# Error bars for Q1 and Q3
xerr_low = sorted_rf['Median_Salary'] - sorted_rf['Q1']
xerr_high = sorted_rf['Q3'] - sorted_rf['Median_Salary']
ax.errorbar(sorted_rf['Median_Salary'], y_pos, xerr=[xerr_low, xerr_high], fmt='none', ecolor='#d62728', elinewidth=2, capsize=4)

ax.set_yticks(y_pos)
ax.set_yticklabels(sorted_rf['Role_Family'])
ax.xaxis.set_major_formatter('${x:,.0f}')
ax.axvline(sal.median(), color='#d62728', linestyle='--', linewidth=1.5, label=f'Cohort Median: ${sal.median():,.0f}')
ax.set_title("Median Annual Salary by Technology Role Family (Error Bars = [Q1, Q3])", pad=15, fontweight='bold')
ax.set_xlabel("Median Annual Salary (USD)")
ax.legend(loc='lower right', frameon=True, facecolor='white')

# Label values and sample sizes on bars
for i, (med, n_cnt) in enumerate(zip(sorted_rf['Median_Salary'], sorted_rf['N'])):
    ax.text(med + 3000, i, f"${med/1000:.0f}k (N={n_cnt:,})", va='center', fontsize=9, fontweight='semibold')

ax.set_xlim(0, 310000)
plt.tight_layout()
fig_04_path = os.path.join(fig_dir, "04_salary_by_role_family.png")
plt.savefig(fig_04_path)
plt.close()
print(f"  Figure saved: {fig_04_path}")

# -----------------------------------------------------------------------------
# STEP 6: TECHNICAL SKILL FREQUENCY & PREVALENCE
# -----------------------------------------------------------------------------
print("\n[Step 6] Calculating Technical Skill Frequencies across Corpus and Modeling Set...")

skill_cols = [c for c in df_model.columns if c.startswith('skill_') and c in [f"skill_{s.replace('-', '_').replace('.', '_')}" for s in df_tech_skills.columns]]

# Corpus frequencies
corpus_skill_counts = df_tech_skills.sum().sort_values(ascending=False)
model_skill_df = df_model[[c for c in df_model.columns if c.startswith('skill_')]]
model_tech_cols = [c for c in model_skill_df.columns if c in df_tech_skills.columns or c in [f"skill_{s.replace('-', '_').replace('.', '_')}" for s in df_tech_skills.columns]]

skill_freq_records = []
for orig_name in df_tech_skills.columns:
    mod_col = f"skill_{orig_name.replace('-', '_').replace('.', '_')}" if not orig_name.startswith('skill_') else orig_name
    c_count = int(corpus_skill_counts.get(orig_name, 0))
    m_count = int(df_model[mod_col].sum()) if mod_col in df_model.columns else 0
    m_prev = m_count / n_model
    c_prev = c_count / n_corpus
    skill_freq_records.append({
        "Skill": orig_name.replace('skill_', '').replace('_', '-'),
        "Modeling_Count": m_count,
        "Modeling_Prevalence": m_prev,
        "Corpus_Count": c_count,
        "Corpus_Prevalence": c_prev,
        "IDF_Score": float(np.log(n_model / (m_count + 1)))
    })

skill_freq_df = pd.DataFrame(skill_freq_records).sort_values(by="Modeling_Count", ascending=False)
skill_freq_df.to_csv(os.path.join(table_dir, "skill_frequency.csv"), index=False)
print("  Skill frequency table saved: skill_frequency.csv")

# FIGURE 05: Top 25 Technical Skills by Frequency
top_25_skills = skill_freq_df.head(25).sort_values(by="Modeling_Count", ascending=True)
fig, ax = plt.subplots(figsize=(11, 8))
y_pos = np.arange(len(top_25_skills))
bars = ax.barh(y_pos, top_25_skills['Modeling_Count'], color='#1f77b4', edgecolor='black', alpha=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(top_25_skills['Skill'])
ax.xaxis.set_major_formatter('{x:,.0f}')
ax.set_title("Top 25 Technical Skills by Job Posting Frequency (Modeling Cohort N = 34,036)", pad=15, fontweight='bold')
ax.set_xlabel("Number of Job Postings Citing Skill")

for i, (cnt, prev) in enumerate(zip(top_25_skills['Modeling_Count'], top_25_skills['Modeling_Prevalence'])):
    ax.text(cnt + 200, i, f"{cnt:,} ({prev:.1%})", va='center', fontsize=9)

ax.set_xlim(0, top_25_skills['Modeling_Count'].max() * 1.15)
plt.tight_layout()
fig_05_path = os.path.join(fig_dir, "05_top_technical_skills.png")
plt.savefig(fig_05_path)
plt.close()
print(f"  Figure saved: {fig_05_path}")

# -----------------------------------------------------------------------------
# STEP 7: SKILL-SALARY ASSOCIATIONS & PREMIUMS (RQ1)
# -----------------------------------------------------------------------------
print("\n[Step 7] Evaluating Skill-Salary Associations (RQ1 Preparation)...")

MIN_SUPPORT = 100
cohort_median = float(sal.median())
cohort_mean = float(sal.mean())

skill_assoc_records = []
p_values = []

for _, row in skill_freq_df.iterrows():
    s_name = row['Skill']
    m_col = f"skill_{s_name.replace('-', '_').replace('.', '_')}"
    if m_col not in df_model.columns:
        continue
    
    has_skill = df_model[m_col] == 1
    n_with = int(has_skill.sum())
    
    if n_with < MIN_SUPPORT:
        continue
    
    sal_with = df_model.loc[has_skill, 'annual_salary_usd']
    sal_without = df_model.loc[~has_skill, 'annual_salary_usd']
    
    med_with = float(sal_with.median())
    mean_with = float(sal_with.mean())
    std_with = float(sal_with.std())
    iqr_with = float(sal_with.quantile(0.75) - sal_with.quantile(0.25))
    
    premium = med_with - cohort_median
    premium_pct = (premium / cohort_median) * 100.0
    
    # Nonparametric Mann-Whitney U test
    u_stat, p_val = stats.mannwhitneyu(sal_with, sal_without, alternative='two-sided')
    # Rank-biserial correlation: r = 1 - 2*U / (n1 * n2)
    n1, n2 = len(sal_with), len(sal_without)
    rank_biserial = 1.0 - (2.0 * u_stat) / (n1 * n2)
    
    p_values.append(p_val)
    skill_assoc_records.append({
        "Skill": s_name,
        "Support_N": n_with,
        "Prevalence": n_with / n_model,
        "Median_Salary": med_with,
        "Mean_Salary": mean_with,
        "Std_Dev": std_with,
        "IQR": iqr_with,
        "Salary_Diff_vs_Cohort": premium,
        "Premium_Percentage": premium_pct,
        "Mann_Whitney_U": float(u_stat),
        "P_Value_Raw": float(p_val),
        "Rank_Biserial_Effect": float(rank_biserial)
    })

# Benjamini-Hochberg FDR correction
skill_assoc_df = pd.DataFrame(skill_assoc_records)
m_tests = len(skill_assoc_df)
sorted_indices = np.argsort(skill_assoc_df['P_Value_Raw'].values)
adjusted_p = np.zeros(m_tests)
# BH step-up
p_sorted = skill_assoc_df['P_Value_Raw'].values[sorted_indices]
for rank, p in enumerate(p_sorted, 1):
    adj = p * m_tests / rank
    adjusted_p[rank - 1] = min(adj, 1.0)
# Ensure monotonicity
for i in range(m_tests - 2, -1, -1):
    adjusted_p[i] = min(adjusted_p[i], adjusted_p[i + 1])

skill_assoc_df['P_Value_FDR_BH'] = 0.0
skill_assoc_df.loc[sorted_indices, 'P_Value_FDR_BH'] = adjusted_p

skill_assoc_df = skill_assoc_df.sort_values(by="Premium_Percentage", ascending=False)
skill_assoc_df.to_csv(os.path.join(table_dir, "skill_salary_association.csv"), index=False)

# Dedicated premium table
premium_df = skill_assoc_df[['Skill', 'Support_N', 'Prevalence', 'Median_Salary', 'Salary_Diff_vs_Cohort', 'Premium_Percentage', 'P_Value_FDR_BH', 'Rank_Biserial_Effect']]
premium_df.to_csv(os.path.join(table_dir, "skill_salary_premium.csv"), index=False)
print("  Skill-salary association & premium tables saved.")

# FIGURE 06: Skill Frequency vs Median Salary Scatter
fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(skill_assoc_df['Support_N'], skill_assoc_df['Median_Salary'],
                     c=skill_assoc_df['Premium_Percentage'], cmap='coolwarm',
                     s=skill_assoc_df['Support_N'] / 15 + 40, edgecolors='black', alpha=0.85)
ax.set_xscale('log')
ax.axhline(cohort_median, color='black', linestyle='--', linewidth=1.5, label=f'Cohort Median (${cohort_median:,.0f})')
ax.set_title("Technical Skill Prevalence vs. Associated Median Salary (RQ1)", pad=15, fontweight='bold')
ax.set_xlabel("Skill Frequency / Job Posting Count (Log Scale, Min Support N >= 100)")
ax.set_ylabel("Median Annual Salary (USD)")
ax.yaxis.set_major_formatter('${x:,.0f}')
ax.xaxis.set_major_formatter('{x:,.0f}')

# Label notable skills
notable = skill_assoc_df.head(10)['Skill'].tolist() + skill_assoc_df.tail(5)['Skill'].tolist() + ['python', 'sql', 'aws', 'java', 'docker', 'kubernetes', 'spark', 'react']
for _, row in skill_assoc_df.iterrows():
    if row['Skill'] in notable:
        ax.annotate(row['Skill'], (row['Support_N'], row['Median_Salary']),
                    textcoords="offset points", xytext=(5, 5), fontsize=8.5, fontweight='semibold')

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Salary Premium vs Cohort Median (%)')
ax.legend(loc='lower left', frameon=True, facecolor='white')
plt.tight_layout()
fig_06_path = os.path.join(fig_dir, "06_skill_salary_association.png")
plt.savefig(fig_06_path)
plt.close()
print(f"  Figure saved: {fig_06_path}")

# FIGURE 07: Top 20 Technical Skills by Salary Premium (%)
top_20_prem = skill_assoc_df.head(20).sort_values(by="Premium_Percentage", ascending=True)
fig, ax = plt.subplots(figsize=(11, 8))
y_pos = np.arange(len(top_20_prem))
colors = ['#d62728' if x < 0 else '#2ca02c' for x in top_20_prem['Premium_Percentage']]
bars = ax.barh(y_pos, top_20_prem['Premium_Percentage'], color=colors, edgecolor='black', alpha=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(top_20_prem['Skill'])
ax.axvline(0, color='black', linewidth=1)
ax.set_title("Top 20 Technical Skills by Salary Premium Relative to Cohort Median (N >= 100)", pad=15, fontweight='bold')
ax.set_xlabel("Salary Premium over Cohort Median ($180,373) [%]")
for i, (prem, med, n_cnt) in enumerate(zip(top_20_prem['Premium_Percentage'], top_20_prem['Median_Salary'], top_20_prem['Support_N'])):
    ax.text(prem + 0.3, i, f"+{prem:.1f}% (${med/1000:.0f}k, N={n_cnt:,})", va='center', fontsize=9, fontweight='semibold')
ax.set_xlim(0, top_20_prem['Premium_Percentage'].max() * 1.25)
plt.tight_layout()
fig_07_path = os.path.join(fig_dir, "07_skill_salary_premium.png")
plt.savefig(fig_07_path)
plt.close()
print(f"  Figure saved: {fig_07_path}")

# -----------------------------------------------------------------------------
# STEP 8: PAIRWISE SKILL COMBINATION ANALYSIS (RQ1)
# -----------------------------------------------------------------------------
print("\n[Step 8] Evaluating Pairwise Technical Skill Combinations (RQ1)...")

top_35_skills = skill_freq_df.head(35)['Skill'].tolist()
pair_records = []

# Skill median map for single skills
skill_median_map = {row['Skill']: row['Median_Salary'] for _, row in skill_assoc_df.iterrows()}

for s1, s2 in itertools.combinations(top_35_skills, 2):
    col1 = f"skill_{s1.replace('-', '_').replace('.', '_')}"
    col2 = f"skill_{s2.replace('-', '_').replace('.', '_')}"
    if col1 not in df_model.columns or col2 not in df_model.columns:
        continue
    
    both_mask = (df_model[col1] == 1) & (df_model[col2] == 1)
    pair_count = int(both_mask.sum())
    
    if pair_count < MIN_SUPPORT:
        continue
    
    pair_sals = df_model.loc[both_mask, 'annual_salary_usd']
    pair_med = float(pair_sals.median())
    pair_mean = float(pair_sals.mean())
    pair_prem_cohort = pair_med - cohort_median
    pair_prem_pct = (pair_prem_cohort / cohort_median) * 100.0
    
    # Synergistic premium: compare combination to individual skills
    med1 = skill_median_map.get(s1, cohort_median)
    med2 = skill_median_map.get(s2, cohort_median)
    max_individual = max(med1, med2)
    synergy_prem = pair_med - max_individual
    
    pair_records.append({
        "Skill_A": s1,
        "Skill_B": s2,
        "Pair_Name": f"{s1} + {s2}",
        "Co_Occurrence_Count": pair_count,
        "Co_Occurrence_Prevalence": pair_count / n_model,
        "Median_Salary": pair_med,
        "Mean_Salary": pair_mean,
        "Premium_vs_Cohort": pair_prem_cohort,
        "Premium_Percentage": pair_prem_pct,
        "Max_Individual_Median": max_individual,
        "Synergy_Premium": synergy_prem
    })

skill_pair_df = pd.DataFrame(pair_records).sort_values(by="Median_Salary", ascending=False)
skill_pair_df.to_csv(os.path.join(table_dir, "skill_pair_analysis.csv"), index=False)
print(f"  Skill pair analysis saved: skill_pair_analysis.csv ({len(skill_pair_df)} pairs evaluated)")

# -----------------------------------------------------------------------------
# STEP 9: SKILL CO-OCCURRENCE MATRIX & HEATMAP (RQ2 PREPARATION)
# -----------------------------------------------------------------------------
print("\n[Step 9] Generating Skill Co-Occurrence Structure (RQ2 Preparation)...")

top_25_list = skill_freq_df.head(25)['Skill'].tolist()
top_25_cols = [f"skill_{s.replace('-', '_').replace('.', '_')}" for s in top_25_list]

sub_matrix = df_model[top_25_cols].values.astype(np.float64)
cooccur_counts = np.dot(sub_matrix.T, sub_matrix)
cooccur_df = pd.DataFrame(cooccur_counts.astype(int), index=top_25_list, columns=top_25_list)
cooccur_df.to_csv(os.path.join(table_dir, "skill_cooccurrence.csv"))

# Jaccard Similarity Matrix: J(A, B) = |A ∩ B| / |A ∪ B| = count(A & B) / (count(A) + count(B) - count(A & B))
diag = np.diag(cooccur_counts)
jaccard_matrix = np.zeros_like(cooccur_counts, dtype=float)
for i in range(len(top_25_list)):
    for j in range(len(top_25_list)):
        union = diag[i] + diag[j] - cooccur_counts[i, j]
        jaccard_matrix[i, j] = cooccur_counts[i, j] / union if union > 0 else 0.0

jaccard_df = pd.DataFrame(jaccard_matrix, index=top_25_list, columns=top_25_list)

# FIGURE 08: Skill Co-occurrence / Jaccard Heatmap
fig, ax = plt.subplots(figsize=(14, 12))
mask = np.triu(np.ones_like(jaccard_df, dtype=bool))
sns.heatmap(jaccard_df, mask=mask, cmap='YlGnBu', annot=True, fmt='.2f', annot_kws={"size": 7.5},
            cbar_kws={'label': 'Jaccard Similarity Coefficient'}, linewidths=0.5, ax=ax)
ax.set_title("Pairwise Technical Skill Co-occurrence Heatmap (Jaccard Index) [RQ2 Preparation]", pad=20, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontsize=9.5)
plt.yticks(rotation=0, fontsize=9.5)
plt.tight_layout()
fig_08_path = os.path.join(fig_dir, "08_skill_cooccurrence_heatmap.png")
plt.savefig(fig_08_path)
plt.close()
print(f"  Figure saved: {fig_08_path}")

# -----------------------------------------------------------------------------
# STEP 10: GEOGRAPHIC & REMOTE WORK ANALYSIS
# -----------------------------------------------------------------------------
print("\n[Step 10] Analyzing Geographic Compensation Patterns & Remote Work...")

loc_records = []
for city, sub_df in df_model.groupby('city_clean'):
    sals = sub_df['annual_salary_usd']
    loc_records.append({
        "City": city,
        "N": len(sals),
        "Share": len(sals) / n_model,
        "Median_Salary": float(sals.median()),
        "Mean_Salary": float(sals.mean()),
        "Std_Dev": float(sals.std()),
        "Q1": float(sals.quantile(0.25)),
        "Q3": float(sals.quantile(0.75)),
        "IQR": float(sals.quantile(0.75) - sals.quantile(0.25))
    })

loc_summary_df = pd.DataFrame(loc_records).sort_values(by="Median_Salary", ascending=False)
loc_summary_df.to_csv(os.path.join(table_dir, "location_salary_summary.csv"), index=False)
print("  Location salary summary saved: location_salary_summary.csv")

# Remote analysis
remote_counts = df_model['is_remote'].value_counts()
sal_remote = df_model.loc[df_model['is_remote'] == True, 'annual_salary_usd']
sal_onsite = df_model.loc[df_model['is_remote'] == False, 'annual_salary_usd']
u_remote, p_remote = stats.mannwhitneyu(sal_remote, sal_onsite, alternative='two-sided')

# FIGURE 09: Salary by Location
sorted_loc = loc_summary_df.sort_values(by="Median_Salary", ascending=True)
fig, ax = plt.subplots(figsize=(12, 8))
y_pos = np.arange(len(sorted_loc))
bars = ax.barh(y_pos, sorted_loc['Median_Salary'], color='#8c564b', alpha=0.85, edgecolor='black')
xerr_low = sorted_loc['Median_Salary'] - sorted_loc['Q1']
xerr_high = sorted_loc['Q3'] - sorted_loc['Median_Salary']
ax.errorbar(sorted_loc['Median_Salary'], y_pos, xerr=[xerr_low, xerr_high], fmt='none', ecolor='#1f77b4', elinewidth=2, capsize=4)
ax.set_yticks(y_pos)
ax.set_yticklabels(sorted_loc['City'])
ax.xaxis.set_major_formatter('${x:,.0f}')
ax.axvline(cohort_median, color='#d62728', linestyle='--', linewidth=1.5, label=f'Cohort Median: ${cohort_median:,.0f}')
ax.set_title("Median Annual Compensation across Top US Tech Hubs (Error Bars = [Q1, Q3])", pad=15, fontweight='bold')
ax.set_xlabel("Median Annual Salary (USD)")
ax.legend(loc='lower right', frameon=True, facecolor='white')

for i, (med, n_cnt) in enumerate(zip(sorted_loc['Median_Salary'], sorted_loc['N'])):
    ax.text(med + 2500, i, f"${med/1000:.0f}k (N={n_cnt:,})", va='center', fontsize=9)

ax.set_xlim(0, 260000)
plt.tight_layout()
fig_09_path = os.path.join(fig_dir, "09_salary_by_location.png")
plt.savefig(fig_09_path)
plt.close()
print(f"  Figure saved: {fig_09_path}")

# -----------------------------------------------------------------------------
# STEP 11: MISSINGNESS DIAGNOSTICS
# -----------------------------------------------------------------------------
print("\n[Step 11] Running Missingness Diagnostics...")

cols_to_check = [
    'job_id', 'title', 'company_name', 'department', 'location_raw',
    'country', 'city', 'is_remote', 'employment_type', 'posted_at',
    'salary_min', 'salary_max', 'salary_currency', 'salary_period', 'skills'
]

miss_records = []
for c in cols_to_check:
    c_corpus_miss = int(df_corpus[c].isnull().sum()) if c in df_corpus.columns else 0
    c_model_miss = int(df_model[c].isnull().sum()) if c in df_model.columns else 0
    miss_records.append({
        "Variable": c,
        "Corpus_Missing_Count": c_corpus_miss,
        "Corpus_Missing_Rate": c_corpus_miss / n_corpus,
        "Modeling_Missing_Count": c_model_miss,
        "Modeling_Missing_Rate": c_model_miss / n_model
    })

miss_df = pd.DataFrame(miss_records)
miss_df.to_csv(os.path.join(table_dir, "missingness_summary.csv"), index=False)
print("  Missingness summary saved: missingness_summary.csv")

# FIGURE 10: Missingness Comparison Chart
fig, ax = plt.subplots(figsize=(11, 6))
x_pos = np.arange(len(miss_df))
width = 0.35
ax.bar(x_pos - width/2, miss_df['Corpus_Missing_Rate'] * 100, width, label='Deduplicated Corpus (N=335,995)', color='#7f7f7f', alpha=0.75, edgecolor='black')
ax.bar(x_pos + width/2, miss_df['Modeling_Missing_Rate'] * 100, width, label='Modeling Cohort (N=34,036)', color='#1f77b4', alpha=0.85, edgecolor='black')
ax.set_xticks(x_pos)
ax.set_xticklabels(miss_df['Variable'], rotation=45, ha='right', fontsize=9.5)
ax.set_ylabel("Missingness Rate (%)")
ax.set_title("Missing Data Audit: Deduplicated Corpus vs. Supervised Modeling Cohort", pad=15, fontweight='bold')
ax.legend(frameon=True, facecolor='white')
plt.tight_layout()
fig_10_path = os.path.join(fig_dir, "10_missingness.png")
plt.savefig(fig_10_path)
plt.close()
print(f"  Figure saved: {fig_10_path}")

# -----------------------------------------------------------------------------
# STEP 12: SAVE COMPLETE METRICS JSON FOR REPORTS
# -----------------------------------------------------------------------------
print("\n[Step 12] Aggregating Comprehensive Metrics JSON...")

metrics_out = {
    "population": {
        "raw_ingested": n_raw,
        "deduplicated_corpus": n_dedup,
        "tech_roles_corpus": n_tech_corpus,
        "salary_disclosed_tech": n_disclosed_tech,
        "final_modeling_cohort": n_model,
        "retention_rate_pct": (n_model / n_raw) * 100.0,
        "tech_salary_disclosure_rate_pct": (n_disclosed_tech / n_tech_corpus) * 100.0,
        "outlier_trim_below_30k": n_below_30k,
        "outlier_trim_above_600k": n_above_600k
    },
    "salary_stats": {
        "mean": float(sal.mean()),
        "std": float(sal.std()),
        "median": float(sal.median()),
        "q1": float(sal.quantile(0.25)),
        "q3": float(sal.quantile(0.75)),
        "iqr": float(sal.quantile(0.75) - sal.quantile(0.25)),
        "min": float(sal.min()),
        "max": float(sal.max()),
        "raw_skewness": float(sal.skew()),
        "raw_kurtosis": float(sal.kurtosis()),
        "log_skewness": float(df_model['log_salary'].skew()),
        "log_kurtosis": float(df_model['log_salary'].kurtosis()),
        "log1p_skewness": float(log_sal.skew()),
        "log1p_kurtosis": float(log_sal.kurtosis())
    },
    "seniority_stats": {
        "kruskal_wallis_h": float(h_stat_sen),
        "kruskal_wallis_p": float(p_val_sen),
        "kruskal_wallis_eps2": float(eps2_sen),
        "distributions": salary_by_sen_df.to_dict(orient='records')
    },
    "role_family_stats": {
        "kruskal_wallis_h": float(h_stat_rf),
        "kruskal_wallis_p": float(p_val_rf),
        "kruskal_wallis_eps2": float(eps2_rf),
        "distributions": salary_by_rf_df.to_dict(orient='records')
    },
    "top_skills_by_freq": skill_freq_df.head(10).to_dict(orient='records'),
    "top_skills_by_premium": skill_assoc_df.head(10).to_dict(orient='records'),
    "top_skill_pairs": skill_pair_df.head(10).to_dict(orient='records'),
    "location_stats": {
        "top_cities": loc_summary_df.head(10).to_dict(orient='records'),
        "remote_count": int(remote_counts.get(True, 0)),
        "onsite_count": int(remote_counts.get(False, 0)),
        "remote_median_sal": float(sal_remote.median()) if len(sal_remote) > 0 else 0.0,
        "onsite_median_sal": float(sal_onsite.median()) if len(sal_onsite) > 0 else 0.0,
        "remote_mann_whitney_u": float(u_remote),
        "remote_mann_whitney_p": float(p_remote)
    }
}

metrics_json_path = os.path.join(table_dir, "eda_metrics.json")
with open(metrics_json_path, "w", encoding="utf-8") as f:
    json.dump(metrics_out, f, indent=2)
print(f"  Metrics JSON saved: {metrics_json_path}")

print("\n" + "=" * 75)
print("PHASE 3 STATISTICAL COMPUTATIONS COMPLETE — READY FOR NOTEBOOK & REPORTS")
print("=" * 75)
