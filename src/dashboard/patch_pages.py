"""Patch remaining dashboard pages with premium hero headers."""
import re

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

patches = {
    "e:/Job Market/src/dashboard/salary_intel.py": {
        "old_header": (
            '    st.markdown("# \U0001f4b0 Salary Intelligence")\n'
            '    st.markdown(\n'
            "        \"<p class='page-subtitle'>Empirical analysis of compensation distributions, seniority gradients, \"\n"
            '        "and geographical salary differentials across 34,036 technology postings with verified USD midpoints.</p>",\n'
            '        unsafe_allow_html=True,\n'
            '    )'
        ),
        "new_header": (
            "    render_page_hero(\n"
            "        icon='\U0001f4b0',\n"
            "        title='Salary Intelligence',\n"
            "        subtitle=(\n"
            "            'Empirical analysis of compensation distributions, seniority gradients, '\n"
            "            'and geographical salary differentials across 34,036 technology postings with verified USD midpoints.'\n"
            "        ),\n"
            "        badge_text='Phase 3 EDA \u00b7 34,036 Postings \u00b7 Frozen Results',\n"
            "    )"
        ),
    },
    "e:/Job Market/src/dashboard/skill_explorer.py": {
        "old_header": (
            '    st.markdown("# \U0001f6e0\ufe0f Skill Explorer")\n'
            '    st.markdown(\n'
            "        \"<p class='page-subtitle'>Inspect the market footprint, observed salary associations, \"\n"
            '        "and companion technologies across 82 standardized technical skills in Taxonomy D.</p>",\n'
            '        unsafe_allow_html=True,\n'
            '    )'
        ),
        "new_header": (
            "    render_page_hero(\n"
            "        icon='\U0001f6e0\ufe0f',\n"
            "        title='Skill Explorer',\n"
            "        subtitle='Inspect the market footprint, observed salary associations, and companion technologies across 82 standardized technical skills in Taxonomy D.',\n"
            "        badge_text='Phase 3 EDA | 82 Skills | Taxonomy D',\n"
            "    )"
        ),
    },
    "e:/Job Market/src/dashboard/archetypes.py": {
        "old_header": (
            '    st.markdown("# \U0001f9ec Archetype Explorer")\n'
            '    st.markdown(\n'
            "        \"<p class='page-subtitle'>Discovery and structural profiling of seven recurring skill-based job archetypes \"\n"
            '        "identified via Centered Covariance PCA (15 PCs) and K-Means clustering (k=7) on 116,830 skill-bearing postings.</p>",\n'
            '        unsafe_allow_html=True,\n'
            '    )'
        ),
        "new_header": (
            "    render_page_hero(\n"
            "        icon='\U0001f9ec',\n"
            "        title='Archetype Explorer',\n"
            "        subtitle='Discovery and structural profiling of seven recurring skill-based job archetypes identified via Centered Covariance PCA (15 PCs) and K-Means clustering (k=7) on 116,830 skill-bearing postings.',\n"
            "        badge_text='Phase 4.1 \u00b7 k=7 \u00b7 Mean ARI 0.7901',\n"
            "    )"
        ),
    },
}

for filepath, info in patches.items():
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace imports
    if COMPONENT_IMPORT_OLD in content:
        content = content.replace(COMPONENT_IMPORT_OLD, COMPONENT_IMPORT_NEW)

    # Replace old header
    if info["old_header"] in content:
        content = content.replace(info["old_header"], info["new_header"])
    else:
        print(f"WARNING: Header not found in {filepath}")

    # Replace st.markdown("---") with render_hr()
    content = content.replace('    st.markdown("---")', "    render_hr()")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched: {filepath}")

print("All patches applied.")
