from src.backend.schemas.market import (
    CapabilityStatus,
    CurrencyCode,
    MarketCapability,
    MarketConfig,
    MarketId,
)


def _capabilities(
    salary_prediction: CapabilityStatus,
    salary_analytics: CapabilityStatus,
    skills_analytics: CapabilityStatus,
    demand_analytics: CapabilityStatus,
    occupation_mapping: CapabilityStatus = CapabilityStatus.NOT_IMPLEMENTED,
    employer_intelligence: CapabilityStatus = CapabilityStatus.NOT_IMPLEMENTED,
) -> dict[MarketCapability, CapabilityStatus]:
    return {
        MarketCapability.SALARY_PREDICTION: salary_prediction,
        MarketCapability.SALARY_ANALYTICS: salary_analytics,
        MarketCapability.SKILLS_ANALYTICS: skills_analytics,
        MarketCapability.DEMAND_ANALYTICS: demand_analytics,
        MarketCapability.OCCUPATION_MAPPING: occupation_mapping,
        MarketCapability.EMPLOYER_INTELLIGENCE: employer_intelligence,
    }


_AVAILABLE = CapabilityStatus.AVAILABLE
_PARTIAL = CapabilityStatus.PARTIAL
_NOT_IMPLEMENTED = CapabilityStatus.NOT_IMPLEMENTED

_MARKETS = (
    MarketConfig(
        market_id=MarketId.IN,
        display_name="India",
        iso_country_code="IN",
        primary_currency=CurrencyCode.INR,
        salary_reporting_convention="Existing salary prediction is displayed in INR Lakhs Per Annum; source definitions remain market-specific.",
        occupational_classification="JobIntel India role families; no national occupational crosswalk is integrated.",
        capabilities=_capabilities(_AVAILABLE, _AVAILABLE, _AVAILABLE, _PARTIAL),
        data_availability=_AVAILABLE,
        source_ids=("in.jobintel.market-data",),
    ),
    MarketConfig(
        market_id=MarketId.US,
        display_name="United States",
        iso_country_code="US",
        primary_currency=CurrencyCode.USD,
        salary_reporting_convention="Existing salary prediction is annual base USD; current comparisons do not convert currency.",
        occupational_classification="JobIntel USA role families; no national occupational crosswalk is integrated.",
        capabilities=_capabilities(_AVAILABLE, _AVAILABLE, _AVAILABLE, _PARTIAL),
        data_availability=_AVAILABLE,
        source_ids=("us.jobintel.market-data",),
    ),
    MarketConfig(
        market_id=MarketId.UK,
        display_name="United Kingdom",
        iso_country_code="GB",
        primary_currency=CurrencyCode.GBP,
        salary_reporting_convention="Preserve source gross/basic definition and hourly, weekly, or annual period; no automatic annualization.",
        occupational_classification="UK Standard Occupational Classification",
        occupational_classification_version="SOC 2020",
        capabilities=_capabilities(*((_NOT_IMPLEMENTED,) * 4)),
        data_availability=_NOT_IMPLEMENTED,
        source_ids=("uk.ons.ashe", "uk.ons.labour-demand", "uk.ons.soc2020"),
    ),
    MarketConfig(
        market_id=MarketId.AU,
        display_name="Australia",
        iso_country_code="AU",
        primary_currency=CurrencyCode.AUD,
        salary_reporting_convention="Preserve source weekly/hourly earnings and population; no automatic annualization.",
        occupational_classification="Occupation Standard Classification for Australia",
        occupational_classification_version="OSCA 2024",
        capabilities=_capabilities(*((_NOT_IMPLEMENTED,) * 4)),
        data_availability=_NOT_IMPLEMENTED,
        source_ids=("au.abs.eeh", "au.abs.osca", "au.jsa.ivi"),
    ),
    MarketConfig(
        market_id=MarketId.SG,
        display_name="Singapore",
        iso_country_code="SG",
        primary_currency=CurrencyCode.SGD,
        salary_reporting_convention="Preserve basic or gross monthly wage definition and resident full-time population; no annualization.",
        occupational_classification="Singapore Standard Occupational Classification",
        occupational_classification_version="SSOC 2024",
        capabilities=_capabilities(*((_NOT_IMPLEMENTED,) * 4)),
        data_availability=_NOT_IMPLEMENTED,
        source_ids=("sg.mom.ows", "sg.mom.vacancies", "sg.singstat.ssoc2024"),
    ),
)


class MarketRegistry:
    def __init__(self, markets: tuple[MarketConfig, ...] = _MARKETS) -> None:
        market_map = {market.market_id: market for market in markets}
        if len(market_map) != len(markets):
            raise ValueError("market identifiers must be unique")
        self._markets = market_map

    def list(self) -> list[MarketConfig]:
        return list(self._markets.values())

    def get(self, market_id: str | MarketId) -> MarketConfig:
        try:
            key = market_id if isinstance(market_id, MarketId) else MarketId(market_id)
            return self._markets[key]
        except (ValueError, KeyError) as exc:
            raise KeyError("market not found") from exc


_registry = MarketRegistry()


def get_markets() -> list[MarketConfig]:
    return _registry.list()


def get_market(market_id: str | MarketId) -> MarketConfig:
    return _registry.get(market_id)
