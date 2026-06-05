"""Run local feature engineering and write feature store metadata."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.features.feature_store_simulation import (  # noqa: E402
    run_feature_engineering,
)


def main() -> int:
    """Generate the local model-ready feature table."""
    feature_table, metadata = run_feature_engineering(
        data_config_path=PROJECT_ROOT / "configs" / "data_config.yaml",
        feature_config_path=PROJECT_ROOT / "configs" / "feature_config.yaml",
        project_root=PROJECT_ROOT,
    )

    print(f"Feature engineering complete: {len(feature_table):,} rows")
    print(f"Feature count: {metadata['feature_count']}")
    print("Wrote feature table to data/processed/feature_table.csv")
    print("Wrote metadata to outputs/feature_store_metadata.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
