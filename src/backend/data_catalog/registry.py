from pydantic import AnyHttpUrl

from src.backend.schemas.data import (
    DataSource,
    ReuseReviewStatus,
    SourceCategory,
    ValidationStatus,
)


_REVIEW_REQUIRED = ReuseReviewStatus.REVIEW_REQUIRED
_NOT_COLLECTED = ValidationStatus.NOT_COLLECTED

_SOURCES = (
    DataSource(
        source_id="in.jobintel.market-data",
        source_name="JobIntel India market data",
        source_organization="JobIntel",
        source_reference=AnyHttpUrl("https://github.com/Vansh1412/Job-Market-Intelligence"),
        source_category=SourceCategory.EXISTING_PROJECT_DATA,
        reuse_review_status=ReuseReviewStatus.UNKNOWN,
        dataset_description="Existing India salary prediction and market analytics source family. No row-level dataset is exposed by this catalog.",
        geographic_coverage=("India",),
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="us.jobintel.market-data",
        source_name="JobIntel United States market data",
        source_organization="JobIntel",
        source_reference=AnyHttpUrl("https://github.com/Vansh1412/Job-Market-Intelligence"),
        source_category=SourceCategory.EXISTING_PROJECT_DATA,
        reuse_review_status=ReuseReviewStatus.UNKNOWN,
        dataset_description="Existing United States salary prediction and market analytics source family. No row-level dataset is exposed by this catalog.",
        geographic_coverage=("United States",),
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="au.abs.eeh",
        source_name="Employee Earnings and Hours, Australia",
        source_organization="Australian Bureau of Statistics",
        source_reference=AnyHttpUrl("https://www.abs.gov.au/statistics/labour/earnings-and-working-conditions/employee-earnings-and-hours-australia/latest-release"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Official aggregate earnings and hours tables with occupation and geographic dimensions. No data has been collected into JobIntel.",
        geographic_coverage=("Australia", "States and territories"),
        update_frequency="Periodic survey release",
        reference_period="2025-05",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="au.abs.osca",
        source_name="Occupation Standard Classification for Australia",
        source_organization="Australian Bureau of Statistics",
        source_reference=AnyHttpUrl("https://www.abs.gov.au/about/key-priorities/about-osca/osca-2024"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="OSCA 2024 occupation classification and correspondence resources. Classification metadata only; no JobIntel crosswalk is implemented.",
        geographic_coverage=("Australia",),
        reference_period="2024",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="au.jsa.ivi",
        source_name="Internet Vacancy Index",
        source_organization="Jobs and Skills Australia",
        source_reference=AnyHttpUrl("https://www.jobsandskills.gov.au/data/internet-vacancy-index/methodology"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Monthly online job advertisement series from contributing boards, with occupational and regional breakdowns. Not all vacancies or salary data.",
        geographic_coverage=("Australia", "States and territories", "Selected regions"),
        update_frequency="Monthly",
        reference_period="2026-09",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="uk.ons.ashe",
        source_name="Annual Survey of Hours and Earnings",
        source_organization="Office for National Statistics",
        source_reference=AnyHttpUrl("https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsocashetable15"),
        canonical_publication_url=AnyHttpUrl("https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsocashetable15"),
        acquisition_url=AnyHttpUrl("https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsocashetable15"),
        artifact_download_url=AnyHttpUrl("https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15/2025revised/ashetable152025revised.zip"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Annual aggregate earnings tables by occupation and region. Definitions and suppression vary by table; no data has been collected into JobIntel.",
        geographic_coverage=("United Kingdom", "Regions"),
        update_frequency="Annual",
        reference_period="2026",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="uk.ons.labour-demand",
        source_name="Labour demand volumes by SOC 2020",
        source_organization="Office for National Statistics",
        source_reference=AnyHttpUrl("https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourdemandvolumesbystandardoccupationalclassificationsoc2020uk"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Online job advert counts by local authority and SOC 2020 occupation. Vendor-derived advert measures; not salary or hires.",
        geographic_coverage=("United Kingdom", "Local authorities"),
        update_frequency="Monthly",
        reference_period="2026-09",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="uk.ons.soc2020",
        source_name="Standard Occupational Classification 2020",
        source_organization="Office for National Statistics",
        source_reference=AnyHttpUrl("https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="UK occupation classification, coding index, and correspondence resources. No JobIntel canonical crosswalk is implemented.",
        geographic_coverage=("United Kingdom",),
        reference_period="2020",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="sg.mom.ows",
        source_name="Occupational Wages 2025",
        source_organization="Ministry of Manpower, Singapore",
        source_reference=AnyHttpUrl("https://stats.mom.gov.sg/Pages/Occupational-Wages-Tables2025.aspx"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Aggregate basic and gross monthly wage tables for full-time resident employees. Bonuses are excluded; no data has been collected into JobIntel.",
        geographic_coverage=("Singapore",),
        update_frequency="Annual survey release",
        reference_period="2025-06",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="sg.mom.vacancies",
        source_name="Job Vacancy Statistics",
        source_organization="Ministry of Manpower, Singapore",
        source_reference=AnyHttpUrl("https://stats.mom.gov.sg/SL/Pages/Job-Vacancy-Data-and-Other-Resources.aspx"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="Official quarterly and annual job vacancy releases with occupation detail varying by publication. No data has been collected into JobIntel.",
        geographic_coverage=("Singapore",),
        update_frequency="Quarterly and annual releases",
        validation_status=_NOT_COLLECTED,
    ),
    DataSource(
        source_id="sg.singstat.ssoc2024",
        source_name="Singapore Standard Occupational Classification 2024",
        source_organization="Singapore Department of Statistics",
        source_reference=AnyHttpUrl("https://www.singstat.gov.sg/standard-classifications/national-classifications/singapore-standard-occupational-classification-ssoc"),
        source_category=SourceCategory.OFFICIAL_STATISTICS,
        reuse_review_status=_REVIEW_REQUIRED,
        dataset_description="SSOC 2024 classification and correspondence tables. Classification metadata only; no JobIntel occupation mapping is implemented.",
        geographic_coverage=("Singapore",),
        reference_period="2024",
        validation_status=_NOT_COLLECTED,
    ),
)


class SourceRegistry:
    def __init__(self, sources: tuple[DataSource, ...] = _SOURCES) -> None:
        source_map = {source.source_id: source for source in sources}
        if len(source_map) != len(sources):
            raise ValueError("source identifiers must be unique")
        self._sources = source_map

    def list(self) -> list[DataSource]:
        return list(self._sources.values())

    def get(self, source_id: str) -> DataSource:
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise KeyError("source not found") from exc

    def identifiers(self) -> frozenset[str]:
        return frozenset(self._sources)


_registry = SourceRegistry()


def get_sources() -> list[DataSource]:
    return _registry.list()


def get_source(source_id: str) -> DataSource:
    return _registry.get(source_id)
