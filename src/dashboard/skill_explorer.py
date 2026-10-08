"""
JobIntel Page 3: Skill Explorer
Interactive exploration of technical skill prevalence, salary associations,
companion co-occurrences, and archetype cluster affinity.
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
    COLOR_PURPLE,
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
    load_skill_frequency,
    load_skill_salary_association,
    load_skill_cooccurrence,
    load_cluster_skills,
)


def render_skill_explorer_page():
    """Renders the interactive technical skill explorer page."""
    render_page_hero(
        icon='🛠️',
        title='Skill Explorer',
        subtitle='Inspect the market footprint, observed salary associations, and companion technologies across 82 standardized technical skills in Taxonomy D.',
        badge_text='Phase 3 EDA | 82 Skills | Taxonomy D',
    )

    df_freq = load_skill_frequency()
    df_assoc = load_skill_salary_association()
    df_lift = load_cluster_skills()

    # Clean skill names for display
    skill_list = sorted(df_freq["Skill"].tolist())

    # 1. Interactive Single Skill Profile Selector
    render_section_header("Individual Skill Deep-Dive", "Select a skill to inspect its demand, compensation profile, and archetype affinity.")
    
    # Default to Python or Machine Learning if available
    default_idx = skill_list.index("skill_python") if "skill_python" in skill_list else 0
    selected_skill_raw = st.selectbox(
        "Search & Select Technical Skill",
        options=skill_list,
        index=default_idx,
        format_func=lambda s: s.replace("skill_", "").replace("_", " ").title(),
    )

    clean_name = selected_skill_raw.replace("skill_", "").replace("_", " ").title()

    # Lookup selected skill row
    freq_row = df_freq[df_freq["Skill"] == selected_skill_raw].iloc[0]
    assoc_row = df_assoc[df_assoc["Skill"] == selected_skill_raw]
    has_assoc = len(assoc_row) > 0

    p_count = int(freq_row["Modeling_Count"])
    p_prev = float(freq_row["Modeling_Prevalence"]) * 100
    c_prev = float(freq_row["Corpus_Prevalence"]) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Modeling Postings", f"{p_count:,}", f"Corpus Share: {c_prev:.1f}%")
    with col2:
        render_kpi_card("Salary Cohort Share", f"{p_prev:.1f}%", f"{p_count:,} out of 34,036 jobs")
    with col3:
        if has_assoc:
            med_sal = float(assoc_row["Median_Salary"].values[0])
            render_kpi_card("Observed Median", f"${med_sal:,.0f}", "Midpoint when skill present")
        else:
            render_kpi_card("Observed Median", "N/A", "Insufficient Support")
    with col4:
        if has_assoc:
            diff = med_sal - 180413.0
            delta_str = f"+${diff:,.0f}" if diff >= 0 else f"-${abs(diff):,.0f}"
            render_kpi_card("Diff vs Cohort Median", delta_str, "Benchmark: $180,413", delta=delta_str, delta_positive=(diff >= 0))
        else:
            render_kpi_card("Diff vs Benchmark", "N/A", "Benchmark: $180,413")

    # Archetype Affinity for this Skill
    lift_row = df_lift[df_lift["Skill"] == selected_skill_raw]
    if len(lift_row) > 0:
        cluster_cols = [c for c in df_lift.columns if c.startswith("Cluster_")]
        lifts = {c.replace("Cluster_", "").replace("_", " ", 1): float(lift_row[c].values[0]) for c in cluster_cols}
        best_cluster = max(lifts, key=lifts.get)
        best_lift = lifts[best_cluster]

        render_insight_box(
            f"The skill <strong>{clean_name}</strong> shows its highest representation in archetype "
            f"<strong>{best_cluster}</strong> with a statistical lift factor of <strong>{best_lift:.2f}x</strong> "
            f"relative to the global technical baseline.",
            bold_prefix="Archetype Affinity:",
            border_color=COLOR_INDIGO,
        )

    render_hr()

    # 2. Top Skills by Prevalence & Top Salary-Associated Skills
    render_section_header("Macro Skill Landscapes", "Top skills by market prevalence compared against top salary-associated tools.")
    
    col_chart_left, col_chart_right = st.columns(2)

    with col_chart_left:
        top_prevalence = df_freq.sort_values("Modeling_Prevalence", ascending=False).head(12)
        fig_prev = go.Figure(
            go.Bar(
                y=[s.replace("skill_", "").replace("_", " ").title() for s in top_prevalence["Skill"]],
                x=top_prevalence["Modeling_Prevalence"] * 100,
                orientation="h",
                marker_color=COLOR_INDIGO,
                text=[f"{v*100:.1f}%" for v in top_prevalence["Modeling_Prevalence"]],
                textposition="outside",
            )
        )
        fig_prev.update_layout(
            title="Top 12 Skills by Market Prevalence (% of Jobs)",
            xaxis_title="Prevalence (%)",
            yaxis_autorange="reversed",
            margin=dict(l=100, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_prev, height=420)
        st.plotly_chart(fig_prev, use_container_width=True)

    with col_chart_right:
        top_sal = df_assoc.sort_values("Median_Salary", ascending=False).head(12)
        fig_sal = go.Figure(
            go.Bar(
                y=[s.replace("skill_", "").replace("_", " ").title() for s in top_sal["Skill"]],
                x=top_sal["Median_Salary"],
                orientation="h",
                marker=dict(
                    color=top_sal["Median_Salary"],
                    colorscale=[[0, "#312E81"], [0.5, COLOR_INDIGO], [1, COLOR_CYAN]],
                ),
                text=[f"${v:,.0f}" for v in top_sal["Median_Salary"]],
                textposition="outside",
            )
        )
        fig_sal.update_layout(
            title="Top 12 Skills by Observed Median Salary",
            xaxis_title="Median Salary (USD)",
            xaxis_tickformat="$,.0f",
            xaxis_range=[170000, 210000],
            yaxis_autorange="reversed",
            margin=dict(l=100, r=40, t=50, b=40),
        )
        apply_plotly_theme(fig_sal, height=420)
        st.plotly_chart(fig_sal, use_container_width=True)

    render_hr()

    # 3. Co-Occurrence Heatmap for Top Technical Skills
    render_section_header("Skill Co-Occurrence Patterns", "Pairwise joint presence across the 25 most prevalent technical skills.")
    df_cooc = load_skill_cooccurrence()

    # Format column and index names
    clean_labels = [s.replace("skill_", "").replace("_", " ").replace("-", " ").title() for s in df_cooc.index]
    
    fig_heat = px.imshow(
        df_cooc.values,
        x=clean_labels,
        y=clean_labels,
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig_heat.update_layout(
        title="Joint Co-Occurrence Matrix (Top 25 Technical Skills)",
        xaxis_tickangle=-45,
        margin=dict(l=120, r=40, t=50, b=120),
    )
    apply_plotly_theme(fig_heat, height=540)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer(
        "<strong>Observational Association Notice:</strong> Observed salary differences reflect market co-occurrence "
        "and employer compensation packaging. Skill presence does not imply that acquiring a tool causally causes higher wages."
    )
    render_source_footer("reports/tables/phase3/skill_salary_association.csv", "Phase 3 EDA")
