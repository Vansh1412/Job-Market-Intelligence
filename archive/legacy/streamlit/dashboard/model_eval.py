"""
JobIntel Page 6: Model Performance & Evaluation
Supervised regression benchmarks, baseline comparisons, feature set analyses, and feature importances.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.dashboard.theme import (
    COLOR_INDIGO,
    COLOR_CYAN,
    COLOR_EMERALD,
    COLOR_AMBER,
    COLOR_CORAL,
    apply_plotly_theme,
)
from src.dashboard.ui_components import (
    render_page_hero,
    render_kpi_card,
    render_insight_box,
    render_scientific_disclaimer,
    render_source_footer,
    render_section_header,
    render_hr,
    render_html,
)
from src.dashboard.data_loader import (
    load_test_results,
    load_model_comparison,
    load_feature_importance,
    load_permutation_importance,
    load_bias_variance,
)


def render_model_eval_page():
    """Renders the machine learning model performance evaluation page."""
    render_page_hero(
        icon='📊',
        title='Model Performance & Evaluation',
        subtitle='Rigorous benchmark evaluation of 5 supervised regression algorithms, 3 feature set architectures, and holdout generalization diagnostics (80/20 train/test split).',
        badge_text='Phase 5 · XGBoost Champion · Frozen Results',
    )

    df_test = load_test_results()
    df_feat_imp = load_feature_importance()
    df_perm_imp = load_permutation_importance()
    df_bias_var = load_bias_variance()

    # 1. Headline Benchmark Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Winning Model", "XGBoost (Tuned)", "Feature Set A (123 predictors)")
    with c2:
        render_kpi_card("Holdout Test MAE", "$36,381", "Dummy Baseline: $50,806", delta="-28.4%", delta_positive=True)
    with c3:
        render_kpi_card("Holdout Test RMSE", "$51,082", "Dummy Baseline: $67,660", delta="-24.5%", delta_positive=True)
    with c4:
        render_kpi_card("Holdout Test R²", "0.4233", "CV Mean R²: 0.4192 (±0.007)")

    render_hr()

    # 2. Model Leaderboard Table & Chart
    render_section_header("Algorithm Leaderboard on Holdout Test Set", "Evaluation across naive baseline, linear, tree ensemble, and gradient boosted models.")

    col_board_chart, col_board_table = st.columns([1.3, 1.0])

    with col_board_chart:
        # Sorted by Test MAE ascending
        df_plot = df_test.sort_values("Test_MAE", ascending=False)
        fig_board = go.Figure(
            go.Bar(
                y=df_plot["Model"],
                x=df_plot["Test_MAE"],
                orientation="h",
                marker_color=[COLOR_CORAL if "Dummy" in m else (COLOR_EMERALD if "Tuned" in m else COLOR_INDIGO) for m in df_plot["Model"]],
                text=[f"${v:,.0f}" for v in df_plot["Test_MAE"]],
                textposition="outside",
            )
        )
        fig_board.update_layout(
            title="Model Test MAE Comparison (Lower is Better)",
            xaxis_title="Holdout Test MAE (USD)",
            xaxis_tickformat="$,.0f",
            xaxis_range=[30000, 55000],
            margin=dict(l=150, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_board, height=360)
        st.plotly_chart(fig_board, use_container_width=True)

    with col_board_table:
        st.markdown("##### Detailed Metric Summary")
        disp_test = df_test[["Model", "Feature_Set", "Test_MAE", "Test_RMSE", "Test_R2"]].copy()
        disp_test["Test_MAE"] = disp_test["Test_MAE"].apply(lambda x: f"${x:,.0f}")
        disp_test["Test_RMSE"] = disp_test["Test_RMSE"].apply(lambda x: f"${x:,.0f}")
        disp_test["Test_R2"] = disp_test["Test_R2"].apply(lambda x: f"{x:.4f}")
        st.dataframe(disp_test, use_container_width=True, hide_index=True)

    # 3. Feature Set Comparison (A vs B vs C)
    render_section_header("Feature Set Architecture Comparison", "Testing whether latent archetype indicators add predictive signal beyond explicit metadata.")

    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        render_html(
            """
            <div class="ji-kpi-card" style="border-top: 2px solid #818CF8;">
                <div class="ji-kpi-accent-bar" style="background: #818CF8;"></div>
                <div class="ji-kpi-label">Feature Set A (Explicit)</div>
                <div class="ji-kpi-value" style="font-size: 1.5rem; color: #818CF8;">$36,381 MAE</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">R² = 0.4233 · 123 Features</div>
                <div class="ji-kpi-sub" style="margin-top: 8px;">
                    Metadata (Seniority, Role, City, Remote) + 82 explicit binary technical skills.
                </div>
            </div>
            """
        )
    with c_f2:
        render_html(
            """
            <div class="ji-kpi-card" style="border-top: 2px solid #22D3EE;">
                <div class="ji-kpi-accent-bar" style="background: #22D3EE;"></div>
                <div class="ji-kpi-label">Feature Set B (PCA Compressed)</div>
                <div class="ji-kpi-value" style="font-size: 1.5rem; color: #22D3EE;">$37,842 MAE</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">R² = 0.3814 · 56 Features</div>
                <div class="ji-kpi-sub" style="margin-top: 8px;">
                    Metadata + 15 continuous Principal Components. Compression loses 43.95% variance.
                </div>
            </div>
            """
        )
    with c_f3:
        render_html(
            """
            <div class="ji-kpi-card" style="border-top: 2px solid #34D399;">
                <div class="ji-kpi-accent-bar" style="background: #34D399;"></div>
                <div class="ji-kpi-label">Feature Set C (Archetype Augmented)</div>
                <div class="ji-kpi-value" style="font-size: 1.5rem; color: #34D399;">$36,425 MAE</div>
                <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">R² = 0.4255 · 130 Features</div>
                <div class="ji-kpi-sub" style="margin-top: 8px;">
                    Feature Set A + 7 one-hot archetype indicators. Delta vs Set A: +$44.20 MAE (+0.12%).
                </div>
            </div>
            """
        )

    render_insight_box(
        "Adding the seven archetype indicator features (Feature Set C) produced <strong>no practically meaningful "
        "predictive improvement</strong> over Feature Set A (+$44.20 MAE delta). "
        "This confirms that <strong>explicit skills and structural metadata preserve the principal predictive signal "
        "captured by the supervised models</strong>, leaving little incremental signal for exploratory clustering labels.",
        bold_prefix="Feature Set Finding:",
        border_color=COLOR_INDIGO,
    )

    render_hr()

    # 4. Feature Importance & Permutation Analysis
    render_section_header("Predictive Drivers & Permutation Importance", "Gini tree importance vs holdout test permutation feature impact.")

    col_gini, col_perm = st.columns(2)

    with col_gini:
        top_gini = df_feat_imp.sort_values("Importance", ascending=False).head(12)
        fig_gini = go.Figure(
            go.Bar(
                y=[f.replace("skill_", "").replace("role_family_", "Role: ").replace("seniority_", "Sen: ").replace("city_clean_", "City: ").title() for f in top_gini["Feature"]],
                x=top_gini["Importance"],
                orientation="h",
                marker_color=COLOR_INDIGO,
                text=[f"{v:.3f}" for v in top_gini["Importance"]],
                textposition="outside",
            )
        )
        fig_gini.update_layout(
            title="Top 12 Features by XGBoost Split Importance",
            xaxis_title="Relative Importance",
            yaxis_autorange="reversed",
            margin=dict(l=140, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_gini, height=400)
        st.plotly_chart(fig_gini, use_container_width=True)

    with col_perm:
        top_perm = df_perm_imp.sort_values("Permutation_Importance_Mean", ascending=False).head(12)
        fig_perm = go.Figure(
            go.Bar(
                y=[f.replace("skill_", "").replace("role_family_", "Role: ").replace("seniority_", "Sen: ").replace("city_clean_", "City: ").title() for f in top_perm["Feature"]],
                x=top_perm["Permutation_Importance_Mean"],
                orientation="h",
                marker_color=COLOR_CYAN,
                text=[f"${v:,.0f}" for v in top_perm["Permutation_Importance_Mean"]],
                textposition="outside",
            )
        )
        fig_perm.update_layout(
            title="Top 12 Features by Permutation Impact (Test MAE Increase)",
            xaxis_title="Holdout Test MAE Increase if Shuffled (USD)",
            xaxis_tickformat="$,.0f",
            yaxis_autorange="reversed",
            margin=dict(l=140, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_perm, height=400)
        st.plotly_chart(fig_perm, use_container_width=True)

    # Generalization & Bias-Variance Summary
    render_insight_box(
        "Generalization gap analysis indicates <strong>Train MAE = $33,525 vs Test MAE = $36,381 (Gap: $2,855)</strong>. "
        "The train-test spread is moderate and does not indicate catastrophic overfitting. "
        "Predictive accuracy remains limited by intrinsic labor market compensation variance rather than model underfitting.",
        bold_prefix="Bias-Variance Diagnosis:",
        border_color=COLOR_EMERALD,
    )

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer()
    render_source_footer("reports/tables/phase5/phase5_test_results.csv", "Phase 5 Supervised Modeling")
