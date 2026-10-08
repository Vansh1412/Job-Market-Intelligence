"""
Skill Explorer API Router — Frequencies, Valuations, Landscape Bubbles, and Co-occurrence
"""

from fastapi import APIRouter, Query
from src.backend.data_service import (
    get_skill_frequency_df,
    get_skill_salary_association_df,
    get_skill_cooccurrence_df,
)

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
        return {"error": f"Skill '{skill_name}' not found in Taxonomy D"}

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

    # Find top companion skills from cooccurrence if present
    companions = []
    if "Skill" in df_co.columns:
        match_co = df_co[df_co["Skill"].str.lower() == clean_search]
        if len(match_co) > 0:
            row_dict = match_co.iloc[0].drop("Skill").to_dict()
            sorted_comp = sorted(row_dict.items(), key=lambda x: x[1], reverse=True)
            companions = [{"skill": k, "cooccurrences": v} for k, v in sorted_comp[:6] if k.lower() != clean_search]

    return {
        "skill": skill_name,
        "category": cat,
        "color": CATEGORY_COLORS.get(cat, "#64748B"),
        "postings": postings,
        "prevalence_pct": round(prev, 2),
        "median_salary": med_sal,
        "delta_vs_cohort": med_sal - 180413.0,
        "companions": companions,
    }
