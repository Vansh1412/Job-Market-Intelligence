from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.backend.data_catalog.registry import get_source, get_sources
from src.backend.employers.registry import (
    EmployerRegistry,
    get_active_registry,
    get_employer,
    get_employers,
)
from src.backend.employers.resolver import EmployerEntityResolver
from src.backend.markets.registry import get_market, get_markets
from src.backend.schemas.data import DataSource
from src.backend.schemas.employer import (
    EmployerProfile,
    EmployerResolutionRequest,
    EmployerResolutionResponse,
)
from src.backend.schemas.market import MarketConfig


router = APIRouter(prefix="/v1", tags=["Global Intelligence Foundation"])


@router.get("/markets", response_model=list[MarketConfig])
def list_markets() -> list[MarketConfig]:
    return get_markets()


@router.get("/markets/{market_id}", response_model=MarketConfig)
def retrieve_market(market_id: str) -> MarketConfig:
    try:
        return get_market(market_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Market not found") from exc


@router.get("/sources", response_model=list[DataSource])
def list_sources() -> list[DataSource]:
    return get_sources()


@router.get("/sources/{source_id}", response_model=DataSource)
def retrieve_source(source_id: str) -> DataSource:
    try:
        return get_source(source_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Source not found") from exc


def get_current_registry() -> EmployerRegistry:
    return get_active_registry()


@router.get("/employers", response_model=list[EmployerProfile])
def list_employers(
    limit: Annotated[int | None, Query(ge=1, le=50, description="Maximum employers to return")] = None,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
    registry: Annotated[EmployerRegistry, Depends(get_current_registry)] = None,
) -> list[EmployerProfile]:
    active_reg = registry if registry is not None else get_current_registry()
    all_emp = active_reg.list()
    if limit is not None:
        return all_emp[offset : offset + limit]
    return all_emp


@router.post("/employers/resolve", response_model=EmployerResolutionResponse)
def resolve_employer_endpoint(
    request: EmployerResolutionRequest,
    registry: Annotated[EmployerRegistry, Depends(get_current_registry)] = None,
) -> EmployerResolutionResponse:
    active_reg = registry if registry is not None else get_current_registry()
    resolver = EmployerEntityResolver(registered_employers=active_reg.list())
    return resolver.resolve(request)


@router.get("/employers/{company_id}", response_model=EmployerProfile)
def retrieve_employer(
    company_id: str,
    registry: Annotated[EmployerRegistry, Depends(get_current_registry)] = None,
) -> EmployerProfile:
    active_reg = registry if registry is not None else get_current_registry()
    try:
        return active_reg.get(company_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Employer not found") from exc
