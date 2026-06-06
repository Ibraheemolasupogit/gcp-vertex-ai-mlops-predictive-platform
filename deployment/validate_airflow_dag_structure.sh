#!/usr/bin/env bash
set -euo pipefail

# Dry-run local validation only. This script does not require Airflow, Cloud
# Composer, cloud CLIs, or GCP credentials.

dag_file="airflow/dags/predictive_maintenance_continuous_training_dag.py"

if [[ ! -f "${dag_file}" ]]; then
  echo "DAG file not found: ${dag_file}" >&2
  exit 1
fi

echo "Found DAG skeleton: ${dag_file}"
echo "Running Python syntax check without requiring Airflow..."
python3 -m py_compile "${dag_file}"

echo "Checking expected task names..."
expected_tasks=(
  check_new_data
  validate_data
  build_features
  submit_vertex_training_job
  collect_training_metrics
  run_approval_gates
  register_candidate_model
  notify_reviewer
)

for task_name in "${expected_tasks[@]}"; do
  if ! grep -q "${task_name}" "${dag_file}"; then
    echo "Expected task not found in DAG skeleton: ${task_name}" >&2
    exit 1
  fi
done

echo "DAG skeleton validation passed. No Airflow or GCP commands were run."
