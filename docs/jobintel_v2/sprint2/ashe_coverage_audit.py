"""Reproduce the 2025 revised ASHE Table 15 (4) full-time annual-pay coverage audit.

Read-only: this script reads the ignored ONS archive extraction and SOC reference
workbook; it does not modify source data or write output files.
Requires the already available openpyxl package (no project dependency change).
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/raw/ashe_table15_2025_revised"
ARCHIVE = DATA / "ashetable152025revised.zip"
FOUR_DIGIT = DATA / "extracted/Table 15 (4)"
SOC_REFERENCE = DATA / (
    "soc2020_reference/"
    "soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx"
)
ESTIMATE = next(FOUR_DIGIT.glob("*Table 15.7a*Annual pay - Gross 2025.xlsx"))
CV = next(FOUR_DIGIT.glob("*Table 15.7b*Annual pay - Gross 2025 CV.xlsx"))
EXPECTED_ARCHIVE_SHA256 = (
    "AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3"
)
CELL_CODE = re.compile(r"^'?([0-9]{4})$")


def marker(value: object) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "numeric" if math.isfinite(value) else "invalid_nonfinite"
    if value is None:
        return "blank"
    if isinstance(value, str) and value.strip() in {"x", "..", ":", "-"}:
        return value.strip()
    return "other"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_soc_hierarchy() -> tuple[dict[str, tuple[int, str]], dict[int, str]]:
    workbook = load_workbook(SOC_REFERENCE, read_only=True, data_only=True)
    sheet = workbook["SOC2020 descriptions"]
    groups: dict[int, str] = {}
    units: dict[str, tuple[int, str]] = {}
    current_major: int | None = None
    for row in sheet.iter_rows(min_row=2, max_col=6, values_only=True):
        major, sub_major, minor, unit, title = row[1], row[2], row[3], row[4], row[5]
        if isinstance(major, int) and sub_major in (None, "<blank>") and minor in (None, "<blank>") and unit in (None, "<blank>"):
            current_major = major
            groups[major] = str(title)
        if isinstance(unit, int) and len(str(unit)) == 4:
            if current_major is None or int(str(unit)[0]) != current_major:
                raise ValueError(f"SOC hierarchy major group mismatch for unit group {unit}")
            units[str(unit)] = (current_major, str(title))
    workbook.close()
    return units, groups


def read_cells(path: Path) -> tuple[dict[tuple[str, str], tuple[object, ...]], list[str]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Full-Time"]
    headers = [str(value) if value is not None else "" for value in next(
        sheet.iter_rows(min_row=5, max_row=5, max_col=17, values_only=True)
    )]
    records: dict[tuple[str, str], tuple[object, ...]] = {}
    for row in sheet.iter_rows(min_row=6, max_col=17, values_only=True):
        description, source_code = row[0], row[1]
        if not isinstance(description, str) or source_code is None:
            continue
        match = CELL_CODE.fullmatch(str(source_code).strip())
        if not match:
            continue
        code = match.group(1)
        region = description.strip().split(",", 1)[0].strip()
        key = (region, code)
        if key in records:
            raise ValueError(f"Duplicate region/occupation key: {key!r}")
        records[key] = row
    workbook.close()
    return records, headers


def main() -> None:
    if not ARCHIVE.is_file() or not ESTIMATE.is_file() or not CV.is_file():
        raise FileNotFoundError(f"Expected ASHE files missing beneath {DATA}")

    actual_hash = hash_file(ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive_members = len(archive.namelist())
        corrupt_member = archive.testzip()
    extracted_xlsx_count = sum(1 for _ in DATA.joinpath("extracted").rglob("*.xlsx"))

    units, major_titles = read_soc_hierarchy()
    estimate, headers = read_cells(ESTIMATE)
    cv_cells, _ = read_cells(CV)
    if set(estimate) != set(cv_cells):
        raise ValueError("Estimate and CV sheets do not have identical cell keys")

    source_codes = {code for _, code in estimate}
    official_codes = set(units)
    if source_codes != official_codes:
        raise ValueError(
            f"SOC code mismatch; source-only={sorted(source_codes - official_codes)}, "
            f"official-only={sorted(official_codes - source_codes)}"
        )

    regions = sorted({region for region, _ in estimate})
    state_counts: Counter[str] = Counter()
    region_stats: dict[str, Counter[str]] = defaultdict(Counter)
    occupation_stats: dict[str, Counter[str]] = defaultdict(Counter)
    major_stats: dict[int, Counter[str]] = defaultdict(Counter)
    cv_bands: Counter[str] = Counter()
    cv_status_for_numeric: Counter[str] = Counter()
    quantile_complete = Counter()
    numeric_percentile_count_distribution: Counter[int] = Counter()
    all_percentiles_with_usable_cv = Counter()
    other_statuses: Counter[str] = Counter()
    median_amount_checks: Counter[str] = Counter()
    combinations_by_region_status: dict[str, Counter[str]] = defaultdict(Counter)
    occupation_labels: dict[str, str] = {}
    occupation_major: dict[str, int] = {}

    for (region, code), row in estimate.items():
        state = marker(row[3])  # source median column
        state_counts[state] += 1
        region_stats[region][state] += 1
        occupation_stats[code][state] += 1
        major, soc_title = units[code]
        occupation_labels[code] = soc_title
        occupation_major[code] = major
        major_stats[major][state] += 1
        combinations_by_region_status[region][state] += 1
        if state not in {"numeric", "x", "blank", "..", ":", "-"}:
            other_statuses[state] += 1
        if state == "numeric":
            median_amount_checks["positive_finite"] += int(row[3] > 0)
            median_amount_checks["zero_or_negative"] += int(row[3] <= 0)
            median_amount_checks["finite_numeric"] += int(math.isfinite(row[3]))
        elif state == "invalid_nonfinite":
            median_amount_checks["nonfinite_numeric"] += 1

        cv_value = cv_cells[(region, code)][3]
        if state == "numeric":
            if isinstance(cv_value, (int, float)) and not isinstance(cv_value, bool):
                if cv_value <= 5:
                    band = "<=5%"
                elif cv_value <= 10:
                    band = ">5-10%"
                elif cv_value <= 20:
                    band = ">10-20%"
                else:
                    band = ">20%"
                cv_bands[band] += 1
                cv_status_for_numeric["numeric_cv"] += 1
            else:
                cv_status_for_numeric[f"cv_{marker(cv_value)}"] += 1

        percentile_values = row[7:17]
        numeric_percentiles = sum(marker(value) == "numeric" for value in percentile_values)
        numeric_percentile_count_distribution[numeric_percentiles] += 1
        all_numeric_percentiles = numeric_percentiles == 10
        quantile_complete["all_10_numeric" if all_numeric_percentiles else "not_all_10_numeric"] += 1
        cv_percentiles = cv_cells[(region, code)][7:17]
        all_percentile_cvs_usable = all(
            isinstance(value, (int, float)) and not isinstance(value, bool) and value <= 20
            for value in cv_percentiles
        )
        all_percentiles_with_usable_cv[
            "all_10_estimates_and_cvs_numeric_cv_le_20"
            if all_numeric_percentiles and all_percentile_cvs_usable
            else "not_all_10_estimates_and_cvs_usable"
        ] += 1

    numeric_occupation_support = Counter(
        sum(1 for region in regions if marker(estimate[(region, code)][3]) == "numeric")
        for code in source_codes
    )
    qualifying_occupations = []
    for code in sorted(source_codes):
        count = occupation_stats[code]["numeric"]
        if count >= 8:  # predeclared descriptive threshold: at least 8 of 11 regions
            qualifying_occupations.append({
                "code": code,
                "occupation": occupation_labels[code],
                "major_group": occupation_major[code],
                "numeric_regions": count,
                "suppressed_regions": occupation_stats[code]["x"],
                "blank_regions": occupation_stats[code]["blank"],
            })

    region_rows = []
    for region in regions:
        counts = region_stats[region]
        numeric = counts["numeric"]
        region_rows.append({
            "region": region,
            "unit_groups": len(source_codes),
            "numeric": numeric,
            "numeric_pct": round(100 * numeric / len(source_codes), 1),
            "x_suppressed": counts["x"],
            "x_pct": round(100 * counts["x"] / len(source_codes), 1),
            "blank": counts["blank"],
            "blank_pct": round(100 * counts["blank"] / len(source_codes), 1),
            "other_markers": sum(v for k, v in counts.items() if k not in {"numeric", "x", "blank"}),
        })

    occupation_rows = []
    occupation_region_matrix = []
    for code in sorted(source_codes):
        counts = occupation_stats[code]
        occupation_rows.append({
            "code": code,
            "occupation": occupation_labels[code],
            "major_group": occupation_major[code],
            "numeric_regions": counts["numeric"],
            "x_suppressed_regions": counts["x"],
            "blank_regions": counts["blank"],
            "other_markers": sum(v for k, v in counts.items() if k not in {"numeric", "x", "blank"}),
        })
        occupation_region_matrix.append({
            "code": code,
            "occupation": occupation_labels[code],
            "status_by_region": {
                region: {
                    "numeric": "N",
                    "x": "X",
                    "blank": "B",
                    "..": "D",
                    ":": "NA",
                    "-": "NEGL",
                    "other": "OTHER",
                }.get(marker(estimate[(region, code)][3]), "OTHER")
                for region in regions
            },
        })

    major_rows = []
    for major in sorted(major_stats):
        counts = major_stats[major]
        code_count = sum(1 for code in source_codes if occupation_major[code] == major)
        total = code_count * len(regions)
        numeric = counts["numeric"]
        major_rows.append({
            "major_group": major,
            "title": major_titles[major],
            "unit_groups": code_count,
            "cells": total,
            "numeric": numeric,
            "numeric_pct": round(100 * numeric / total, 1),
            "x_suppressed": counts["x"],
            "blank": counts["blank"],
            "other_markers": sum(v for k, v in counts.items() if k not in {"numeric", "x", "blank"}),
        })

    major_region_rows = []
    for major in sorted(major_stats):
        for region in regions:
            numeric = sum(
                1 for code in source_codes
                if occupation_major[code] == major
                and marker(estimate[(region, code)][3]) == "numeric"
            )
            unit_groups = sum(1 for code in source_codes if occupation_major[code] == major)
            major_region_rows.append({
                "major_group": major,
                "region": region,
                "unit_groups": unit_groups,
                "numeric": numeric,
                "numeric_pct": round(100 * numeric / unit_groups, 1),
            })

    total_cells = len(estimate)
    result = {
        "archive": {
            "path": str(ARCHIVE),
            "sha256": actual_hash,
            "matches_documented_sha256": actual_hash == EXPECTED_ARCHIVE_SHA256,
            "zip_members": archive_members,
            "corrupt_member": corrupt_member,
            "extracted_xlsx_count": extracted_xlsx_count,
        },
        "source": {
            "estimate_file": ESTIMATE.name,
            "cv_file": CV.name,
            "sheet": "Full-Time",
            "reference_period": "2025 revised; annual gross pay, tax year ending 5 April 2025",
            "headers": headers,
        },
        "grain": {
            "valid_occupation_region_cells": total_cells,
            "regions": regions,
            "region_count": len(regions),
            "source_soc_codes": len(source_codes),
            "official_soc2020_unit_group_codes": len(official_codes),
            "code_sets_exactly_match": source_codes == official_codes,
            "unique_region_code_keys": total_cells,
            "duplicates": 0,
        },
        "median_status_counts": dict(sorted(state_counts.items())),
        "median_status_pct": {
            key: round(100 * value / total_cells, 2)
            for key, value in sorted(state_counts.items())
        },
        "median_amount_validation": dict(sorted(median_amount_checks.items())),
        "cv_bands_for_numeric_medians": dict(sorted(cv_bands.items())),
        "cv_state_for_numeric_medians": dict(sorted(cv_status_for_numeric.items())),
        "percentile_coverage_across_all_10_reported_percentiles": dict(quantile_complete),
        "numeric_percentile_count_distribution": {
            str(k): numeric_percentile_count_distribution[k]
            for k in range(11)
            if numeric_percentile_count_distribution[k]
        },
        "all_percentiles_and_matching_cv_coverage": dict(all_percentiles_with_usable_cv),
        "occupation_numeric_region_count_distribution": {
            str(k): numeric_occupation_support[k]
            for k in range(len(regions) + 1)
            if numeric_occupation_support[k]
        },
        "occupations_with_at_least_8_of_11_numeric_regions": qualifying_occupations,
        "occupations_with_numeric_value_in_all_11_regions": [
            item for item in qualifying_occupations if item["numeric_regions"] == len(regions)
        ],
        "regions": region_rows,
        "major_groups": major_rows,
        "major_group_by_region_coverage": major_region_rows,
        "occupation_coverage_rows": occupation_rows,
        "occupation_region_status_matrix": occupation_region_matrix,
        "other_marker_counts": dict(sorted(other_statuses.items())),
        "thresholds": {
            "occupation_region_comparison": "at least 8 of 11 region cells numeric (analytical screening rule, not an ONS standard)",
            "regional_occupation_profile": "at least 70% of 412 unit groups numeric (analytical screening rule, not an ONS standard)",
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
