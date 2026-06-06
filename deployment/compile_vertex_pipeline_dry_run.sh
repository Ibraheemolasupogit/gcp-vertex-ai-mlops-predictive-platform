#!/usr/bin/env bash
set -euo pipefail

# Dry-run helper only. This script does not submit Vertex AI Pipeline jobs.

pipeline_file="pipelines/vertex_pipeline.py"
package_path="${PIPELINE_PACKAGE_PATH:-outputs/predictive_maintenance_pipeline.json}"

if [[ ! -f "${pipeline_file}" ]]; then
  echo "Pipeline skeleton not found: ${pipeline_file}" >&2
  exit 1
fi

echo "Checking whether the Kubeflow Pipelines SDK is installed..."
if ! python3 -c "import kfp" >/dev/null 2>&1; then
  echo "Kubeflow Pipelines SDK is not installed. Skipping compile step successfully."
  echo "Install kfp locally later if you want to compile a static pipeline package."
  exit 0
fi

echo "Kubeflow Pipelines SDK is available."
if [[ "${CONFIRM_COMPILE_VERTEX_PIPELINE:-false}" != "true" ]]; then
  echo "Dry run only. Set CONFIRM_COMPILE_VERTEX_PIPELINE=true to compile a local package."
  echo "No pipeline job was submitted."
  exit 0
fi

echo "Compiling local pipeline package to ${package_path}. No GCP commands will run."
python3 - <<'PY'
import os
from pathlib import Path

from kfp import compiler

from pipelines.vertex_pipeline import predictive_maintenance_mlops_pipeline

package_path = Path(os.environ.get("PIPELINE_PACKAGE_PATH", "outputs/predictive_maintenance_pipeline.json"))
package_path.parent.mkdir(parents=True, exist_ok=True)
compiler.Compiler().compile(
    pipeline_func=predictive_maintenance_mlops_pipeline,
    package_path=str(package_path),
)
print(f"Compiled local pipeline package: {package_path}")
PY
