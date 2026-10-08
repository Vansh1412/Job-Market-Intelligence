"""
JobIntel Theme & Design System -- Phase 7.1 Premium Reconstruction
Glassmorphism | Atmospheric Gradients | Micro-animations | Executive Typography
"""

import streamlit as st
import plotly.graph_objects as go

# Color Design Tokens
COLOR_BG            = "#080C14"
COLOR_SURFACE_1     = "#0D1220"
COLOR_SURFACE_GLASS = "rgba(15, 21, 40, 0.72)"
COLOR_BORDER        = "rgba(99, 102, 241, 0.18)"
COLOR_BORDER_MUTED  = "rgba(148, 163, 184, 0.10)"

COLOR_TEXT_PRIMARY   = "#F1F5F9"
COLOR_TEXT_SECONDARY = "#94A3B8"
COLOR_TEXT_MUTED     = "#64748B"

COLOR_INDIGO  = "#818CF8"
COLOR_VIOLET  = "#A78BFA"
COLOR_CYAN    = "#22D3EE"
COLOR_EMERALD = "#34D399"
COLOR_AMBER   = "#FBBF24"
COLOR_CORAL   = "#F87171"
COLOR_PINK    = "#F472B6"
COLOR_BLUE    = "#60A5FA"
COLOR_PURPLE  = "#A855F7"

ARCHETYPE_COLORS = {
    "FOUND_TECH":  "#64748B",
    "DEVOPS_PLAT": "#22D3EE",
    "WEB_FRONT":   "#60A5FA",
    "CLOUD_ARCH":  "#FBBF24",
    "DATA_BI":     "#34D399",
    "AI_ML":       "#A78BFA",
    "SYS_ENG":     "#F472B6",
}

ARCHETYPE_GRAD = {
    "FOUND_TECH":  "linear-gradient(135deg, rgba(100,116,139,0.13), rgba(100,116,139,0.03))",
    "DEVOPS_PLAT": "linear-gradient(135deg, rgba(34,211,238,0.13), rgba(34,211,238,0.03))",
    "WEB_FRONT":   "linear-gradient(135deg, rgba(96,165,250,0.13), rgba(96,165,250,0.03))",
    "CLOUD_ARCH":  "linear-gradient(135deg, rgba(251,191,36,0.13), rgba(251,191,36,0.03))",
    "DATA_BI":     "linear-gradient(135deg, rgba(52,211,153,0.13), rgba(52,211,153,0.03))",
    "AI_ML":       "linear-gradient(135deg, rgba(167,139,250,0.13), rgba(167,139,250,0.03))",
    "SYS_ENG":     "linear-gradient(135deg, rgba(244,114,182,0.13), rgba(244,114,182,0.03))",
}


def apply_plotly_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    """Applies premium dark glassmorphic styling to all Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(13, 18, 32, 0.0)",
        plot_bgcolor="rgba(13, 18, 32, 0.0)",
        font=dict(
            family="Inter, Segoe UI, system-ui, -apple-system, sans-serif",
            color=COLOR_TEXT_SECONDARY,
            size=12,
        ),
        margin=dict(l=40, r=30, t=52, b=40),
        height=height,
        title_font=dict(size=14, color=COLOR_TEXT_PRIMARY),
        legend=dict(
            bgcolor="rgba(13,18,32,0.6)",
            bordercolor=COLOR_BORDER,
            borderwidth=1,
            font=dict(color=COLOR_TEXT_SECONDARY, size=11),
        ),
        hoverlabel=dict(
            bgcolor="#0D1220",
            font_size=12,
            font_color="#FFFFFF",
            bordercolor=COLOR_BORDER,
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(99,102,241,0.08)",
        zerolinecolor="rgba(99,102,241,0.15)",
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_SECONDARY, size=12),
        linecolor=COLOR_BORDER_MUTED,
    )
    fig.update_yaxes(
        gridcolor="rgba(99,102,241,0.08)",
        zerolinecolor="rgba(99,102,241,0.15)",
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_SECONDARY, size=12),
        linecolor=COLOR_BORDER_MUTED,
    )
    return fig


_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900'
    '&display=swap" rel="stylesheet">'
)

_CSS = """
<style>
*, *::before, *::after { font-family: Inter, Segoe UI, system-ui, -apple-system, sans-serif !important; }
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(99,102,241,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(34,211,238,0.07) 0%, transparent 55%),
        radial-gradient(ellipse 50% 30% at 50% 50%, rgba(167,139,250,0.04) 0%, transparent 70%),
        #080C14 !important;
}
[data-testid="stSidebar"] {
    background: rgba(9,13,22,0.96) !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebar"] > div { background: transparent !important; }
[data-testid="stSidebarNav"] a {
    color: #94A3B8 !important; border-radius: 8px !important;
    transition: all 0.18s ease !important; font-size: 0.875rem !important;
    font-weight: 500 !important; padding: 8px 12px !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(129,140,248,0.12) !important; color: #E2E8F0 !important;
}
[data-testid="stSidebarNav"] [aria-selected="true"] {
    background: rgba(129,140,248,0.18) !important; color: #818CF8 !important;
    border-left: 2px solid #818CF8 !important;
}
.block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 1260px !important; }
[data-testid="stDataFrame"] { border: 1px solid rgba(99,102,241,0.18) !important; border-radius: 10px !important; overflow: hidden !important; }
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px -4px rgba(99,102,241,0.45) !important; letter-spacing: -0.01em !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 28px -4px rgba(99,102,241,0.6) !important; }
.stButton > button:active { transform: translateY(0) !important; }
[data-baseweb="select"] > div {
    background: rgba(15,21,40,0.8) !important; border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 8px !important; color: #E2E8F0 !important;
}
[data-baseweb="select"] > div:hover { border-color: rgba(129,140,248,0.45) !important; }
[data-baseweb="tag"] { background: rgba(99,102,241,0.25) !important; border: 1px solid rgba(99,102,241,0.35) !important; border-radius: 6px !important; color: #A5B4FC !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(15,21,40,0.6) !important; border-radius: 10px !important; padding: 4px !important; border: 1px solid rgba(99,102,241,0.15) !important; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; color: #64748B !important; font-weight: 500 !important; transition: all 0.15s ease !important; }
.stTabs [aria-selected="true"] { background: rgba(99,102,241,0.25) !important; color: #818CF8 !important; }
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; backdrop-filter: blur(12px) !important; }
[data-testid="stCheckbox"] label { color: #94A3B8 !important; font-size: 0.9rem !important; font-weight: 500 !important; }
.js-plotly-plot { border-radius: 12px !important; overflow: hidden !important; }
.ji-hero {
    background: linear-gradient(135deg, rgba(129,140,248,0.12) 0%, rgba(167,139,250,0.06) 50%, rgba(34,211,238,0.05) 100%);
    border: 1px solid rgba(99,102,241,0.18); border-radius: 16px; padding: 28px 32px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.ji-hero::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(129,140,248,0.6), transparent); }
.ji-hero-badge { display: inline-flex; align-items: center; gap: 5px; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 12px; }
.ji-hero-title { font-size: 1.85rem; font-weight: 800; color: #F1F5F9; letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 6px 0; }
.ji-hero-subtitle { font-size: 0.97rem; color: #94A3B8; font-weight: 400; line-height: 1.55; max-width: 780px; margin: 0; }
.ji-kpi-card { background: rgba(15,21,40,0.72); border: 1px solid rgba(99,102,241,0.16); border-radius: 14px; padding: 18px 20px 16px 20px; margin-bottom: 14px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); transition: all 0.2s ease; position: relative; overflow: hidden; }
.ji-kpi-card::after { content: ''; position: absolute; bottom: 0; left: 20px; right: 20px; height: 1px; background: linear-gradient(90deg, transparent, rgba(129,140,248,0.2), transparent); }
.ji-kpi-card:hover { border-color: rgba(129,140,248,0.3); transform: translateY(-2px); box-shadow: 0 8px 28px -6px rgba(0,0,0,0.4); }
.ji-kpi-label { font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.ji-kpi-value { font-size: 1.9rem; font-weight: 800; color: #F1F5F9; letter-spacing: -0.04em; line-height: 1.05; }
.ji-kpi-sub { font-size: 0.78rem; color: #64748B; margin-top: 6px; font-weight: 400; }
.ji-kpi-delta-pos { font-size: 0.8rem; font-weight: 700; color: #34D399; margin-top: 4px; }
.ji-kpi-delta-neg { font-size: 0.8rem; font-weight: 700; color: #F87171; margin-top: 4px; }
.ji-kpi-accent-bar { position: absolute; top: 0; left: 0; width: 3px; height: 100%; border-radius: 14px 0 0 14px; }
.ji-section-header { margin: 28px 0 6px 0; }
.ji-section-title { font-size: 1.15rem; font-weight: 700; color: #E2E8F0; letter-spacing: -0.02em; margin: 0 0 4px 0; }
.ji-section-sub { font-size: 0.85rem; color: #64748B; font-weight: 400; margin: 0; }
.ji-section-divider { height: 1px; background: linear-gradient(90deg, rgba(99,102,241,0.3) 0%, transparent 80%); margin: 8px 0 18px 0; border: none; }
.ji-insight { background: rgba(99,102,241,0.07); border: 1px solid rgba(99,102,241,0.22); border-left: 3px solid #818CF8; border-radius: 0 10px 10px 0; padding: 13px 18px; margin: 10px 0 18px 0; font-size: 0.875rem; color: #CBD5E1; line-height: 1.6; }
.ji-insight strong { color: #F1F5F9; font-weight: 600; }
.ji-insight code { background: rgba(129,140,248,0.18); border-radius: 4px; padding: 1px 5px; font-size: 0.82rem; color: #A5B4FC; }
.ji-rq-card { background: rgba(15,21,40,0.72); border: 1px solid rgba(99,102,241,0.18); border-radius: 14px; padding: 22px; min-height: 220px; backdrop-filter: blur(12px); transition: all 0.2s ease; position: relative; overflow: hidden; }
.ji-rq-card:hover { transform: translateY(-3px); box-shadow: 0 16px 44px -8px rgba(0,0,0,0.5); }
.ji-rq-number { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
.ji-rq-title { font-size: 1rem; font-weight: 700; color: #F1F5F9; margin-bottom: 8px; }
.ji-rq-question { font-size: 0.82rem; color: #94A3B8; font-style: italic; line-height: 1.5; margin-bottom: 12px; }
.ji-rq-finding { font-size: 0.82rem; color: #CBD5E1; line-height: 1.55; }
.ji-rq-finding strong { color: #F1F5F9; }
.ji-rq-finding code { background: rgba(255,255,255,0.08); border-radius: 4px; padding: 1px 5px; font-size: 0.78rem; }
.ji-disclaimer { background: rgba(100,116,139,0.08); border: 1px solid rgba(100,116,139,0.2); border-radius: 10px; padding: 11px 16px; margin: 20px 0 10px 0; font-size: 0.8rem; color: #94A3B8; line-height: 1.55; }
.ji-disclaimer strong { color: #CBD5E1; }
.ji-footer { border-top: 1px solid rgba(99,102,241,0.12); padding-top: 12px; margin-top: 32px; font-size: 0.72rem; color: #475569; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.ji-footer code { color: #64748B; background: rgba(255,255,255,0.05); border-radius: 4px; padding: 1px 5px; font-size: 0.69rem; }
.ji-glass-card { background: rgba(15,21,40,0.72); border: 1px solid rgba(99,102,241,0.18); border-radius: 14px; padding: 20px 22px; margin-bottom: 14px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); transition: all 0.22s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden; }
.ji-glass-card:hover { border-color: rgba(129,140,248,0.35); background: rgba(20,28,52,0.78); transform: translateY(-2px); box-shadow: 0 12px 40px -8px rgba(0,0,0,0.5); }
.ji-arch-badge { display: inline-flex; align-items: center; gap: 5px; border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.ji-pred-hero { background: linear-gradient(135deg, rgba(99,102,241,0.18) 0%, rgba(99,102,241,0.06) 100%); border: 1px solid rgba(129,140,248,0.35); border-radius: 16px; padding: 28px 32px; text-align: center; position: relative; overflow: hidden; }
.ji-pred-hero::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(129,140,248,0.7), transparent); }
.ji-pred-label { font-size: 0.75rem; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.ji-pred-value { font-size: 3.2rem; font-weight: 900; color: #F1F5F9; letter-spacing: -0.05em; line-height: 1.0; }
.ji-pred-delta { font-size: 0.9rem; color: #94A3B8; margin-top: 6px; }
.ji-awaiting { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 40px; background: rgba(15,21,40,0.5); border: 1px dashed rgba(99,102,241,0.25); border-radius: 16px; text-align: center; }
.ji-awaiting-icon { font-size: 2.5rem; margin-bottom: 14px; }
.ji-awaiting-title { font-size: 1.05rem; font-weight: 600; color: #94A3B8; margin-bottom: 6px; }
.ji-awaiting-sub { font-size: 0.82rem; color: #475569; max-width: 380px; }
.ji-sidebar-brand { padding: 14px 4px 18px 4px; margin-bottom: 10px; }
.ji-sidebar-logo { font-size: 1.5rem; font-weight: 900; color: #F1F5F9; letter-spacing: -0.04em; }
.ji-sidebar-logo-dot { display: inline-block; width: 8px; height: 8px; background: linear-gradient(135deg, #818CF8, #22D3EE); border-radius: 50%; animation: pulse-dot 2s ease-in-out infinite; vertical-align: middle; margin-right: 6px; }
@keyframes pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(129,140,248,0.4); } 50% { opacity: 0.85; transform: scale(1.15); box-shadow: 0 0 0 4px rgba(129,140,248,0); } }
.ji-sidebar-tagline { font-size: 0.72rem; font-weight: 600; color: #818CF8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 3px; }
.ji-sidebar-meta { font-size: 0.7rem; color: #475569; margin-top: 5px; }
.ji-sidebar-divider { height: 1px; background: linear-gradient(90deg, rgba(99,102,241,0.3) 0%, transparent 100%); margin: 14px 0; }
.ji-sidebar-footer { margin-top: 30px; padding-top: 14px; border-top: 1px solid rgba(99,102,241,0.12); font-size: 0.7rem; color: #475569; line-height: 1.7; }
.ji-sidebar-footer strong { color: #64748B; }
.ji-hr { height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.2) 20%, rgba(99,102,241,0.2) 80%, transparent); border: none; margin: 24px 0; }
.ji-stat-val { font-size: 1.3rem; font-weight: 700; color: #F1F5F9; letter-spacing: -0.03em; }
.ji-stat-unit { font-size: 0.75rem; color: #64748B; }
</style>
"""


def inject_custom_css():
    """Injects the complete Phase 7.1 premium design system CSS."""
    st.markdown(_FONTS_LINK + _CSS, unsafe_allow_html=True)
