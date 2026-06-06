#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"
"${PYTHON_BIN}" scripts/generate_demo_data.py
"${PYTHON_BIN}" scripts/run_data_validation.py
"${PYTHON_BIN}" scripts/run_feature_engineering.py
"${PYTHON_BIN}" scripts/run_training_pipeline.py
"${PYTHON_BIN}" scripts/run_approval_gates.py
"${PYTHON_BIN}" scripts/run_local_prediction.py
