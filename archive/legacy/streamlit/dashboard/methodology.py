"""
JobIntel Page 8: Research Methodology & Transparency
End-to-end analytical pipeline, reproducibility protocols, and comprehensive scientific limitations.
"""

import streamlit as st
import pandas as pd

from src.dashboard.theme import (
    COLOR_INDIGO,
    COLOR_CYAN,
    COLOR_EMERALD,
    COLOR_AMBER,
    COLOR_CORAL,
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


def render_methodology_page():
    """Renders the comprehensive research methodology and limitations page."""
    render_page_hero(
        icon='📚',
        title='Research Methodology & Transparency',
        subtitle='Comprehensive documentation of the end-to-end analytical architecture, reproducibility controls, leakage prevention protocols, and acknowledged project boundaries.',
        badge_text='INT234 · 7-Phase Pipeline · Audit Score 99/100',
    )

    # 1. Pipeline Execution Map
    render_section_header("Phased Research Architecture", "Strict sequential analytical phases from raw ingestion to interactive deployment.")

    phases = [
        ("Phase 1", "Provenance & Audit", "Audited 394,300 raw postings from DataForge Tier 1 snapshot. Selected Dataset A over B due to USD coverage and direct ATS sourcing."),
        ("Phase 2 & 2.1", "Taxonomic Cleaning", "Established Taxonomy D: 82 technical skills, 18 role families, 5 seniority tiers. Enforced [$30k, $600k] salary domain bounds."),
        ("Phase 3", "Exploratory Discovery", "Conducted statistical profiling on 34,036 salary postings. Mapped skill prevalence, salary associations, and pairwise co-occurrences."),
        ("Phase 4 & 4.1", "Archetype Discovery", "Centered Covariance PCA (15 PCs, 56.05% variance) + K-Means (k=7) on 116,830 skill-bearing jobs. Zero-skill postings isolated."),
        ("Phase 4.2", "Statistical Clustering Audit", "Verified resampling stability (Mean ARI = 0.7901, AMI = 0.8030). Audited covariance vs correlation scaling trade-offs."),
        ("Phase 5", "Supervised Modeling", "Trained 5 algorithms across Feature Sets A, B, C with 5-fold CV. XGBoost selected; verified zero target leakage across folds."),
        ("Phase 6", "Scientific Synthesis", "Compiled Frozen Results Registry (SSOT), resolved semantic claims, and audited cross-phase numerical consistency (Score: 99/100)."),
        ("Phase 7", "Interactive Deployment", "Packaged frozen models and aggregated summaries into JobIntel: zero retraining, sub-millisecond inference, full license compliance."),
    ]

    for p_tag, p_name, p_desc in phases:
        render_html(
            f"""
            <div style="background: rgba(21, 28, 44, 0.5); border-left: 3px solid #818CF8; border-radius: 0 8px 8px 0; padding: 10px 16px; margin-bottom: 8px;">
                <span style="color: #818CF8; font-weight: 700; font-size: 0.85rem; margin-right: 8px;">{p_tag}: {p_name}</span>
                <span style="color: #94A3B8; font-size: 0.85rem;">— {p_desc}</span>
            </div>
            """
        )

    render_hr()

    # 2. Strict Target Leakage Controls
    render_section_header("Leakage Prevention Protocol", "Strict training-partition isolation verified in Phase 5 audit.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        render_html(
            """
            <div class="ji-kpi-card" style="min-height: 180px;">
                <div class="ji-kpi-label" style="color: #34D399;">Preprocessing & Encoders</div>
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">Fit-on-Train Exclusivity</div>
                <div class="ji-kpi-sub" style="color: #94A3B8; line-height: 1.5;">
                    The <code>MetadataTransformer</code> was fitted strictly on the 80% training partition (N = 27,228). 
                    No validation or holdout test statistics leaked into one-hot categories or feature scalers.
                </div>
            </div>
            """
        )
    with col_l2:
        render_html(
            """
            <div class="ji-kpi-card" style="min-height: 180px;">
                <div class="ji-kpi-label" style="color: #22D3EE;">Feature Set C Archetypes</div>
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">Fold-Safe Centroid Projection</div>
                <div class="ji-kpi-sub" style="color: #94A3B8; line-height: 1.5;">
                    PCA components and K-Means centroids in Feature Set C were fitted inside each CV training fold. 
                    Holdout test archetypes were predicted using training centroids via nearest-distance assignment.
                </div>
            </div>
            """
        )

    render_hr()

    # 3. Acknowledged Scientific Limitations (The 9 Core Dimensions)
    render_section_header("The 9 Project Limitations", "Defensive boundary documentation required for distinction-level academic research.")

    limits = [
        ("1. Salary Disclosure Bias", "Not every employer discloses compensation in ATS listings; observations reflect transparent employers which may skew toward larger tech firms or states with pay transparency laws."),
        ("2. Base Midpoint Incompleteness", "Target reflects base salary midpoints only. It excludes equity, stock grants, performance bonuses, signing bonuses, and 401(k) benefits, which constitute substantial total compensation in tech."),
        ("3. Binary Skill Indicators", "Skills are represented as binary presence/absence indicators (0 or 1). Depth of expertise, years of experience, and proficiency levels are uncaptured."),
        ("4. Curated Taxonomy Boundaries", "Taxonomy D contains 82 curated technical skills. Specialized niche tools, internal proprietary frameworks, and newly emerging libraries are unrepresented."),
        ("5. Upper-Tail Sparsity", "Postings offering midpoints > $350,000 are relatively sparse in standard ATS records, contributing to higher prediction residuals in executive and enterprise architect bands."),
        ("6. FOUND_TECH Residual Cohort", "The largest discovered archetype (FOUND_TECH, 49.5%) is a heterogeneous residual group (85.3% have ≤2 skills) rather than a tightly coherent professional specialty."),
        ("7. PCA Dimensionality Compression", "The 15 retained continuous Principal Components capture 56.05% of skill variance; 43.95% remains unrepresented outside the latent space."),
        ("8. Observational Bounds (No Causality)", "All findings represent observational labor market associations. Acquiring a skill does not causally produce or guarantee higher wages."),
        ("9. Geographic Generalization Limits", "Data is sourced from North American technology job boards; conclusions cannot be automatically generalized to global labor markets."),
    ]

    for lim_title, lim_body in limits:
        render_html(
            f"""
            <div style="margin-bottom: 12px; padding: 12px 16px; background: rgba(15, 23, 42, 0.4); border: 1px solid #1E293B; border-radius: 8px;">
                <div style="font-weight: 600; color: #F8FAFC; font-size: 0.88rem;">{lim_title}</div>
                <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 4px; line-height: 1.45;">{lim_body}</div>
            </div>
            """
        )

    # Scientific Disclaimer & Source Footer
    render_scientific_disclaimer()
    render_source_footer("reports/phase6_integrated_analysis.md & reproducibility.md", "Phase 6 Integration")
