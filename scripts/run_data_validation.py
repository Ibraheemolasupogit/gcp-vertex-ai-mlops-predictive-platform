"""Run local ingestion and data validation for sample datasets."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.ingestion.validate_schema import validate_and_write_summary  # noqa: E402


def main() -> int:
    """Validate configured sample datasets and write the data quality summary."""
    output_path = PROJECT_ROOT / "outputs" / "data_quality_summary.json"
    summary = validate_and_write_summary(
        config_path=PROJECT_ROOT / "configs" / "data_config.yaml",
        output_path=output_path,
    )

    total_checks = len(summary["validation_checks"])
    issue_count = sum(summary["issue_counts_by_severity"].values())
    print(f"Data validation status: {summary['overall_status']}")
    print(f"Validation checks: {total_checks}")
    print(f"Issues found: {issue_count}")
    print(f"Wrote summary to {output_path.relative_to(PROJECT_ROOT)}")
    return 0 if summary["overall_status"] in {"passed", "warning"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
