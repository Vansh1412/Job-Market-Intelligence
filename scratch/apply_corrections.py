"""
Apply scientific language and numerical corrections to reports/india_phase4_modeling.md
"""

with open('reports/india_phase4_modeling.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Feature contributions wording
old_1 = 'Professional experience (`experience_midpoint_years`) is the dominant foundational predictor, explaining 46.7% of salary variance alone. Standardized roles add ~3.2% variance reduction, geographic tech metros add ~4.8%, and the 284 specific technical skills provide an essential incremental boost, lowering CV MAE from 4.08 LPA to 3.85 LPA.'
new_1 = 'Professional experience (`experience_midpoint_years`) provides the strongest single predictive signal, achieving a cross-validated $R^2$ of ~0.467 in isolation. Adding standardized roles reduces cross-validated MAE by ~0.32 LPA, adding geographic tech metros reduces MAE by an additional ~0.24 LPA, and adding the 284 specific technical skills yields an incremental error reduction, lowering CV MAE from 4.08 LPA to 3.85 LPA.'
assert old_1 in text, 'old_1 not found'
text = text.replace(old_1, new_1)

# 2. Set 1 table description
old_2 = '| **Set 1: Experience Only** | `experience_midpoint`, `experience_range` | 2 | Isolated effect of professional tenure. |'
new_2 = '| **Set 1: Experience Only** | `experience_midpoint`, `experience_range` | 2 | Predictive capacity of experience features in isolation. |'
assert old_2 in text, 'old_2 not found'
text = text.replace(old_2, new_2)

# 3. Log target superior wording
old_3 = "For JobIntel's product goal of realistic salary estimates for typical applicants, **log-target models are empirically superior**."
new_3 = "For JobIntel's product goal of realistic salary estimates for typical applicants, **log1p target transformation produced lower holdout MAE across the evaluated model configurations**."
assert old_3 in text, 'old_3 not found'
text = text.replace(old_3, new_3)

# 4. Set 1 exp variance wording
old_4 = '| **Set 1: Exp Only** | 2 | 4.97 LPA | 4.88 LPA | 4.82 LPA | 0.4666 | Experience alone explains 46.7% variance. |'
new_4 = '| **Set 1: Exp Only** | 2 | 4.97 LPA | 4.88 LPA | 4.82 LPA | 0.4666 | Experience features in isolation achieve a cross-validated R² of 0.467. |'
assert old_4 in text, 'old_4 not found'
text = text.replace(old_4, new_4)

# 5. Runner-up wording
old_5 = """### Transparent Runner-Up Analysis:
- `XGBoost_tuned` (Log) finished a fraction behind with Holdout MAE of 3.76 LPA (+0.05 LPA difference) and achieved the lowest train-to-holdout gap (0.40 LPA).
- On raw target, `XGBoost_tuned` (Raw) achieved the highest overall $R^2$ (0.5945) and lowest RMSE (6.11 LPA).
- Both tree-boosting models exhibit exceptional alignment. `HistGradientBoostingRegressor` was selected under the primary lowest-MAE policy."""

new_5 = """### Transparent Runner-Up Analysis & Selection Context:
- HistGradientBoosting achieved the lowest observed holdout MAE (3.71 LPA) among the evaluated configurations, while tuned XGBoost produced highly competitive performance (3.76 LPA), an absolute difference of only ₹0.05 LPA.
- On the raw target formulation, `XGBoost_tuned` (Raw) achieved the lowest overall RMSE (6.11 LPA) and highest $R^2$ (0.5945).
- Model selection was governed strictly by the pre-declared primary selection criterion (lowest holdout MAE). Under this rule, `HistGradientBoostingRegressor` with log1p transformation was selected."""
assert old_5 in text, 'old_5 not found'
text = text.replace(old_5, new_5)

# 6. Experience table numbers
old_6 = """| Seniority Tier | Experience Range | Holdout N | Pct (%) | MAE (LPA) | RMSE (LPA) | Median AE (LPA) | Bias (LPA) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Entry Level** | 0–2 years | 148 | 12.62% | **1.62 LPA** | 2.82 LPA | 0.81 LPA | -0.32 LPA |
| **Mid-Level** | 3–5 years | 569 | 48.51% | **2.74 LPA** | 4.31 LPA | 1.95 LPA | +0.07 LPA |
| **Senior** | 6–10 years | 360 | 30.69% | **4.87 LPA** | 7.62 LPA | 3.32 LPA | +1.87 LPA |
| **Lead / Staff** | 11–15 years | 84 | 7.16% | **8.12 LPA** | 10.98 LPA | 6.89 LPA | +3.82 LPA |
| **Principal / Exec** | 16+ years | 12 | 1.02% | **18.72 LPA** | 21.64 LPA | 16.42 LPA | +17.15 LPA |

### Insight:
Predictive accuracy is extremely tight for Entry-Level (1.62 LPA) and Mid-Level (2.74 LPA) engineers, which constitute 61.1% of the market. Error scales with seniority as unobserved individual merit and negotiation leverage become prominent factors."""

new_6 = """| Seniority Tier | Experience Range | Holdout N | Pct (%) | MAE (LPA) | RMSE (LPA) | Median AE (LPA) | Bias (LPA) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Entry Level** | 0–2 years | 129 | 11.00% | **0.84 LPA** | 1.60 LPA | 0.49 LPA | +0.19 LPA |
| **Mid-Level** | 3–5 years | 339 | 28.90% | **2.55 LPA** | 4.95 LPA | 1.35 LPA | +0.86 LPA |
| **Senior** | 6–10 years | 570 | 48.59% | **4.50 LPA** | 6.59 LPA | 2.92 LPA | +1.33 LPA |
| **Lead / Staff** | 11–15 years | 114 | 9.72% | **5.99 LPA** | 9.15 LPA | 3.95 LPA | +1.57 LPA |
| **Principal / Exec** | 16+ years | 21 | 1.79% | **6.32 LPA** | 10.80 LPA | 2.28 LPA | +2.15 LPA |

### Insight:
Prediction error is lowest for Entry-Level (0.84 LPA) and Mid-Level (2.55 LPA) postings. Prediction error scales with seniority as unobserved individual tenure, negotiation leverage, and role scope become increasingly differentiated."""
assert old_6 in text, 'old_6 not found'
text = text.replace(old_6, new_6)

# 7. Salary band accuracy wording
old_7 = '| **₹10–20 LPA** | 356 | 30.35% | **3.33 LPA** | 4.38 LPA | 2.58 LPA | **+0.38 LPA** | **Near-zero bias; peak accuracy zone.** |'
new_7 = '| **₹10–20 LPA** | 356 | 30.35% | **3.33 LPA** | 4.38 LPA | 2.58 LPA | **+0.38 LPA** | **Near-zero signed bias (+0.38 LPA); lowest relative distortion.** |'
assert old_7 in text, 'old_7 not found'
text = text.replace(old_7, new_7)

# 8. Upper tail truncation wording
old_8 = '3. **Upper-Tail Truncation:** Unobserved executive pedigree limits tree accuracy above ₹40 LPA.'
new_8 = '3. **Upper-Tail Truncation:** Unobserved executive compensation structures and equity packages lead to systematic underprediction for postings above ₹40 LPA.'
assert old_8 in text, 'old_8 not found'
text = text.replace(old_8, new_8)

# 9. RQ3 wording
old_9 = r'- **Experience Invariance:** Entry- and Mid-level positions have minimal error ($\text{MAE} \le 2.74\text{ LPA}$), while senior leadership positions ($\ge 11$ years) display wider error bars due to bilateral negotiation leverage.'
new_9 = r'- **Experience Invariance:** Entry- and Mid-level positions have lower prediction error ($\text{MAE} \le 2.55\text{ LPA}$), while senior leadership positions ($\ge 11$ years) display wider error margins due to bilateral negotiation latitude.'
assert old_9 in text, 'old_9 not found'
text = text.replace(old_9, new_9)

# 10. Ensemble wording
old_10 = '2. **Ensemble Architecture:** In Phase India-5 / Phase India-6, deploying a weighted blend of `HistGradientBoostingRegressor` (for lowest MAE) and `XGBoostRegressor` (for lower RMSE) will provide optimal predictions.'
new_10 = '2. **Ensemble Architecture:** In Phase India-5 / Phase India-6, deploying a weighted blend of `HistGradientBoostingRegressor` (for lowest MAE) and `XGBoostRegressor` (for lower RMSE) could be evaluated for enhanced generalization across both metrics.'
assert old_10 in text, 'old_10 not found'
text = text.replace(old_10, new_10)

with open('reports/india_phase4_modeling.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully applied all 10 targeted documentation corrections.')
