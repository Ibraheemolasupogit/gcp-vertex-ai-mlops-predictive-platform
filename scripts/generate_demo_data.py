"""Generate local synthetic predictive maintenance sample datasets."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.data_generation import (  # noqa: E402
    generate_all_datasets,
    load_data_config,
)


def main() -> int:
    """Generate all configured synthetic sample datasets."""
    config = load_data_config(PROJECT_ROOT / "configs" / "data_config.yaml")
    datasets = generate_all_datasets(config=config, project_root=PROJECT_ROOT)

    for name, dataframe in datasets.items():
        output_path = PROJECT_ROOT / config["output_paths"][name]
        print(f"Wrote {len(dataframe):,} rows to {output_path.relative_to(PROJECT_ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
