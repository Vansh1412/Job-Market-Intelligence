"""Patch model_eval, error_analysis, and methodology pages with premium headers."""

COMPONENT_IMPORT_OLD = """from src.dashboard.ui_components import (
    render_kpi_card,
    render_insight_box,
    render_scientific_disclaimer,
    render_source_footer,
    render_section_header,
)"""

COMPONENT_IMPORT_NEW = """from src.dashboard.ui_components import (
    render_page_hero,
    render_kpi_card,
    render_insight_box,
    render_scientific_disclaimer,
    render_source_footer,
    render_section_header,
    render_hr,
)"""

patches = [
    (
        "e:/Job Market/src/dashboard/model_eval.py",
        '    st.markdown("# \U0001f4ca Model Performance & Evaluation")\n'
        '    st.markdown(\n'
        "        \"<p class='page-subtitle'>Rigorous benchmark evaluation of 5 supervised regression algorithms, \"\n"
        '        "3 feature set architectures, and holdout generalization diagnostics (80/20 train/test split).</p>",\n'
        '        unsafe_allow_html=True,\n'
        '    )',
        "    render_page_hero(\n"
        "        icon='\U0001f4ca',\n"
        "        title='Model Performance & Evaluation',\n"
        "        subtitle='Rigorous benchmark evaluation of 5 supervised regression algorithms, 3 feature set architectures, and holdout generalization diagnostics (80/20 train/test split).',\n"
        "        badge_text='Phase 5 \u00b7 XGBoost Champion \u00b7 Frozen Results',\n"
        "    )",
    ),
]

# Read error_analysis and methodology to get exact headers
with open("e:/Job Market/src/dashboard/error_analysis.py", "r", encoding="utf-8") as f:
    ea = f.read()

with open("e:/Job Market/src/dashboard/methodology.py", "r", encoding="utf-8") as f:
    meth = f.read()

print("error_analysis headers:")
for line in ea.split("\n")[33:45]:
    print(repr(line))

print("methodology headers:")
for line in meth.split("\n")[33:50]:
    print(repr(line))
