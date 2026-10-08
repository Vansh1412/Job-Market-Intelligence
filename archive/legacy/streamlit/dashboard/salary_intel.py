"""
JobIntel Page 2: Salary Intelligence
Interactive exploration of labor market salary distributions by seniority, role family, and location.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
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
    load_salary_summary,
    load_salary_by_role,
    load_salary_by_seniority,
    load_salary_by_location,
)


def render_salary_intel_page():
    """Renders the salary intelligence exploration page."""
    render_page_hero(
        icon="💰",
        title="Salary Intelligence",
        subtitle=(
            "Empirical analysis of compensation distributions, seniority gradients, "
            "and geographical salary differentials across 34,036 technology postings with verified USD midpoints."
        ),
        badge_text="Phase 3 EDA · Frozen Results",
    )

    # 1. Headline Salary Moments
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Cohort Median", "$180,413", "50th Percentile Midpoint")
    with c2:
        render_kpi_card("Cohort Mean", "$187,031", "Std Dev: $65,753")
    with c3:
        render_kpi_card("Interquartile Range", "$85,000", "Q1: $140k | Q3: $225k")
    with c4:
        render_kpi_card("Salary Skewness", "+0.9436", "Moderate Right-Tail Dispersion")

    render_insight_box(
        "The salary target is right-skewed (+0.9436) with heavy concentration between $130,000 and $230,000. "
        "Domain bounds [$30,000, $600,000] were applied in Phase 2 to eliminate extreme scraping artifacts without synthetic trimming.",
        bold_prefix="Distributional Profile:",
        border_color=COLOR_INDIGO,
    )

    render_hr()

    # 2. Seniority Progression Gradient
    render_section_header("Seniority Compensation Gradient", "Observed salary scaling across 5 standardized seniority tiers.")
    df_seniority = load_salary_by_seniority()

    # Ensure explicit tier ordering
    tier_order = ["Intern", "Junior / Entry", "Mid / Unspecified", "Senior", "Lead / Principal / Executive"]
    df_seniority["Seniority"] = pd.Categorical(df_seniority["Seniority"], categories=tier_order, ordered=True)
    df_seniority = df_seniority.sort_values("Seniority")

    col_sen_chart, col_sen_stats = st.columns([1.4, 1.0])

    with col_sen_chart:
        fig_sen = go.Figure()
        fig_sen.add_trace(
            go.Bar(
                x=df_seniority["Seniority"],
                y=df_seniority["Median_Salary"],
                name="Median Salary",
                marker_color=COLOR_INDIGO,
                text=[f"${v:,.0f}" for v in df_seniority["Median_Salary"]],
                textposition="outside",
            )
        )
        fig_sen.add_trace(
            go.Scatter(
                x=df_seniority["Seniority"],
                y=df_seniority["Mean_Salary"],
                name="Mean Salary",
                mode="lines+markers",
                marker=dict(color=COLOR_CYAN, size=8),
                line=dict(color=COLOR_CYAN, width=2, dash="dash"),
            )
        )
        fig_sen.update_layout(
            title="Seniority Progression: Median & Mean Midpoint",
            yaxis_title="Salary (USD)",
            yaxis_tickformat="$,.0f",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        apply_plotly_theme(fig_sen, height=360)
        st.plotly_chart(fig_sen, use_container_width=True)

    with col_sen_stats:
        st.markdown("##### Seniority Distribution Breakdown")
        display_sen = df_seniority[["Seniority", "N", "Share", "Median_Salary", "Mean_Salary"]].copy()
        display_sen["Share"] = (display_sen["Share"] * 100).round(1).astype(str) + "%"
        display_sen["Median_Salary"] = display_sen["Median_Salary"].apply(lambda x: f"${x:,.0f}")
        display_sen["Mean_Salary"] = display_sen["Mean_Salary"].apply(lambda x: f"${x:,.0f}")
        display_sen["N"] = display_sen["N"].apply(lambda x: f"{x:,}")
        st.dataframe(display_sen, use_container_width=True, hide_index=True)

        render_insight_box(
            "Seniority establishes the baseline structural wage scale. The jump from Junior ($137.5k) to Senior ($190k) "
            "represents a +38.2% baseline differential, while Executive/Lead tiers reach a median of $225,000.",
            bold_prefix="Seniority Effect:",
            border_color=COLOR_CYAN,
        )

    render_hr()

    # 3. Role Family Salary Comparison
    render_section_header("Salary by Role Family", "Horizontal ranking across all 18 standardized technical role families.")
    df_roles = load_salary_by_role().sort_values("Median_Salary", ascending=True)

    fig_role = go.Figure()
    fig_role.add_trace(
        go.Bar(
            y=df_roles["Role_Family"],
            x=df_roles["Median_Salary"],
            orientation="h",
            marker=dict(
                color=df_roles["Median_Salary"],
                colorscale=[[0, "#312E81"], [0.5, COLOR_INDIGO], [1, COLOR_CYAN]],
            ),
            text=[f"${v:,.0f}" for v in df_roles["Median_Salary"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Median: $%{x:,.0f}<br><extra></extra>",
        )
    )
    fig_role.update_layout(
        title="Role Families Ranked by Median Salary",
        xaxis_title="Median Salary (USD)",
        xaxis_tickformat="$,.0f",
        xaxis_range=[100000, 240000],
        margin=dict(l=160, r=40, t=50, b=40),
    )
    apply_plotly_theme(fig_role, height=520)
    st.plotly_chart(fig_role, use_container_width=True)

    render_hr()

    # 4. Location Salary Analysis & Interactive Comparator
    render_section_header("Geographic Salary Differentials", "Metropolitan market hubs vs overall technology cohort.")
    df_loc = load_salary_by_location().sort_values("Median_Salary", ascending=False)

    col_loc_chart, col_comparator = st.columns([1.2, 1.0])

    with col_loc_chart:
        fig_loc = go.Figure()
        fig_loc.add_trace(
            go.Bar(
                x=df_loc["City"],
                y=df_loc["Median_Salary"],
                marker_color=COLOR_EMERALD,
                text=[f"${v:,.0f}" for v in df_loc["Median_Salary"]],
                textposition="outside",
            )
        )
        fig_loc.update_layout(
            title="Metropolitan Regions Ranked by Median Salary",
            yaxis_title="Median Salary (USD)",
            yaxis_tickformat="$,.0f",
            xaxis_tickangle=-45,
        )
        apply_plotly_theme(fig_loc, height=380)
        st.plotly_chart(fig_loc, use_container_width=True)

    with col_comparator:
        st.markdown("##### 🔍 Cohort Segment Comparator")
        st.markdown("<p style='font-size: 0.85rem; color: #94A3B8;'>Compare segment medians against overall benchmark ($180,413).</p>", unsafe_allow_html=True)
        
        sel_role = st.selectbox("Select Role Family", options=df_roles["Role_Family"].tolist(), index=len(df_roles)-1)
        sel_sen = st.selectbox("Select Seniority Tier", options=tier_order, index=3)
        sel_city = st.selectbox("Select Metropolitan Area", options=df_loc["City"].tolist(), index=0)

        role_med = df_roles.loc[df_roles["Role_Family"] == sel_role, "Median_Salary"].values[0]
        sen_med = df_seniority.loc[df_seniority["Seniority"] == sel_sen, "Median_Salary"].values[0]
        city_med = df_loc.loc[df_loc["City"] == sel_city, "Median_Salary"].values[0]
        
        render_html(
            f"""
            <div class="ji-kpi-card" style="margin-top: 10px;">
                <div class="ji-kpi-label">Role Family Median ({sel_role})</div>
                <div class="ji-kpi-value" style="font-size: 1.3rem; color: #818CF8;">${role_med:,.0f}</div>
                <div class="ji-kpi-label" style="margin-top: 10px;">Seniority Tier Median ({sel_sen})</div>
                <div class="ji-kpi-value" style="font-size: 1.3rem; color: #22D3EE;">${sen_med:,.0f}</div>
                <div class="ji-kpi-label" style="margin-top: 10px;">Metro Region Median ({sel_city})</div>
                <div class="ji-kpi-value" style="font-size: 1.3rem; color: #34D399;">${city_med:,.0f}</div>
            </div>
            """
        )

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer()
    render_source_footer("reports/tables/phase3/salary_by_role_family.csv", "Phase 3 EDA")
