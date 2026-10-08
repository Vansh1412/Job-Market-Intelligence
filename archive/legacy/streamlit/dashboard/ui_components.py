"""
JobIntel Reusable UI Components — Phase 7.1 Premium Reconstruction
All components emit clean HTML using the ji-* design system CSS classes.
NO raw HTML should ever render; all st.markdown calls use unsafe_allow_html=True correctly
and strip leading indentation to prevent markdown parser code-block escaping.
"""

import streamlit as st


def render_html(html: str):
    """Renders raw HTML safely without triggering Markdown indented code block parsing."""
    cleaned = "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Page Hero Header
# ──────────────────────────────────────────────────────────────────────────────
def render_page_hero(
    icon: str,
    title: str,
    subtitle: str,
    badge_text: str = None,
    accent_color: str = "#818CF8",
):
    """Renders a premium glassmorphic page hero header."""
    badge_html = f'<div class="ji-hero-badge">{badge_text}</div>' if badge_text else ""
    render_html(f"""
    <div class="ji-hero">
        {badge_html}
        <div class="ji-hero-title">{icon} {title}</div>
        <p class="ji-hero-subtitle">{subtitle}</p>
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# KPI Cards
# ──────────────────────────────────────────────────────────────────────────────
def render_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    delta: str = "",
    delta_positive: bool = True,
    accent_color: str = None,
):
    """Renders a premium glass KPI metric card."""
    delta_html = ""
    if delta:
        delta_class = "ji-kpi-delta-pos" if delta_positive else "ji-kpi-delta-neg"
        delta_arrow = "↑" if delta_positive else "↓"
        delta_html = f'<div class="{delta_class}">{delta_arrow} {delta}</div>'

    sub_html = f'<div class="ji-kpi-sub">{subtitle}</div>' if subtitle else ""
    accent_bar_html = ""
    if accent_color:
        accent_bar_html = f'<div class="ji-kpi-accent-bar" style="background: {accent_color};"></div>'

    render_html(f"""
    <div class="ji-kpi-card">
        {accent_bar_html}
        <div class="ji-kpi-label">{title}</div>
        <div class="ji-kpi-value">{value}</div>
        {delta_html}
        {sub_html}
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Section Headers
# ──────────────────────────────────────────────────────────────────────────────
def render_section_header(title: str, subtitle: str = None):
    """Renders a premium section header with gradient divider."""
    sub_html = f'<p class="ji-section-sub">{subtitle}</p>' if subtitle else ""
    render_html(f"""
    <div class="ji-section-header">
        <div class="ji-section-title">{title}</div>
        {sub_html}
    </div>
    <div class="ji-section-divider"></div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Insight Callout Boxes
# ──────────────────────────────────────────────────────────────────────────────
def render_insight_box(text: str, bold_prefix: str = "Key Insight:", border_color: str = "#818CF8"):
    """Renders a highlighted research insight callout box."""
    render_html(f"""
    <div class="ji-insight" style="border-left-color: {border_color};">
        <strong>{bold_prefix}</strong> {text}
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Glass Card Container
# ──────────────────────────────────────────────────────────────────────────────
def render_glass_card(content_html: str):
    """Renders arbitrary HTML inside a premium glass surface card."""
    render_html(f'<div class="ji-glass-card">{content_html}</div>')


# ──────────────────────────────────────────────────────────────────────────────
# Scientific Disclaimer
# ──────────────────────────────────────────────────────────────────────────────
def render_scientific_disclaimer(custom_text: str = None):
    """Renders the mandatory observational research disclaimer."""
    default_text = (
        "<strong>Methodological Notice:</strong> All reported salary figures and model predictions reflect "
        "<strong>observational labor market associations</strong> within the audited tech job corpus. "
        "Skill presence indicates market valuation correlation and does not imply causal wage enhancement."
    )
    msg = custom_text if custom_text else default_text
    render_html(f'<div class="ji-disclaimer">{msg}</div>')


# ──────────────────────────────────────────────────────────────────────────────
# Source Footer
# ──────────────────────────────────────────────────────────────────────────────
def render_source_footer(source_file: str, phase_tag: str, verified_date: str = "October 2026"):
    """Renders academic artifact provenance footer."""
    render_html(f"""
    <div class="ji-footer">
        <span>Source: <code>{source_file}</code> ({phase_tag})</span>
        <span>Frozen Results Registry · INT234 Predictive Analytics · {verified_date}</span>
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Horizontal Rule
# ──────────────────────────────────────────────────────────────────────────────
def render_hr():
    """Renders a premium gradient horizontal separator."""
    render_html('<div class="ji-hr"></div>')


# ──────────────────────────────────────────────────────────────────────────────
# Awaiting State Placeholder
# ──────────────────────────────────────────────────────────────────────────────
def render_awaiting_state(icon: str = "🎯", title: str = "Awaiting Input", subtitle: str = ""):
    """Renders a premium empty / awaiting state placeholder."""
    render_html(f"""
    <div class="ji-awaiting">
        <div class="ji-awaiting-icon">{icon}</div>
        <div class="ji-awaiting-title">{title}</div>
        <div class="ji-awaiting-sub">{subtitle}</div>
    </div>
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Archetype Badge Chip
# ──────────────────────────────────────────────────────────────────────────────
def render_archetype_badge(code: str, name: str, color: str) -> str:
    """Returns inline HTML for an archetype badge chip (use inside st.markdown)."""
    return (
        f'<span class="ji-arch-badge" '
        f'style="background: {color}22; border: 1px solid {color}55; color: {color};">'
        f'● {code}</span>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# Predictor Result Hero
# ──────────────────────────────────────────────────────────────────────────────
def render_prediction_hero(predicted_salary: float, baseline: float = 180413.0):
    """Renders the large prediction result hero card."""
    delta = predicted_salary - baseline
    delta_sign = "+" if delta >= 0 else ""
    delta_color = "#34D399" if delta >= 0 else "#F87171"
    render_html(f"""
    <div class="ji-pred-hero">
        <div class="ji-pred-label">Model-Estimated Salary Midpoint</div>
        <div class="ji-pred-value">${predicted_salary:,.0f}</div>
        <div class="ji-pred-delta" style="color: {delta_color};">
            {delta_sign}${abs(delta):,.0f} vs. cohort median (${baseline:,.0f})
        </div>
    </div>
    """)
