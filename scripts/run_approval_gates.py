"""Run local deployment approval gates."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.training.approval_gates import (  # noqa: E402
    load_gate_config,
    run_approval_gates,
    write_gate_outputs,
)


def main() -> int:
    """Run local approval gates and write readiness artifacts."""
    config = load_gate_config(PROJECT_ROOT / "configs" / "deployment_gates.yaml")
    readiness = run_approval_gates(config, project_root=PROJECT_ROOT)
    results_path, report_path = write_gate_outputs(readiness, config, project_root=PROJECT_ROOT)

    print(f"Deployment readiness status: {readiness['overall_status']}")
    print(f"Passed gates: {readiness['gate_summary']['passed']}")
    print(f"Warnings: {readiness['gate_summary']['warnings']}")
    print(f"Failed gates: {readiness['gate_summary']['failed']}")
    print(f"Wrote gate results to {results_path.relative_to(PROJECT_ROOT)}")
    print(f"Wrote readiness report to {report_path.relative_to(PROJECT_ROOT)}")
    return 0 if readiness["overall_status"] in {"Ready", "Review"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
