"""
JobIntel Page 1: Executive Overview — Phase 7.1 Premium Reconstruction
Premium hero, glass KPI cards, RQ cards, and animated funnel visualization.
"""

import streamlit as st
import plotly.graph_objects as go

from src.dashboard.theme import (
    COLOR_INDIGO, COLOR_CYAN, COLOR_EMERALD, COLOR_AMBER, COLOR_VIOLET,
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
from src.dashboard.data_loader import load_funnel_data


def render_overview_page():
    """Renders the executive overview landing page."""
    # ── Hero Header ────────────────────────────────────────────────────────────
    render_page_hero(
        icon="🏛️",
        title="JobIntel",
        subtitle=(
            "An interactive research platform for discovering skill-based job archetypes, "
            "analyzing labor market salary structures, and evaluating supervised machine learning "
            "performance across the North American technology sector."
        ),
        badge_text="INT234 Predictive Analytics · Phase 6 Frozen",
        accent_color=COLOR_INDIGO,
    )

    # ── KPI Row 1: Research Scale ───────────────────────────────────────────────
    render_section_header("Research Scale & Model Benchmarks", "Corpus statistics and holdout evaluation metrics.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Raw Harvested", "394,300", "ATS Postings (DataForge Tier 1)", accent_color=COLOR_INDIGO)
    with c2:
        render_kpi_card("Skill-Bearing", "116,830", "≥1 Parsed Skill — Clustering Pop.", accent_color=COLOR_CYAN)
    with c3:
        render_kpi_card("Salary Cohort", "34,036", "USD Midpoints ($30k–$600k)", accent_color=COLOR_EMERALD)
    with c4:
        render_kpi_card(
            "Holdout Test MAE", "$36,381",
            "Baseline Reduction: 28.4%",
            delta="28.4% vs. baseline", delta_positive=True,
            accent_color=COLOR_VIOLET,
        )

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_kpi_card("Holdout Test R²", "0.4233", "Unexplained Variance: 57.7%", accent_color=COLOR_INDIGO)
    with c6:
        render_kpi_card(
            "Holdout Test RMSE", "$51,082",
            "Baseline Reduction: 24.5%",
            delta="24.5% vs. baseline", delta_positive=True,
            accent_color=COLOR_CYAN,
        )
    with c7:
        render_kpi_card("Discovered Archetypes", "7", "Mean Stability ARI: 0.7901", accent_color=COLOR_AMBER)
    with c8:
        render_kpi_card("Technical Skills", "82", "Curated Taxonomy D", accent_color=COLOR_EMERALD)

    render_hr()

    # ── Research Questions ─────────────────────────────────────────────────────
    render_section_header("The Three Research Questions", "Core empirical objectives and validated findings.")
    rq1, rq2, rq3 = st.columns(3)

    with rq1:
        render_html(
            """
            <div class="ji-rq-card" style="border-top: 2px solid #818CF8;">
                <div class="ji-rq-number" style="color: #818CF8;">Research Question 1</div>
                <div class="ji-rq-title">Skill–Salary Associations</div>
                <div class="ji-rq-question">Which skills and skill combinations are most associated with higher salaries?</div>
                <div class="ji-rq-finding">
                    <strong>Supported.</strong> AI/ML tools (<code>PyTorch</code>, <code>Deep Learning</code>,
                    <code>TensorFlow</code>) and infrastructure stacks exhibit top observed salary medians
                    ($195k–$197k). Conditional XGBoost importance is dominated by ML, cloud architecture,
                    and systems engineering.
                </div>
            </div>
            """
        )

    with rq2:
        render_html(
            """
            <div class="ji-rq-card" style="border-top: 2px solid #22D3EE;">
                <div class="ji-rq-number" style="color: #22D3EE;">Research Question 2</div>
                <div class="ji-rq-title">Latent Archetype Discovery</div>
                <div class="ji-rq-question">Do job postings naturally form meaningful skill-based archetypes?</div>
                <div class="ji-rq-finding">
                    <strong>Supported — with moderate separation and substantial overlap.</strong>
                    Identified 7 stable clusters (mean ARI = 0.7901). Largest cluster
                    (<code>FOUND_TECH</code>, 49.5%) is a heterogeneous residual cohort
                    dominated by low-specificity postings.
                </div>
            </div>
            """
        )

    with rq3:
        render_html(
            """
            <div class="ji-rq-card" style="border-top: 2px solid #34D399;">
                <div class="ji-rq-number" style="color: #34D399;">Research Question 3</div>
                <div class="ji-rq-title">Archetype-Specific Error Variance</div>
                <div class="ji-rq-question">Does salary-prediction error differ meaningfully across archetypes?</div>
                <div class="ji-rq-finding">
                    <strong>Yes.</strong> Kruskal-Wallis <em>H</em> = 88.10 (<em>p</em> = 7.53×10⁻¹⁷)
                    confirms statistically significant error variance. <code>AI_ML</code> has lowest
                    MAE ($27,002) while <code>CLOUD_ARCH</code> has highest ($46,098).
                </div>
            </div>
            """
        )

    render_hr()

    # ── Data Pipeline Funnel ───────────────────────────────────────────────────
    render_section_header("Data Pipeline & Population Funnel", "Step-by-step corpus curation and sample attrition.")
    df_funnel = load_funnel_data()

    col_funnel, col_insights = st.columns([1.3, 1.0])

    with col_funnel:
        fig_funnel = go.Figure(
            go.Funnel(
                y=df_funnel["Stage"],
                x=df_funnel["Count"],
                textposition="inside",
                textinfo="value+percent previous",
                opacity=0.92,
                marker=dict(
                    color=[COLOR_INDIGO, "#6366F1", COLOR_CYAN, COLOR_EMERALD, "#059669"],
                    line=dict(width=1, color="rgba(99,102,241,0.2)"),
                ),
                connector=dict(line=dict(color="rgba(99,102,241,0.2)", width=1.5)),
            )
        )
        fig_funnel.update_layout(
            title="Postings Volume Across Ingestion & Filtering Stages",
            margin=dict(l=20, r=20, t=44, b=20),
        )
        apply_plotly_theme(fig_funnel, height=370)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_insights:
        render_insight_box(
            "Deduplication eliminated 58,305 casing/whitespace redundant records (14.8%), "
            "preserving full corpus provenance without distorting market density.",
            bold_prefix="Funnel Milestone 1:",
            border_color=COLOR_INDIGO,
        )
        render_insight_box(
            "Phase 4.1 quarantined 219,165 zero-skill postings from primary clustering, "
            "preventing degenerate centroid collapse and isolating 116,830 skill-bearing jobs.",
            bold_prefix="Funnel Milestone 2:",
            border_color=COLOR_CYAN,
        )
        render_insight_box(
            "The supervised regression cohort comprises 34,036 technology postings with verified "
            "direct USD salary midpoints constrained to the defensible [$30,000, $600,000] interval.",
            bold_prefix="Funnel Milestone 3:",
            border_color=COLOR_EMERALD,
        )

    render_scientific_disclaimer()
    render_source_footer("reports/frozen_results_registry.md", "Phase 6 Synthesis")
