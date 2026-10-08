"""
Phase 5: Master Experiment Execution Script
===========================================
INT234 Predictive Analytics — Job Market Intelligence:
Skill-Based Job Archetype Discovery and Salary Prediction using Machine Learning

Executes all 18 mandatory stages of Phase 5 in a controlled, reproducible manner:
1. Data loading & audit
2. Train/Test isolation (80/20)
3. 5-Fold Cross-Validation across Feature Sets A, B, and C
4. Controlled hyperparameter tuning
5. Final model freezing & ONE holdout test evaluation
6. Bias/variance, residual, interpretability, and archetype-level error analyses
7. Exports all tables, figures, and model artifacts
"""

import os
import sys
sys.path.insert(0, ".")

import time
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, learning_curve, validation_curve
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from src.phase5.data import load_raw_modeling_data, audit_dataset, get_train_test_split
from src.phase5.evaluation import run_fold_safe_cv, evaluate_baselines_cv, compute_metrics
from src.phase5.feature_sets import FeatureSetBuilder
from src.phase5.models import get_default_models
from src.phase5.error_analysis import analyze_archetype_errors
from src.phase5.interpretability import (
    get_tree_feature_importance,
    compute_test_permutation_importance,
    get_ridge_coefficients,
    triangulate_rq1_skills,
)
from src.phase5.plots import (
    plot_cv_comparisons,
    plot_test_comparisons,
    plot_learning_curve,
    plot_validation_curves,
    plot_residual_diagnostics,
    plot_interpretability,
    plot_archetype_error_diagnostics,
)

RANDOM_STATE = 42
TABLES_DIR = "reports/tables/phase5"
FIGURES_DIR = "reports/figures/phase5"
MODELS_DIR = "models/phase5"

for d in [TABLES_DIR, FIGURES_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)


def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{t}] {msg}", flush=True)


def main():
    log("=" * 70)
    log("STARTING PHASE 5: SALARY PREDICTION & COMPARATIVE MACHINE LEARNING")
    log("=" * 70)

    # -------------------------------------------------------------
    # STAGES 1 & 2: DATA AUDIT & VALIDATION
    # -------------------------------------------------------------
    log("STAGE 1 & 2: Loading dataset and auditing schema integrity...")
    df, tech_skills = load_raw_modeling_data()
    audit_df = audit_dataset(df, tech_skills)

    # -------------------------------------------------------------
    # STAGE 3: TRAIN / TEST SPLIT (80% / 20%)
    # -------------------------------------------------------------
    log("STAGE 3: Partitioning data into Train (80%) and Holdout Test (20%)...")
    split_data = get_train_test_split(df, tech_skills)
    X_train_df = split_data["X_train"]
    X_test_df = split_data["X_test"]
    y_train = split_data["y_train"]
    y_test = split_data["y_test"]
    metadata_cols = split_data["metadata_cols"]

    # -------------------------------------------------------------
    # STAGE 4: LEAKAGE AUDIT VERIFICATION
    # -------------------------------------------------------------
    log("STAGE 4: Verifying leakage safety...")
    assert "salary_midpoint" not in X_train_df.columns, "Target leaked into predictors!"
    assert "log_salary" not in X_train_df.columns, "Log target leaked into predictors!"
    assert "cluster_id" not in X_train_df.columns, "Exploratory cluster labels leaked into predictors!"
    log("Leakage audit passed: 0 target columns or precomputed cluster labels in predictors.")

    # -------------------------------------------------------------
    # STAGE 8 & 9: 5-FOLD CV ON FEATURE SETS A, B, AND C
    # -------------------------------------------------------------
    log("STAGE 8 & 9: Evaluating Naive Baselines and 5-Fold CV across Sets A, B, C...")
    df_base = evaluate_baselines_cv(X_train_df, y_train)

    default_models = get_default_models()

    cv_table_path = os.path.join(TABLES_DIR, "phase5_cv_results.csv")
    comp_table_path = os.path.join(TABLES_DIR, "phase5_model_comparison.csv")

    if os.path.exists(cv_table_path) and os.path.exists(comp_table_path):
        log(f"Loading existing verified CV results from: {cv_table_path}")
        df_all_cv = pd.read_csv(cv_table_path)
        df_comparison = pd.read_csv(comp_table_path)
    else:
        # Feature Set A: Original Features
        df_cv_A = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="A", models=default_models)

        # Feature Set B: PCA Features (15 PCs)
        df_cv_B = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="B", models=default_models)

        # Feature Set C: Original + Archetype Features (k=7)
        df_cv_C = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="C", models=default_models)

        # Combine all CV results
        df_all_cv = pd.concat([df_base, df_cv_A, df_cv_B, df_cv_C], ignore_index=True)
        df_all_cv.to_csv(cv_table_path, index=False)
        log(f"Saved complete CV results: {cv_table_path}")

        # Comparative Summary (Feature Set A vs B vs C)
        df_comparison = df_all_cv[~df_all_cv["Model"].str.contains("Dummy")].copy()
        df_comparison.to_csv(comp_table_path, index=False)
        log(f"Saved model comparison table: {comp_table_path}")

    # Identify best performing model and feature set from CV
    best_cv_row = df_comparison.loc[df_comparison["CV_MAE_Mean"].idxmin()]
    best_model_name = best_cv_row["Model"]
    best_feature_set = str(best_cv_row["Feature_Set"]).replace("Set ", "")
    log(f"Best CV Model: {best_model_name} on Feature Set {best_feature_set} (CV MAE = ${best_cv_row['CV_MAE_Mean']:,.0f}, R² = {best_cv_row['CV_R2_Mean']:.4f})")

    # -------------------------------------------------------------
    # STAGE 10: CONTROLLED HYPERPARAMETER TUNING
    # -------------------------------------------------------------
    log("STAGE 10: Executing controlled hyperparameter tuning on top model (XGBoost)...")
    builder = FeatureSetBuilder(metadata_cols, tech_skills)

    # Build Feature Set A and C matrices for tuning on full training set
    X_tr_A, fn_A, trans_A = builder.build_feature_set_A(X_train_df)
    X_tr_C, fn_C, trans_C = builder.build_feature_set_C(X_train_df)

    tuning_table_path = os.path.join(TABLES_DIR, "phase5_hyperparameter_results.csv")
    if os.path.exists(tuning_table_path):
        log(f"Loading existing hyperparameter tuning results from: {tuning_table_path}")
        df_tuning = pd.read_csv(tuning_table_path)
    else:
        # Compact tuning grid for XGBoost on training set using 5-fold CV
        kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        tuning_records = []
        param_grid = [
            {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 150},
            {"max_depth": 5, "learning_rate": 0.10, "n_estimators": 100},
            {"max_depth": 6, "learning_rate": 0.05, "n_estimators": 150},
            {"max_depth": 6, "learning_rate": 0.10, "n_estimators": 150},
        ]

        for p in param_grid:
            fold_maes = []
            fold_rmses = []
            fold_r2s = []
            for tr_idx, val_idx in kf.split(X_tr_A):
                m = XGBRegressor(
                    max_depth=p["max_depth"],
                    learning_rate=p["learning_rate"],
                    n_estimators=p["n_estimators"],
                    subsample=0.8,
                    colsample_bytree=0.8,
                    tree_method="hist",
                    random_state=RANDOM_STATE,
                    n_jobs=-1
                )
                m.fit(X_tr_A[tr_idx], y_train[tr_idx])
                y_pred_val = m.predict(X_tr_A[val_idx])
                res = compute_metrics(y_train[val_idx], y_pred_val)
                fold_maes.append(res["MAE"])
                fold_rmses.append(res["RMSE"])
                fold_r2s.append(res["R2"])

            tuning_records.append({
                "Model": "XGBoost",
                "max_depth": p["max_depth"],
                "learning_rate": p["learning_rate"],
                "n_estimators": p["n_estimators"],
                "CV_MAE_Mean": float(np.mean(fold_maes)),
                "CV_MAE_Std": float(np.std(fold_maes)),
                "CV_RMSE_Mean": float(np.mean(fold_rmses)),
                "CV_R2_Mean": float(np.mean(fold_r2s)),
            })
            log(f"  Tuned XGBoost (depth={p['max_depth']}, lr={p['learning_rate']}, n_est={p['n_estimators']}) -> CV MAE = ${np.mean(fold_maes):,.0f} | R² = {np.mean(fold_r2s):.4f}")

        df_tuning = pd.DataFrame(tuning_records)
        df_tuning.to_csv(tuning_table_path, index=False)
        log(f"Saved hyperparameter tuning results: {tuning_table_path}")

    best_tune_params = df_tuning.loc[df_tuning["CV_MAE_Mean"].idxmin()]
    log(f"Optimal Tuned Hyperparameters: max_depth={int(best_tune_params['max_depth'])}, lr={best_tune_params['learning_rate']}, n_est={int(best_tune_params['n_estimators'])}")

    # -------------------------------------------------------------
    # STAGE 11 & 12: FINAL MODEL FREEZING & ONE HOLDOUT TEST EVALUATION
    # -------------------------------------------------------------
    log("STAGE 11 & 12: Freezing final model and executing ONE final holdout test evaluation...")

    # Build final train and test feature sets strictly from training transformers
    X_tr_final_A, X_te_final_A, feature_names_A, trans_A = builder.build_feature_set_A(X_train_df, X_test_df)
    X_tr_final_C, X_te_final_C, feature_names_C, trans_C = builder.build_feature_set_C(X_train_df, X_test_df)

    # Train final candidate models on full training set (80%)
    final_models = {
        "Dummy (Median)": DummyRegressor(strategy="median"),
        "Ridge": Ridge(alpha=10.0, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=15, min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, min_samples_leaf=5, random_state=RANDOM_STATE),
        "XGBoost (Default)": XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, tree_method="hist", random_state=RANDOM_STATE, n_jobs=-1),
        "XGBoost (Tuned)": XGBRegressor(
            n_estimators=int(best_tune_params["n_estimators"]),
            max_depth=int(best_tune_params["max_depth"]),
            learning_rate=float(best_tune_params["learning_rate"]),
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "XGBoost (Set C Archetype)": XGBRegressor(
            n_estimators=int(best_tune_params["n_estimators"]),
            max_depth=int(best_tune_params["max_depth"]),
            learning_rate=float(best_tune_params["learning_rate"]),
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
    }

    test_records = []
    test_predictions = {}

    for name, m in final_models.items():
        if "Set C" in name:
            X_tr_use = X_tr_final_C
            X_te_use = X_te_final_C
            f_set_name = "Set C"
        else:
            X_tr_use = X_tr_final_A
            X_te_use = X_te_final_A
            f_set_name = "Set A"

        if name == "Ridge":
            s_dense = StandardScaler()
            X_tr_use = s_dense.fit_transform(X_tr_use)
            X_te_use = s_dense.transform(X_te_use)

        m.fit(X_tr_use, y_train)
        y_pred_te = m.predict(X_te_use)
        y_pred_tr = m.predict(X_tr_use)

        test_m = compute_metrics(y_test, y_pred_te)
        train_m = compute_metrics(y_train, y_pred_tr)

        test_predictions[name] = y_pred_te

        test_records.append({
            "Model": name,
            "Feature_Set": f_set_name,
            "Train_MAE": train_m["MAE"],
            "Train_RMSE": train_m["RMSE"],
            "Train_R2": train_m["R2"],
            "Test_MAE": test_m["MAE"],
            "Test_RMSE": test_m["RMSE"],
            "Test_R2": test_m["R2"],
            "Test_MAPE": test_m["MAPE"],
            "Generalization_Gap_MAE": test_m["MAE"] - train_m["MAE"],
            "Generalization_Gap_R2": train_m["R2"] - test_m["R2"],
        })
        log(f"  Holdout Test Evaluation: {name:26s} | Test MAE = ${test_m['MAE']:,.0f} | Test RMSE = ${test_m['RMSE']:,.0f} | Test R² = {test_m['R2']:.4f}")

    df_test_results = pd.DataFrame(test_records)
    test_table_path = os.path.join(TABLES_DIR, "phase5_test_results.csv")
    df_test_results.to_csv(test_table_path, index=False)
    log(f"Saved final test evaluation results: {test_table_path}")

    # Bias / Variance Table
    df_bias_var = df_test_results[["Model", "Feature_Set", "Train_MAE", "Test_MAE", "Generalization_Gap_MAE", "Train_R2", "Test_R2", "Generalization_Gap_R2"]].copy()
    bv_table_path = os.path.join(TABLES_DIR, "phase5_bias_variance.csv")
    df_bias_var.to_csv(bv_table_path, index=False)
    log(f"Saved bias-variance analysis table: {bv_table_path}")

    # Final Winning Model: XGBoost (Tuned) on Feature Set A
    final_winning_model = final_models["XGBoost (Tuned)"]
    y_test_pred_final = test_predictions["XGBoost (Tuned)"]

    # -------------------------------------------------------------
    # STAGE 13: BIAS / VARIANCE & LEARNING CURVES
    # -------------------------------------------------------------
    log("STAGE 13: Generating learning curve and validation curve diagnostics...")
    # Learning curve for best model on training set sample
    train_sizes_sub = np.linspace(0.2, 1.0, 5)
    train_sizes_abs, train_scores, val_scores = learning_curve(
        XGBRegressor(max_depth=5, learning_rate=0.1, n_estimators=100, tree_method="hist", random_state=RANDOM_STATE, n_jobs=-1),
        X_tr_final_A,
        y_train,
        cv=3,
        train_sizes=train_sizes_sub,
        scoring="r2",
        n_jobs=-1
    )
    plot_learning_curve(train_sizes_abs, train_scores, val_scores, model_name="XGBoost Regressor")

    # Validation curves
    param_range_ridge = np.logspace(-1, 3, 5)
    _, ridge_val_scores = validation_curve(
        Ridge(random_state=RANDOM_STATE),
        X_tr_final_A,
        y_train,
        param_name="alpha",
        param_range=param_range_ridge,
        cv=3,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )

    param_range_xgb = [3, 4, 5, 6, 7]
    _, xgb_val_scores = validation_curve(
        XGBRegressor(n_estimators=100, learning_rate=0.1, tree_method="hist", random_state=RANDOM_STATE, n_jobs=-1),
        X_tr_final_A,
        y_train,
        param_name="max_depth",
        param_range=param_range_xgb,
        cv=3,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )
    plot_validation_curves(param_range_ridge, ridge_val_scores, param_range_xgb, xgb_val_scores)

    # -------------------------------------------------------------
    # STAGE 14: RESIDUAL & INTERPRETABILITY ANALYSIS (RQ1)
    # -------------------------------------------------------------
    log("STAGE 14: Executing interpretability analysis and skill triangulation (RQ1)...")
    plot_residual_diagnostics(y_test, y_test_pred_final, model_name="XGBoost (Tuned)")

    # Tree feature importances
    df_tree_imp = get_tree_feature_importance(final_winning_model, feature_names_A)
    tree_imp_path = os.path.join(TABLES_DIR, "phase5_feature_importance.csv")
    df_tree_imp.to_csv(tree_imp_path, index=False)
    log(f"Saved feature importance table: {tree_imp_path}")

    # Permutation importance on test set
    df_perm_imp = compute_test_permutation_importance(final_winning_model, X_te_final_A, y_test, feature_names_A, n_repeats=5, random_state=RANDOM_STATE)
    perm_imp_path = os.path.join(TABLES_DIR, "phase5_permutation_importance.csv")
    df_perm_imp.to_csv(perm_imp_path, index=False)
    log(f"Saved permutation importance table: {perm_imp_path}")

    # Standardized Ridge coefficients
    ridge_fitted = final_models["Ridge"]
    df_ridge_coefs = get_ridge_coefficients(ridge_fitted, feature_names_A)

    # Triangulate RQ1 Skills
    df_rq1 = triangulate_rq1_skills(df_tree_imp, df_perm_imp, df_ridge_coefs, tech_skills)
    rq1_path = os.path.join(TABLES_DIR, "phase5_rq1_skill_associations.csv")
    df_rq1.to_csv(rq1_path, index=False)
    log(f"Saved RQ1 triangulated skill associations: {rq1_path}")

    plot_interpretability(df_tree_imp, df_perm_imp, df_ridge_coefs)

    # -------------------------------------------------------------
    # STAGE 15: ARCHETYPE-LEVEL ERROR ANALYSIS (RQ3)
    # -------------------------------------------------------------
    log("STAGE 15: Executing archetype-level error analysis and Kruskal-Wallis test (RQ3)...")
    # Assign holdout test instances to archetypes using the training K-Means centroids (Zero Leakage!)
    meta_tr, pca_tr, km_tr = trans_C
    X_skills_test = X_test_df[tech_skills].values.astype(np.float32)
    X_pca_test = pca_tr.transform(X_skills_test)
    test_archetype_labels = km_tr.predict_cluster_labels(X_pca_test)

    df_arch_errors, kw_summary = analyze_archetype_errors(y_test, y_test_pred_final, test_archetype_labels)
    arch_error_path = os.path.join(TABLES_DIR, "phase5_archetype_errors.csv")
    df_arch_errors.to_csv(arch_error_path, index=False)
    log(f"Saved archetype error analysis table: {arch_error_path}")
    log(f"Kruskal-Wallis Test: Stat = {kw_summary['kruskal_wallis_stat']:.4f}, p-val = {kw_summary['kruskal_wallis_pval']:.4e} (Significant: {kw_summary['is_significant_005']})")

    plot_archetype_error_diagnostics(df_arch_errors, y_test, y_test_pred_final, test_archetype_labels)

    # -------------------------------------------------------------
    # STAGE 16: PUBLICATION FIGURES
    # -------------------------------------------------------------
    log("STAGE 16: Generating all CV and holdout test publication figures...")
    plot_cv_comparisons(df_all_cv)
    plot_test_comparisons(df_test_results)

    # -------------------------------------------------------------
    # STAGE 17: MODEL ARTIFACT SERIALIZATION
    # -------------------------------------------------------------
    log("STAGE 17: Serializing model artifacts in models/phase5/...")
    joblib.dump(final_winning_model, os.path.join(MODELS_DIR, "best_model.pkl"))
    joblib.dump(trans_A, os.path.join(MODELS_DIR, "best_pipeline.pkl"))

    # Save feature metadata
    metadata_json = {
        "model_name": "XGBoost (Tuned)",
        "feature_set": "Feature Set A",
        "n_training_samples": len(X_train_df),
        "n_test_samples": len(X_test_df),
        "n_features": len(feature_names_A),
        "feature_names": feature_names_A,
        "metadata_cols": metadata_cols,
        "tech_skills": tech_skills,
        "test_metrics": compute_metrics(y_test, y_test_pred_final),
        "kruskal_wallis": kw_summary,
    }
    with open(os.path.join(MODELS_DIR, "feature_metadata.json"), "w") as f:
        json.dump(metadata_json, f, indent=2)

    with open(os.path.join(MODELS_DIR, "model_metrics.json"), "w") as f:
        json.dump(test_records, f, indent=2)

    log("=" * 70)
    log("PHASE 5 MASTER EXPERIMENTS COMPLETE & VERIFIED")
    log("=" * 70)


if __name__ == "__main__":
    main()
