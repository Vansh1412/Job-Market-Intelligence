from fastapi import APIRouter, HTTPException

from src.backend.data_catalog.registry import get_source, get_sources
from src.backend.employers.registry import get_employer, get_employers
from src.backend.markets.registry import get_market, get_markets
from src.backend.schemas.data import DataSource
from src.backend.schemas.employer import EmployerProfile
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


@router.get("/employers", response_model=list[EmployerProfile])
def list_employers() -> list[EmployerProfile]:
    return get_employers()


@router.get("/employers/{company_id}", response_model=EmployerProfile)
def retrieve_employer(company_id: str) -> EmployerProfile:
    try:
        return get_employer(company_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Employer not found") from exc
