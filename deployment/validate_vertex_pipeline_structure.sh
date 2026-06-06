#!/usr/bin/env bash
set -euo pipefail

# Dry-run local validation only. This script does not require Kubeflow,
# Vertex AI, cloud CLIs, or GCP credentials.

pipeline_file="pipelines/vertex_pipeline.py"
components_file="pipelines/components.md"
config_file="pipelines/config/vertex_pipeline_config.example.yaml"

for file_path in "${pipeline_file}" "${components_file}" "${config_file}"; do
  if [[ ! -f "${file_path}" ]]; then
    echo "Required pipeline file not found: ${file_path}" >&2
    exit 1
  fi
done

echo "Found Vertex AI pipeline design files."
echo "Running Python syntax check without requiring Kubeflow..."
python3 -m py_compile "${pipeline_file}"

echo "Checking expected component names..."
expected_components=(
  validate_data_component
  build_features_component
  train_model_component
  evaluate_model_component
  run_approval_gates_component
  register_model_component
  generate_model_card_component
  predictive_maintenance_mlops_pipeline
)

for component_name in "${expected_components[@]}"; do
  if ! grep -q "${component_name}" "${pipeline_file}"; then
    echo "Expected component not found in pipeline skeleton: ${component_name}" >&2
    exit 1
  fi
done

echo "Vertex AI pipeline skeleton validation passed. No pipeline jobs or GCP commands were run."
