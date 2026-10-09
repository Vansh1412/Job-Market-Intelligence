"""
Skill Explorer API Router — Frequencies, Valuations, Landscape Bubbles, and Co-occurrence
"""

from fastapi import APIRouter, Query, HTTPException
from src.backend.data_service import (
    get_skill_frequency_df,
    get_skill_salary_association_df,
    get_skill_cooccurrence_df,
    get_cluster_skill_lift_df,
)
from src.backend.services.market_service import MarketService

router = APIRouter(prefix="/api/skills", tags=["Skills"])

# Skill category mappings for rich visualization
SKILL_CATEGORIES = {
    "AI / Machine Learning": ["python", "pytorch", "tensorflow", "machine_learning", "deep_learning", "nlp", "computer_vision", "keras", "scikit_learn", "huggingface", "llm"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci_cd", "ansible", "linux", "cloud", "devops", "jenkins", "helm", "serverless"],
    "Data & Analytics": ["sql", "spark", "hadoop", "pandas", "numpy", "tableau", "power_bi", "snowflake", "bigquery", "databricks", "kafka", "etl", "data_warehousing"],
    "Web & Frontend": ["javascript", "typescript", "react", "node", "angular", "vue", "html", "css", "next_js", "tailwind", "graphql", "rest_api"],
    "Systems & Backend": ["c", "c++", "c#", "java", "go", "rust", "scala", "ruby", "php", "swift", "kotlin", "embedded", "distributed_systems"],
}


def categorize_skill(skill_name: str) -> str:
    cleaned = skill_name.lower().replace(" ", "_").replace("-", "_").replace(".", "_")
    for category, skills in SKILL_CATEGORIES.items():
        if any(s in cleaned for s in skills):
            return category
    return "Other Technical"


CATEGORY_COLORS = {
    "AI / Machine Learning": "#8B5CF6",
    "Cloud & DevOps": "#06B6D4",
    "Data & Analytics": "#F59E0B",
    "Web & Frontend": "#EC4899",
    "Systems & Backend": "#10B981",
    "Other Technical": "#64748B",
}


@router.get("/frequency")
def get_skill_frequency():
    df = get_skill_frequency_df().copy()
    if "Corpus_Count" in df.columns:
        df["Postings"] = df["Corpus_Count"]
    elif "Modeling_Count" in df.columns:
        df["Postings"] = df["Modeling_Count"]
    if "Corpus_Prevalence" in df.columns:
        df["Prevalence_Pct"] = (df["Corpus_Prevalence"] * 100).round(2)
    elif "Modeling_Prevalence" in df.columns:
        df["Prevalence_Pct"] = (df["Modeling_Prevalence"] * 100).round(2)
    if "Postings" in df.columns:
        df = df.sort_values(by="Postings", ascending=False)
    records = df.to_dict(orient="records")
    for r in records:
        skill_name = r.get("Skill", "")
        cat = categorize_skill(skill_name)
        r["Category"] = cat
        r["Color"] = CATEGORY_COLORS.get(cat, "#64748B")
    return records


@router.get("/salary-association")
def get_skill_salary_association():
    df = get_skill_salary_association_df().copy()
    if "Support_N" in df.columns and "Postings" not in df.columns:
        df["Postings"] = df["Support_N"]
    if "Prevalence" in df.columns and "Prevalence_Pct" not in df.columns:
        df["Prevalence_Pct"] = (df["Prevalence"] * 100).round(2)
    if "Median_Salary" in df.columns:
        df = df.sort_values(by="Median_Salary", ascending=False)
    records = df.to_dict(orient="records")
    for r in records:
        skill_name = r.get("Skill", "")
        cat = categorize_skill(skill_name)
        r["Category"] = cat
        r["Color"] = CATEGORY_COLORS.get(cat, "#64748B")
    return records


@router.get("/landscape")
def get_skill_landscape():
    """
    Merges frequency and salary association for the interactive 2D bubble chart.
    X-axis: Market Prevalence (%)
    Y-axis: Observed Median Salary ($)
    Z-axis (Size): Total Postings
    Color: Category
    """
    df_freq = get_skill_frequency_df().copy()
    df_sal = get_skill_salary_association_df().copy()

    # Normalize skill names
    df_freq["clean_name"] = df_freq["Skill"].astype(str).str.lower().str.strip()
    df_sal["clean_name"] = df_sal["Skill"].astype(str).str.lower().str.strip()

    merged = df_freq.merge(df_sal, on="clean_name", suffixes=("_freq", "_sal"))
    landscape = []

    for _, row in merged.iterrows():
        skill_name = str(row.get("Skill_freq", row["clean_name"]))
        cat = categorize_skill(skill_name)
        
        postings = int(row.get("Corpus_Count", row.get("Modeling_Count", row.get("Support_N", 100))))
        raw_prev = float(row.get("Corpus_Prevalence", row.get("Modeling_Prevalence", row.get("Prevalence", 0.05))))
        prevalence = raw_prev * 100 if raw_prev <= 1.0 else raw_prev
        salary = float(row.get("Median_Salary", 180000.0))

        landscape.append({
            "skill": skill_name,
            "category": cat,
            "color": CATEGORY_COLORS.get(cat, "#64748B"),
            "prevalence_pct": round(prevalence, 2),
            "median_salary": round(salary, 0),
            "postings": postings,
            "delta_vs_median": round(salary - 180413.0, 0),
        })

    return landscape


@router.get("/cooccurrence")
def get_skill_cooccurrence():
    df = get_skill_cooccurrence_df()
    skills = df.columns.tolist()
    if "Skill" in skills:
        skills.remove("Skill")
    matrix = df.to_dict(orient="records")
    return {"skills": skills, "matrix": matrix}


@router.get("/detail/{skill_name}")
def get_skill_detail(skill_name: str):
    df_freq = get_skill_frequency_df()
    df_sal = get_skill_salary_association_df()
    df_co = get_skill_cooccurrence_df()

    clean_search = skill_name.lower().strip()
    row_freq = df_freq[df_freq["Skill"].str.lower() == clean_search]
    row_sal = df_sal[df_sal["Skill"].str.lower() == clean_search]

    if len(row_freq) == 0 and len(row_sal) == 0:
        alt_search = clean_search.replace("_", "-") if "_" in clean_search else clean_search.replace("-", "_")
        row_freq = df_freq[df_freq["Skill"].str.lower() == alt_search]
        row_sal = df_sal[df_sal["Skill"].str.lower() == alt_search]

    if len(row_freq) == 0 and len(row_sal) == 0:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found in Taxonomy D")

    postings = 0
    if len(row_freq) > 0:
        if "Corpus_Count" in row_freq.columns:
            postings = int(row_freq["Corpus_Count"].values[0])
        elif "Modeling_Count" in row_freq.columns:
            postings = int(row_freq["Modeling_Count"].values[0])
    elif len(row_sal) > 0 and "Support_N" in row_sal.columns:
        postings = int(row_sal["Support_N"].values[0])

    prev = 0.0
    if len(row_freq) > 0:
        if "Corpus_Prevalence" in row_freq.columns:
            prev = float(row_freq["Corpus_Prevalence"].values[0]) * 100
        elif "Modeling_Prevalence" in row_freq.columns:
            prev = float(row_freq["Modeling_Prevalence"].values[0]) * 100
    elif len(row_sal) > 0 and "Prevalence" in row_sal.columns:
        prev = float(row_sal["Prevalence"].values[0]) * 100

    med_sal = float(row_sal["Median_Salary"].values[0]) if len(row_sal) > 0 and "Median_Salary" in row_sal.columns else 180413.0
    cat = categorize_skill(skill_name)

    # Discover associated roles from USA cohort
    roles = []
    cohort_df = MarketService.get_usa_cohort_df()
    target_skill_col = f"skill_{clean_search.replace(' ', '_').replace('-', '_')}"
    if target_skill_col not in cohort_df.columns:
        for col in cohort_df.columns:
            if col.startswith("skill_") and col.replace("skill_", "").lower() == clean_search.replace(" ", "_"):
                target_skill_col = col
                break

    if target_skill_col in cohort_df.columns:
        matched_cohort = cohort_df[cohort_df[target_skill_col] == 1]
        if len(matched_cohort) > 0:
            roles = matched_cohort["role_family"].value_counts().head(4).index.tolist()

    # Discover associated archetypes from Phase 4.1 lift table
    archetypes = []
    df_lift = get_cluster_skill_lift_df()
    arch_labels = {
        "Cluster_0_FOUND_TECH": "Foundational Tech",
        "Cluster_1_DEVOPS_PLAT": "DevOps & Platform",
        "Cluster_2_WEB_FRONT": "Frontend & Web",
        "Cluster_3_CLOUD_ARCH": "Cloud Architecture",
        "Cluster_4_DATA_BI": "Data & BI",
        "Cluster_5_AI_ML": "AI / ML & LLMs",
        "Cluster_6_SYS_ENG": "Systems & Infrastructure",
    }
    match_lift = df_lift[df_lift["Skill"].str.lower() == target_skill_col.lower()]
    if len(match_lift) == 0:
        match_lift = df_lift[df_lift["Skill"].str.lower().str.replace("skill_", "") == clean_search.replace(" ", "_")]
    if len(match_lift) > 0:
        row = match_lift.iloc[0]
        arch_scores = [(arch_labels.get(col, col), float(row[col])) for col in arch_labels if col in row and float(row[col]) > 1.0]
        arch_scores = sorted(arch_scores, key=lambda x: x[1], reverse=True)
        archetypes = [a[0] for a in arch_scores[:3]]

    # Find top companion skills from cooccurrence if present
    companions = []
    combos = []
    if "Skill" in df_co.columns:
        match_co = df_co[df_co["Skill"].str.lower() == clean_search]
        if len(match_co) == 0:
            alt_search = clean_search.replace("_", "-") if "_" in clean_search else clean_search.replace("-", "_")
            match_co = df_co[df_co["Skill"].str.lower() == alt_search]
        if len(match_co) > 0:
            row_dict = match_co.iloc[0].drop("Skill").to_dict()
            sorted_comp = sorted(row_dict.items(), key=lambda x: x[1], reverse=True)
            companions = [{"skill": k, "cooccurrences": v} for k, v in sorted_comp[:6] if k.lower() != clean_search]
            combos = [k for k, _ in sorted_comp[:6] if k.lower() != clean_search]

    delta = med_sal - 180413.0
    return {
        "skill": skill_name,
        "category": cat,
        "color": CATEGORY_COLORS.get(cat, "#64748B"),
        "postings": postings,
        "prevalence_pct": round(prev, 2),
        "median_salary": round(med_sal, 2),
        "delta_vs_cohort": round(delta, 2),
        "roles": roles,
        "archetypes": archetypes,
        "companions": companions,
        "combos": combos,
        # Explicit backward compatibility aliases for existing frontend contracts
        "median_with": round(med_sal, 2),
        "prevalence": round(prev, 2),
        "delta": round(delta, 2),
        "associated_roles": roles,
        "associated_archetypes": archetypes,
        "cooccurring_skills": combos,
    }
