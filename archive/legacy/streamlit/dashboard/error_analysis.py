"""
JobIntel Page 7: Archetype Error Analysis (RQ3)
Statistical testing and disaggregation of salary prediction errors across the seven job archetypes.
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
    ARCHETYPE_COLORS,
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
from src.dashboard.data_loader import load_archetype_errors, load_feature_metadata


def render_error_analysis_page():
    """Renders the archetype error analysis page answering RQ3."""
    render_page_hero(
        icon='🔍',
        title='Archetype Error Diagnostics (RQ3)',
        subtitle='Investigation of model error variance across latent skill archetypes. Answering Research Question 3 via non-parametric statistical hypothesis testing.',
        badge_text='RQ3 · Kruskal-Wallis · p = 7.53×10⁻¹⁷',
    )

    df_errors = load_archetype_errors()
    meta = load_feature_metadata()
    kw_info = meta.get("kruskal_wallis", {})

    kw_stat = kw_info.get("kruskal_wallis_stat", 88.0969)
    kw_pval = kw_info.get("kruskal_wallis_pval", 7.5255e-17)

    # 1. Headline Statistical Test Result
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Kruskal-Wallis H", f"{kw_stat:.2f}", "Chi-Square Test Statistic")
    with c2:
        render_kpi_card("Asymptotic p-value", f"{kw_pval:.2e}", "Significant at α = 0.001", delta="p < 0.001", delta_positive=True)
    with c3:
        render_kpi_card("Lowest Prediction Error", "AI_ML ($27,002)", "Relative Error: 14.42%")
    with c4:
        render_kpi_card("Highest Absolute Error", "CLOUD_ARCH ($46,098)", "Median Midpoint: $220k")

    render_insight_box(
        f"<strong>RQ3 Empirical Answer: YES.</strong> The Kruskal-Wallis test (<em>H</em> = {kw_stat:.2f}, "
        f"<em>p</em> = {kw_pval:.2e}) definitively confirms that <strong>salary-prediction error distributions "
        f"differ significantly across archetypes</strong>. Prediction difficulty is not uniform across technical sectors.",
        bold_prefix="Statistical Conclusion:",
        border_color=COLOR_INDIGO,
    )

    render_hr()

    # 2. Archetype Error Comparison Charts
    render_section_header("Holdout Test Error Disaggregation", "Comparing absolute Mean Absolute Error (MAE) and relative Mean Absolute Percentage Error (MAPE).")

    col_mae_chart, col_mape_chart = st.columns(2)

    with col_mae_chart:
        # Sorted by MAE ascending
        df_mae_sorted = df_errors.sort_values("MAE", ascending=False)
        fig_mae = go.Figure(
            go.Bar(
                y=df_mae_sorted["Archetype_Name"],
                x=df_mae_sorted["MAE"],
                orientation="h",
                marker_color=[
                    COLOR_EMERALD if "AI_ML" in name else (COLOR_CORAL if "CLOUD_ARCH" in name else COLOR_INDIGO)
                    for name in df_mae_sorted["Archetype_Name"]
                ],
                text=[f"${v:,.0f}" for v in df_mae_sorted["MAE"]],
                textposition="outside",
            )
        )
        fig_mae.update_layout(
            title="Mean Absolute Error by Archetype (USD)",
            xaxis_title="Holdout MAE (USD)",
            xaxis_tickformat="$,.0f",
            xaxis_range=[20000, 52000],
            margin=dict(l=150, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_mae, height=380)
        st.plotly_chart(fig_mae, use_container_width=True)

    with col_mape_chart:
        # Check if MAPE column exists or calculate relative error
        if "MAPE" in df_errors.columns:
            mape_col = "MAPE"
        elif "Relative_MAE_%" in df_errors.columns:
            mape_col = "Relative_MAE_%"
        else:
            # Fallback calculate MAE / Median_Salary
            df_errors["MAPE_Calc"] = (df_errors["MAE"] / df_errors["Median_Salary"]) * 100
            mape_col = "MAPE_Calc"

        df_mape_sorted = df_errors.sort_values(mape_col, ascending=False)
        fig_mape = go.Figure(
            go.Bar(
                y=df_mape_sorted["Archetype_Name"],
                x=df_mape_sorted[mape_col],
                orientation="h",
                marker_color=[
                    COLOR_EMERALD if "AI_ML" in name else (COLOR_CORAL if "FOUND_TECH" in name else COLOR_CYAN)
                    for name in df_mape_sorted["Archetype_Name"]
                ],
                text=[f"{v:.1f}%" for v in df_mape_sorted[mape_col]],
                textposition="outside",
            )
        )
        fig_mape.update_layout(
            title="Relative Error (% of Median Midpoint)",
            xaxis_title="Relative Error (%)",
            xaxis_range=[10, 26],
            margin=dict(l=150, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_mape, height=380)
        st.plotly_chart(fig_mape, use_container_width=True)

    render_hr()

    # 3. Granular Error Summary Table
    render_section_header("Detailed Error Metrics Table", "Full metrics suite across the 6,808 holdout test set observations.")

    disp_err = df_errors.copy()
    disp_cols = [c for c in ["Archetype_ID", "Archetype_Name", "N", "Median_Salary", "MAE", "RMSE", mape_col] if c in disp_err.columns]
    disp_err = disp_err[disp_cols]
    disp_err["Median_Salary"] = disp_err["Median_Salary"].apply(lambda x: f"${x:,.0f}")
    disp_err["MAE"] = disp_err["MAE"].apply(lambda x: f"${x:,.0f}")
    if "RMSE" in disp_err.columns:
        disp_err["RMSE"] = disp_err["RMSE"].apply(lambda x: f"${x:,.0f}")
    disp_err[mape_col] = disp_err[mape_col].apply(lambda x: f"{x:.2f}%")
    disp_err = disp_err.rename(columns={mape_col: "Relative_Error_%"})

    st.dataframe(disp_err, use_container_width=True, hide_index=True)

    render_hr()

    # 4. Analytical Explanations (Labeled strictly as Hypotheses)
    render_section_header("Plausible Analytical Explanations", "Analytical hypotheses explaining observed error differentials across archetypes.")

    e1, e2, e3 = st.columns(3)
    with e1:
        render_html(
            """
            <div class="ji-kpi-card" style="border-left: 4px solid #10B981; min-height: 220px;">
                <div class="ji-kpi-label" style="color: #34D399;">Hypothesis 1: AI_ML Accuracy</div>
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">Dense & Discriminating Stacks</div>
                <div class="ji-kpi-sub" style="color: #94A3B8; line-height: 1.5;">
                    <code>AI_ML</code> postings typically feature highly correlated, tightly coupled competencies 
                    (<code>machine_learning</code>, <code>python</code>, <code>pytorch</code>, <code>deep_learning</code>). 
                    This density provides the supervised tree ensemble with strong, unambiguous predictive splits.
                </div>
            </div>
            """
        )
    with e2:
        render_html(
            """
            <div class="ji-kpi-card" style="border-left: 4px solid #F59E0B; min-height: 220px;">
                <div class="ji-kpi-label" style="color: #FBBF24;">Hypothesis 2: CLOUD_ARCH Dispersion</div>
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">Elevated Baseline & Scope</div>
                <div class="ji-kpi-sub" style="color: #94A3B8; line-height: 1.5;">
                    <code>CLOUD_ARCH</code> postings command the highest baseline scale ($220,000 median) with 
                    wide enterprise compensation dispersion (standard deviation: $66.5k). Absolute error naturally scales 
                    with the underlying target midpoint magnitude.
                </div>
            </div>
            """
        )
    with e3:
        render_html(
            """
            <div class="ji-kpi-card" style="border-left: 4px solid #EF4444; min-height: 220px;">
                <div class="ji-kpi-label" style="color: #F87171;">Hypothesis 3: FOUND_TECH Sparsity</div>
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">Residual Role Heterogeneity</div>
                <div class="ji-kpi-sub" style="color: #94A3B8; line-height: 1.5;">
                    <code>FOUND_TECH</code> suffers the highest relative error (22.16%) because 85.31% of postings 
                    possess ≤2 skills. The sparse feature vectors provide minimal tree splitting information, forcing 
                    the regressor to rely primarily on coarse structural priors.
                </div>
            </div>
            """
        )

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer(
        "<strong>Inferential Boundary Notice:</strong> The Kruskal-Wallis test rejects the null hypothesis of equal median "
        "errors across archetypes (p < 0.001). The qualitative mechanisms above represent observational hypotheses and "
        "must not be interpreted as proven causal mechanisms."
    )
    render_source_footer("reports/tables/phase5/phase5_archetype_errors.csv", "Phase 5 Error Analysis")
