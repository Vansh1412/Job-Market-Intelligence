import pickle, json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import linear_sum_assignment
from sklearn.model_selection import GroupShuffleSplit
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

df = pd.read_parquet('data/processed/india/india_modeling_cohort.parquet')
skill_cols = [c for c in df.columns if c.startswith('skill_')]
mask = df[skill_cols].sum(axis=1) >= 1
df_skills = df[mask].copy()

# 1. Full cohort PCA + KMeans
pca_full = PCA(n_components=15, random_state=42)
X_full_pca = pca_full.fit_transform(df_skills[skill_cols].values)
km_full = KMeans(n_clusters=6, random_state=42, n_init=10).fit(X_full_pca)
full_labels = km_full.labels_

full_medians = [df_skills.loc[full_labels == c, 'salary_midpoint_inr'].median() / 100000.0 for c in range(6)]
rank_order = np.argsort(full_medians)[::-1] # highest median first

arc_meta = {}
for rank, c_idx in enumerate(rank_order):
    arc_id = f'IND_ARC_0{rank+1}'
    arc_meta[c_idx] = {
        'arc_id': arc_id,
        'cluster_idx': c_idx,
        'rank': rank + 1,
        'median_sal': full_medians[c_idx]
    }
print('Full cohort archetypes ranked by median salary:')
for c_idx, m in sorted(arc_meta.items(), key=lambda x: x[1]['rank']):
    print(f"{m['arc_id']}: Cluster {c_idx}, Median Salary = {m['median_sal']:.2f} LPA")

# 2. Train / Holdout Leakage-Safe
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, holdout_idx = next(gss.split(df, groups=df['content_fingerprint']))

df_train = df.iloc[train_idx].copy().reset_index(drop=True)
df_holdout = df.iloc[holdout_idx].copy().reset_index(drop=True)

tr_mask = df_train[skill_cols].sum(axis=1) >= 1
ho_mask = df_holdout[skill_cols].sum(axis=1) >= 1

df_tr_skills = df_train[tr_mask].copy()
df_ho_skills = df_holdout[ho_mask].copy()

pca_tr = PCA(n_components=15, random_state=42).fit(df_tr_skills[skill_cols].values)
X_tr_pca = pca_tr.transform(df_tr_skills[skill_cols].values)
km_tr = KMeans(n_clusters=6, random_state=42, n_init=10).fit(X_tr_pca)
tr_labels = km_tr.labels_

# Hungarian matching
train_job_ids = set(df_tr_skills['job_id'])
full_train_mask = df_skills['job_id'].isin(train_job_ids)
labels_full_on_train = full_labels[full_train_mask]

contingency = np.zeros((6, 6), dtype=int)
for f_l, t_l in zip(labels_full_on_train, tr_labels):
    contingency[f_l, t_l] += 1

row_ind, col_ind = linear_sum_assignment(-contingency)
train_to_full_map = {col: row for row, col in zip(row_ind, col_ind)}
print('\nTrain to Full Cluster Mapping via Hungarian:', train_to_full_map)

# Holdout transformation
X_ho_pca = pca_tr.transform(df_ho_skills[skill_cols].values)
ho_tr_clusters = km_tr.predict(X_ho_pca)
ho_full_clusters = np.array([train_to_full_map[c] for c in ho_tr_clusters])
ho_arc_ids = np.array([arc_meta[c]['arc_id'] for c in ho_full_clusters])

# Frozen model predictions
with open('models/india/final_preprocessor.pkl', 'rb') as f: prep = pickle.load(f)
with open('models/india/final_model.pkl', 'rb') as f: model = pickle.load(f)
with open('models/india/final_feature_list.json', 'r') as f: raw_feats = json.load(f)['feature_names_raw']

X_ho_proc = prep.transform(df_ho_skills[raw_feats])
y_ho = df_ho_skills['salary_midpoint_inr'].values / 100000.0
pred_ho = np.expm1(model.predict(X_ho_proc)) / 100000.0
abs_err_ho = np.abs(y_ho - pred_ho)
res_ho = y_ho - pred_ho

print('\n=== LEAKAGE-SAFE HOLDOUT ERROR BY ARCHETYPE ===')
for rank in range(1, 7):
    arc_id = f'IND_ARC_0{rank}'
    mask_arc = (ho_arc_ids == arc_id)
    n_a = mask_arc.sum()
    y_a = y_ho[mask_arc]
    err_a = res_ho[mask_arc]
    abs_a = abs_err_ho[mask_arc]
    
    mae_a = np.mean(abs_a)
    rmse_a = np.sqrt(np.mean(err_a**2))
    med_ae_a = np.median(abs_a)
    mean_res_a = np.mean(err_a)
    med_sal_a = np.median(y_a)
    rel_mae_a = (mae_a / med_sal_a) * 100.0 if med_sal_a > 0 else 0
    
    print(f"{arc_id}: N={n_a:3d} ({n_a/len(df_ho_skills)*100:4.1f}%), MedSal={med_sal_a:5.2f} LPA | MAE={mae_a:5.2f} LPA, RMSE={rmse_a:5.2f} LPA, MedAE={med_ae_a:5.2f} LPA, MeanRes={mean_res_a:+5.2f} LPA, RelMAE={rel_mae_a:4.1f}%")

# Kruskal-Wallis test across archetypes on holdout
groups_arc = [abs_err_ho[ho_arc_ids == f'IND_ARC_0{r}'] for r in range(1, 7)]
h_kw, p_kw = stats.kruskal(*groups_arc)
N_ho = len(abs_err_ho)
eps2_kw = (h_kw - 6 + 1) / (N_ho - 6)
print(f"\nHoldout Error Kruskal-Wallis: H = {h_kw:.2f}, df = 5, p = {p_kw:.2e}, eps2 = {eps2_kw:.4f}")
