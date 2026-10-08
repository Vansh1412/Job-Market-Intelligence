"""
JobIntel Page 5: Interactive Salary Predictor — Phase 7.1 Premium Reconstruction
Live supervised ML salary estimation with premium prediction hero display.
"""

import streamlit as st
import pandas as pd

from src.dashboard.theme import (
    COLOR_INDIGO, COLOR_CYAN, COLOR_EMERALD, COLOR_AMBER, COLOR_CORAL, COLOR_VIOLET,
    ARCHETYPE_COLORS, ARCHETYPE_GRAD,
)
from src.dashboard.ui_components import (
    render_page_hero,
    render_kpi_card,
    render_insight_box,
    render_scientific_disclaimer,
    render_source_footer,
    render_section_header,
    render_hr,
    render_awaiting_state,
    render_prediction_hero,
    render_archetype_badge,
    render_html,
)
from src.dashboard.data_loader import load_feature_metadata
from src.dashboard.inference import predict_salary_and_archetype


def render_predictor_page():
    """Renders the interactive salary prediction tool."""
    render_page_hero(
        icon="🎯",
        title="Salary Predictor",
        subtitle=(
            "Estimate market salary midpoint and project latent archetype membership using the "
            "frozen, audited XGBoost regressor. R² = 0.4233 · Test MAE = $36,381 · Holdout RMSE = $51,082."
        ),
        badge_text="Live ML Inference · Phase 5 Frozen Model",
        accent_color=COLOR_INDIGO,
    )

    meta_info = load_feature_metadata()
    tech_skills_raw = meta_info["tech_skills"]

    role_options = [
        "Backend Developer", "Data / BI Analyst", "Data Engineer", "Data Scientist",
        "DevOps / Cloud / Platform", "Embedded & Hardware", "Engineering Management",
        "Frontend Developer", "Full-Stack Developer", "ML / AI Engineer", "Mobile Engineer",
        "Other Tech", "QA / SDET", "Security Engineer", "Software Engineer",
        "Solutions & Architecture", "Systems & Network Engineer", "Technical Product & PM",
    ]
    seniority_options = [
        "Intern", "Junior / Entry", "Mid / Unspecified", "Senior", "Lead / Principal / Executive"
    ]
    city_options = [
        "Boston", "Chicago", "Costa Mesa", "Denver", "Hawthorne", "Long Beach",
        "Los Angeles", "Mountain View", "New York", "New York City", "Other",
        "San Francisco", "San Jose", "Seattle", "Toronto", "Washington"
    ]
    skill_display_map = {
        s: s.replace("skill_", "").replace("_", " ").title() for s in tech_skills_raw
    }
    skill_options = sorted(list(skill_display_map.keys()), key=lambda k: skill_display_map[k])

    # ── Input Configuration ────────────────────────────────────────────────────
    render_section_header("Job Profile Configuration", "Specify structural metadata and select technical competencies.")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        sel_role = st.selectbox("Role Family", options=role_options, index=9)
    with col_r2:
        sel_sen = st.selectbox("Seniority Level", options=seniority_options, index=3)
    with col_r3:
        sel_city = st.selectbox("Metropolitan Region", options=city_options, index=11)

    col_r4, col_r5 = st.columns([1.0, 3.0])
    with col_r4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        sel_remote = st.checkbox("Remote Opportunity", value=True)
    with col_r5:
        default_skills = ["skill_machine_learning", "skill_python", "skill_pytorch"]
        sel_skills = st.multiselect(
            "Technical Skills (82 Taxonomy Skills)",
            options=skill_options,
            default=default_skills,
            format_func=lambda k: skill_display_map[k],
        )

    btn_predict = st.button(
        "🚀 Calculate Estimated Salary Midpoint",
        type="primary",
        use_container_width=True,
    )

    render_hr()

    # ── Prediction Output ──────────────────────────────────────────────────────
    if btn_predict or "last_pred" in st.session_state:
        res = predict_salary_and_archetype(
            role_family=sel_role,
            seniority=sel_sen,
            city_clean=sel_city,
            is_remote=sel_remote,
            selected_skills=sel_skills,
        )
        st.session_state["last_pred"] = res

        pred_sal = res["predicted_salary"]
        arch_info = res["archetype"]
        arch_code = arch_info["code"]
        arch_color = ARCHETYPE_COLORS.get(arch_code, COLOR_INDIGO)
        arch_grad = ARCHETYPE_GRAD.get(arch_code, "linear-gradient(135deg, rgba(99,102,241,0.13), rgba(99,102,241,0.03))")

        render_section_header("Estimation & Archetype Mapping", "Live inference outputs from the frozen analytical pipeline.")

        # Prediction hero + archetype + error context
        p1, p2, p3 = st.columns([1.4, 1.0, 1.0])

        with p1:
            render_prediction_hero(pred_sal)

        with p2:
            render_html(
                f"""
                <div class="ji-kpi-card" style="border-top: 2px solid {arch_color}; background: {arch_grad};">
                    <div class="ji-kpi-accent-bar" style="background: {arch_color};"></div>
                    <div class="ji-kpi-label">Detected Archetype</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #F1F5F9; margin-bottom: 4px;">{arch_info['name']}</div>
                    <div style="font-size: 0.75rem; font-weight: 700; color: {arch_color}; letter-spacing: 0.06em; text-transform: uppercase;">{arch_code}</div>
                    <div class="ji-kpi-sub" style="margin-top: 8px;">{arch_info['desc']}</div>
                </div>
                """
            )

        with p3:
            render_html(
                f"""
                <div class="ji-kpi-card" style="border-top: 2px solid {COLOR_CYAN};">
                    <div class="ji-kpi-accent-bar" style="background: {COLOR_CYAN};"></div>
                    <div class="ji-kpi-label">Holdout Error Context</div>
                    <div class="ji-kpi-value" style="font-size: 1.6rem; color: {COLOR_CYAN};">±${arch_info['typical_mae']:,.0f}</div>
                    <div style="font-size: 0.75rem; color: {COLOR_CYAN}; font-weight: 600; margin-top: 4px;">Archetype Holdout MAE</div>
                    <div class="ji-kpi-sub">Relative error: ~{arch_info['rel_error']:.1f}%</div>
                </div>
                """
            )

        render_insight_box(
            f"Based on <strong>{sel_sen}</strong> seniority, <strong>{sel_role}</strong> role in "
            f"<strong>{sel_city}</strong> ({'Remote' if sel_remote else 'On-site'}) with {len(sel_skills)} skills — "
            f"estimated midpoint <strong>${pred_sal:,.0f}</strong>. "
            f"Projected into archetype <strong>{arch_code}</strong> with typical holdout error ±${arch_info['typical_mae']:,.0f}.",
            bold_prefix="Prediction Decomposition:",
            border_color=COLOR_INDIGO,
        )

        st.info(
            "ℹ️ **Historical Error Context:** The ± figure is the empirical holdout MAE for this archetype. "
            "It is provided for diagnostic transparency and must **not** be treated as a mathematical confidence interval."
        )

    else:
        render_awaiting_state(
            icon="🎯",
            title="Awaiting Profile Configuration",
            subtitle="Select role metadata and technical competencies above, then click 'Calculate Estimated Salary Midpoint'.",
        )

    render_scientific_disclaimer(
        "<strong>Predictive Boundary Notice:</strong> Model R² is 0.4233, indicating that approximately 57.7% of "
        "salary variance is driven by unobserved factors (candidate pedigree, equity budgets, interview performance). "
        "Predictions should be used for analytical benchmarking rather than deterministic compensation setting."
    )
    render_source_footer("models/phase5/best_model.pkl & feature_metadata.json", "Phase 5 Inference")
