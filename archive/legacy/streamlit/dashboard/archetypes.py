"""
JobIntel Page 4: Archetype Explorer
Interactive exploration of the seven latent skill archetypes discovered via PCA and K-Means.
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
)
from src.dashboard.data_loader import (
    load_archetype_dict,
    load_cluster_sizes,
    load_cluster_salary,
    load_cluster_skills,
    load_cluster_roles,
    load_pca_variance,
)


def render_archetypes_page():
    """Renders the unsupervised archetype discovery page."""
    render_page_hero(
        icon='🧬',
        title='Archetype Explorer',
        subtitle='Discovery and structural profiling of seven recurring skill-based job archetypes identified via Centered Covariance PCA (15 PCs) and K-Means clustering (k=7) on 116,830 skill-bearing postings.',
        badge_text='Phase 4.1 · k=7 · Mean ARI 0.7901',
    )

    df_dict = load_archetype_dict()
    df_sizes = load_cluster_sizes()
    df_salary = load_cluster_salary()
    df_lift = load_cluster_skills()
    df_roles = load_cluster_roles()

    # 1. Macro Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Clustering Population", "116,830", "Postings with ≥1 skill")
    with c2:
        render_kpi_card("Selected k", "k = 7", "Silhouette: 0.2379 | DB: 1.7633")
    with c3:
        render_kpi_card("Cluster Stability", "0.7901 ARI", "Good-to-Strong Resampling Stability")
    with c4:
        render_kpi_card("PCA Retained Dim.", "15 PCs", "56.05% Cumulative Variance")

    # Methodological Callout
    render_insight_box(
        "<strong>RQ2 Finding:</strong> Postings naturally form skill-based structures, "
        "<strong>supported with moderate separation and substantial overlap</strong>. "
        "Archetypes are empirical, fuzzy labor market profiles rather than mutually exclusive occupational classes.",
        bold_prefix="Methodological Conclusion:",
        border_color=COLOR_CYAN,
    )

    render_hr()

    # 2. Archetype Population Distribution
    render_section_header("Archetype Population Distribution", "Relative market share across the 116,830 skill-bearing postings.")
    
    col_pie, col_bar = st.columns([1.0, 1.4])

    with col_pie:
        fig_donut = go.Figure(
            go.Pie(
                labels=df_sizes["Archetype_Name"],
                values=df_sizes["Postings_Count"],
                hole=0.45,
                marker=dict(colors=[ARCHETYPE_COLORS.get(code, "#64748B") for code in df_sizes["Short_Code"]]),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )
        )
        fig_donut.update_layout(
            title="Archetype Market Shares",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        apply_plotly_theme(fig_donut, height=360)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_bar:
        # Salary Comparison across Archetypes
        df_sal_sorted = df_salary.sort_values("Median_Salary", ascending=True)
        fig_sal = go.Figure(
            go.Bar(
                y=df_sal_sorted["Archetype_Name"],
                x=df_sal_sorted["Median_Salary"],
                orientation="h",
                marker_color=[ARCHETYPE_COLORS.get(code.split()[0], COLOR_INDIGO) for code in df_sal_sorted["Archetype_Name"]],
                text=[f"${v:,.0f}" for v in df_sal_sorted["Median_Salary"]],
                textposition="outside",
            )
        )
        fig_sal.update_layout(
            title="Observed Median Salary by Archetype (USD)",
            xaxis_title="Median Salary (USD)",
            xaxis_tickformat="$,.0f",
            xaxis_range=[140000, 240000],
            margin=dict(l=150, r=40, t=40, b=40),
        )
        apply_plotly_theme(fig_sal, height=360)
        st.plotly_chart(fig_sal, use_container_width=True)

    render_hr()

    # 3. Interactive Archetype Deep-Dive
    render_section_header("Archetype Profile Deep-Dive", "Select an archetype to inspect defining skill lift, role distribution, and salary spreads.")

    selected_arch_name = st.selectbox(
        "Select Job Archetype",
        options=df_dict["Archetype_Name"].tolist(),
        index=0,
    )

    arch_row = df_dict[df_dict["Archetype_Name"] == selected_arch_name].iloc[0]
    arch_id = int(arch_row["Cluster_ID"])
    arch_code = arch_row["Short_Code"]

    # Special callout for FOUND_TECH
    if arch_code == "FOUND_TECH":
        st.warning(
            "⚠️ **FOUND_TECH Heterogeneity Notice:** FOUND_TECH represents a broad and heterogeneous residual "
            "foundational cohort. Evidence: 67.56% of postings possess only a single parsed skill, and 85.31% have ≤2 skills. "
            "It must not be interpreted as a narrowly coherent technical specialization."
        )

    # Detailed Archetype Metrics
    size_row = df_sizes[df_sizes["Cluster_ID"] == arch_id].iloc[0]
    sal_row = df_salary[df_salary["Cluster_ID"] == arch_id].iloc[0]

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        render_kpi_card("Postings Count", f"{int(size_row['Postings_Count']):,}", f"Share: {size_row['Primary_Share_%']:.2f}%")
    with d2:
        render_kpi_card("Median Salary", f"${sal_row['Median_Salary']:,.0f}", f"Mean: ${sal_row['Mean_Salary']:,.0f}")
    with d3:
        render_kpi_card("Salary IQR Spread", f"${sal_row['Std_Dev']:,.0f}", "Standard Deviation")
    with d4:
        render_kpi_card("Defining Signature", arch_code, arch_row["Top_Defining_Skills"][:30] + "...")

    col_lift_chart, col_role_chart = st.columns(2)

    with col_lift_chart:
        # Top Lift Skills
        cluster_lift_col = f"Cluster_{arch_id}_{arch_code}"
        if cluster_lift_col in df_lift.columns:
            top_lift_skills = df_lift.sort_values(cluster_lift_col, ascending=False).head(8)
            fig_lift = go.Figure(
                go.Bar(
                    y=[s.replace("skill_", "").replace("_", " ").title() for s in top_lift_skills["Skill"]],
                    x=top_lift_skills[cluster_lift_col],
                    orientation="h",
                    marker_color=ARCHETYPE_COLORS.get(arch_code, COLOR_INDIGO),
                    text=[f"{v:.2f}x" for v in top_lift_skills[cluster_lift_col]],
                    textposition="outside",
                )
            )
            fig_lift.update_layout(
                title=f"Top 8 Over-Indexed Skills (Lift Factor: {arch_code})",
                xaxis_title="Lift Ratio vs Global Baseline",
                yaxis_autorange="reversed",
                margin=dict(l=100, r=40, t=50, b=40),
            )
            apply_plotly_theme(fig_lift, height=380)
            st.plotly_chart(fig_lift, use_container_width=True)

    with col_role_chart:
        # Role Family Composition in this Cluster
        roles_cluster = df_roles[df_roles["Cluster_ID"] == arch_id].sort_values("Share_Within_Cluster_%", ascending=False).head(6)
        fig_r = go.Figure(
            go.Bar(
                y=roles_cluster["Role_Family"],
                x=roles_cluster["Share_Within_Cluster_%"],
                orientation="h",
                marker_color=COLOR_CYAN,
                text=[f"{v:.1f}%" for v in roles_cluster["Share_Within_Cluster_%"]],
                textposition="outside",
            )
        )
        fig_r.update_layout(
            title=f"Primary Role Families inside {arch_code}",
            xaxis_title="Share within Archetype (%)",
            yaxis_autorange="reversed",
            margin=dict(l=140, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_r, height=380)
        st.plotly_chart(fig_r, use_container_width=True)

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer(
        "<strong>Clustering Boundary Notice:</strong> Archetypes reflect statistical groupings discovered through "
        "Centered Covariance PCA and K-Means. 43.95% of technical variance remains outside the 15-dimensional representation."
    )
    render_source_footer("reports/tables/phase4_1/archetype_dictionary.csv", "Phase 4.1 Archetypes")
