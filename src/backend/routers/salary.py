"""
Salary Intelligence API Router — Role, Seniority, and Location Disaggregations
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from src.backend.data_service import (
    get_salary_summary_df,
    get_salary_by_role_df,
    get_salary_by_seniority_df,
    get_salary_by_location_df,
)
from src.backend.schemas.salary import (
    CrossMarketSalaryComparisonResult,
    OccupationSalaryProfile,
    PppFxRatesPayload,
    SalarySourceMeta,
)
from src.backend.services.salary_service import get_salary_service

router = APIRouter(prefix="/salary", tags=["Salary Intelligence"])


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


# =====================================================================
# Cross-Market Descriptive Salary Intelligence API (Sprint 3B.1)
# =====================================================================

v1_salary_router = APIRouter(prefix="/v1/salary", tags=["Cross-Market Salary Intelligence"])


@v1_salary_router.get("/sources", response_model=list[SalarySourceMeta])
def list_salary_sources(
    active_only: bool = Query(True, description="Filter for active official sources only"),
    service=Depends(get_salary_service),
):
    """List all official and benchmark salary data sources across the 5 markets."""
    return service.list_sources(active_only=active_only)


@v1_salary_router.get("/sources/{source_id}", response_model=SalarySourceMeta)
def get_salary_source(
    source_id: str,
    service=Depends(get_salary_service),
):
    """Retrieve metadata and licensing for a specific salary data source."""
    src = service.get_source(source_id)
    if not src:
        raise HTTPException(status_code=404, detail=f"Salary source '{source_id}' not found.")
    return src


@v1_salary_router.get("/rates", response_model=PppFxRatesPayload)
def get_ppp_and_fx_rates(
    service=Depends(get_salary_service),
):
    """Retrieve authoritative FX rates and World Bank ICP 2024 PPP conversion factors."""
    return service.get_ppp_fx_rates()


@v1_salary_router.get("/observations", response_model=list[OccupationSalaryProfile])
def list_salary_observations(
    market_id: str | None = Query(None, description="Optional market filter: US, UK, AU, SG, IN"),
    service=Depends(get_salary_service),
):
    """List salary observations for national occupations across markets."""
    return service.list_observations(market_id=market_id)


@v1_salary_router.get("/occupations/{occupation_id}", response_model=OccupationSalaryProfile)
def get_occupation_salary_profile(
    occupation_id: str,
    service=Depends(get_salary_service),
):
    """Retrieve the salary observation profile (percentiles and conversions) for an occupation.
    
    Fails closed with HTTP 503 if UK ASHE publication gate is active.
    """
    profile = service.get_salary_profile_for_occupation(occupation_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"No salary observation available for occupation '{occupation_id}'.",
        )
    return profile


@v1_salary_router.get("/compare", response_model=CrossMarketSalaryComparisonResult)
def compare_cross_market_salaries(
    occupation_id: str = Query(..., description="Source occupation ID (e.g. US_SOC_2018:15-1252)"),
    service=Depends(get_salary_service),
):
    """Perform source-backed cross-market descriptive salary comparison.
    
    Returns side-by-side nominal USD, PPP USD, percentile distributions,
    and automated comparability evaluations across the 11 methodological dimensions.
    Fails closed with HTTP 503 if source occupation is UK and publication gate is active.
    """
    return service.compare_occupation_salaries(occupation_id)


@v1_salary_router.get("/convert")
def convert_salary_amount(
    amount: float = Query(..., gt=0, description="Salary amount to convert"),
    from_currency: str = Query(..., description="Currency code: USD, GBP, AUD, SGD, INR"),
    service=Depends(get_salary_service),
):
    """Convert an amount to both Nominal USD and PPP USD with explicit methodology citations."""
    try:
        return service.convert_amount(amount, from_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

