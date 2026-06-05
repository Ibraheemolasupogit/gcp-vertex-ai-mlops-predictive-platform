#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"
PYTHONPATH=src "${PYTHON_BIN}" -m vertex_mlops_platform.cli run-all-local
