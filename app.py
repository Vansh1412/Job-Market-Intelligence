"""
JobIntel — Interactive ML-Powered Job Market Intelligence Dashboard
INT234 Predictive Analytics Capstone Project
================================================================
Phase 7.1 — Premium UI/UX Reconstruction
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

import streamlit as st

st.set_page_config(
    page_title="JobIntel — Job Market Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.dashboard.theme import inject_custom_css
inject_custom_css()

from src.dashboard.overview import render_overview_page
from src.dashboard.salary_intel import render_salary_intel_page
from src.dashboard.skill_explorer import render_skill_explorer_page
from src.dashboard.archetypes import render_archetypes_page
from src.dashboard.predictor import render_predictor_page
from src.dashboard.model_eval import render_model_eval_page
from src.dashboard.error_analysis import render_error_analysis_page
from src.dashboard.methodology import render_methodology_page

# ── Premium Sidebar Branding ───────────────────────────────────────────────────
st.sidebar.markdown(
    '<div class="ji-sidebar-brand">'
    '<div class="ji-sidebar-logo">'
    '<span class="ji-sidebar-logo-dot"></span>JobIntel'
    '</div>'
    '<div class="ji-sidebar-tagline">Job Market Intelligence</div>'
    '<div class="ji-sidebar-meta">INT234 Predictive Analytics &middot; Phase 7</div>'
    '</div>'
    '<div class="ji-sidebar-divider"></div>',
    unsafe_allow_html=True,
)

# ── Navigation ─────────────────────────────────────────────────────────────────
pages = {
    "Executive & Foundations": [
        st.Page(render_overview_page, title="Executive Overview", icon="🏛️", default=True),
        st.Page(render_methodology_page, title="Research Methodology", icon="📚"),
    ],
    "Market Analytics": [
        st.Page(render_salary_intel_page, title="Salary Intelligence", icon="💰"),
        st.Page(render_skill_explorer_page, title="Skill Explorer", icon="🛠️"),
        st.Page(render_archetypes_page, title="Archetype Explorer", icon="🧬"),
    ],
    "Machine Learning Engine": [
        st.Page(render_predictor_page, title="Salary Predictor", icon="🎯"),
        st.Page(render_model_eval_page, title="Model Performance", icon="📊"),
        st.Page(render_error_analysis_page, title="Archetype Error (RQ3)", icon="🔍"),
    ],
}

nav = st.navigation(pages)
nav.run()

# ── Sidebar Footer ─────────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div class="ji-sidebar-footer">'
    '<div><strong>Status:</strong> Phase 1&ndash;6 Frozen (SSOT)</div>'
    '<div><strong>License:</strong> DataForge Tier 1 (Derived)</div>'
    '<div><strong>ML Stack:</strong> Scikit-learn + XGBoost</div>'
    '<div><strong>Archetypes:</strong> 7 (PCA + K-Means, k=7)</div>'
    '</div>',
    unsafe_allow_html=True,
)
