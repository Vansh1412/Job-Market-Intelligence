"""
Salary Intelligence API Router — Role, Seniority, and Location Disaggregations
"""

from fastapi import APIRouter, Query
from src.backend.data_service import (
    get_salary_summary_df,
    get_salary_by_role_df,
    get_salary_by_seniority_df,
    get_salary_by_location_df,
)

router = APIRouter(prefix="/api/salary", tags=["Salary Intelligence"])


@router.get("/summary")
def get_salary_summary():
    df = get_salary_summary_df()
    return df.to_dict(orient="records")


@router.get("/by-role")
def get_salary_by_role():
    df = get_salary_by_role_df().copy()
    if "N" in df.columns and "Postings" not in df.columns:
        df["Postings"] = df["N"]
    if "Role_Family" in df.columns:
        df = df.sort_values(by="Median_Salary", ascending=False)
    return df.to_dict(orient="records")


@router.get("/by-seniority")
def get_salary_by_seniority():
    tier_order = ["Entry-level", "Mid-level", "Senior", "Lead / Principal", "Executive / Director"]
    df = get_salary_by_seniority_df().copy()
    if "N" in df.columns and "Postings" not in df.columns:
        df["Postings"] = df["N"]
    if "Seniority" in df.columns:
        df["order"] = df["Seniority"].map(lambda x: tier_order.index(x) if x in tier_order else 99)
        df = df.sort_values(by="order").drop(columns=["order"])
    return df.to_dict(orient="records")


@router.get("/by-location")
def get_salary_by_location():
    df = get_salary_by_location_df().copy()
    if "N" in df.columns and "Postings" not in df.columns:
        df["Postings"] = df["N"]
    if "Median_Salary" in df.columns:
        df = df.sort_values(by="Median_Salary", ascending=False)
    return df.to_dict(orient="records")


@router.get("/comparator")
def get_comparator(
    role: str = Query("ML / AI Engineer"),
    seniority: str = Query("Senior"),
    city: str = Query("San Francisco"),
):
    df_roles = get_salary_by_role_df()
    df_sen = get_salary_by_seniority_df()
    df_loc = get_salary_by_location_df()

    role_row = df_roles[df_roles["Role_Family"] == role]
    role_med = float(role_row["Median_Salary"].values[0]) if len(role_row) > 0 else 180413.0

    sen_row = df_sen[df_sen["Seniority"] == seniority]
    sen_med = float(sen_row["Median_Salary"].values[0]) if len(sen_row) > 0 else 180413.0

    loc_row = df_loc[df_loc["City"] == city]
    loc_med = float(loc_row["Median_Salary"].values[0]) if len(loc_row) > 0 else 180413.0

    benchmark = 180413.0
    return {
        "benchmark": benchmark,
        "role": {
            "name": role,
            "median": role_med,
            "delta_vs_benchmark": role_med - benchmark,
            "pct_vs_benchmark": round(((role_med - benchmark) / benchmark) * 100, 1),
        },
        "seniority": {
            "name": seniority,
            "median": sen_med,
            "delta_vs_benchmark": sen_med - benchmark,
            "pct_vs_benchmark": round(((sen_med - benchmark) / benchmark) * 100, 1),
        },
        "location": {
            "name": city,
            "median": loc_med,
            "delta_vs_benchmark": loc_med - benchmark,
            "pct_vs_benchmark": round(((loc_med - benchmark) / benchmark) * 100, 1),
        },
    }
