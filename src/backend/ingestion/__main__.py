from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.backend.ingestion.runner import (
    DEFAULT_ARCHIVE,
    DEFAULT_EXTRACTED,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SOC_REFERENCE,
    PipelineError,
    run_ashe_2025_pipeline,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the verified ASHE 2025 revised Table 15 aggregate locally."
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--extracted-root", type=Path, default=DEFAULT_EXTRACTED)
    parser.add_argument("--soc-reference", type=Path, default=DEFAULT_SOC_REFERENCE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--local-preparation-only",
        action="store_true",
        help="Acknowledge that source reuse remains REVIEW_REQUIRED and outputs are not publishable.",
    )
    args = parser.parse_args()
    try:
        result = run_ashe_2025_pipeline(
            archive_path=args.archive,
            extracted_root=args.extracted_root,
            soc_reference_path=args.soc_reference,
            output_root=args.output_root,
            local_preparation_only=args.local_preparation_only,
        )
    except PipelineError as exc:
        print(f"ASHE ingestion failed [{exc.code}]: {exc}", file=sys.stderr)
        if exc.parse_result is not None:
            print(
                "Redacted structured validation result: "
                + json.dumps(exc.parse_result.quality.model_dump(mode="json"), sort_keys=True),
                file=sys.stderr,
            )
        return 2
    print(f"run_id={result.run_id}")
    print(f"records_written={result.records_written}")
    print(f"dataset={result.dataset_path}")
    print(f"dataset_sha256={result.dataset_sha256}")
    print(f"manifest={result.manifest_path}")
    print(f"quality_report={result.quality_report_path}")
    print(f"reused_existing_output={result.reused_existing_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
