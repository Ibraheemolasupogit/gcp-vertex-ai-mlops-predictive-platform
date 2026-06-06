"""Model and metadata loading utilities for local prediction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "predictive_maintenance_model.joblib"
DEFAULT_METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"


def load_model(model_path: Path | str = DEFAULT_MODEL_PATH) -> Any:
    """Load the trained local model artifact."""
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")
    return joblib.load(model_path)


def load_model_metadata(metadata_path: Path | str = DEFAULT_METADATA_PATH) -> dict[str, Any]:
    """Load serving-oriented model metadata."""
    metadata_path = Path(metadata_path)
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Model metadata not found: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def load_model_bundle(
    model_path: Path | str = DEFAULT_MODEL_PATH,
    metadata_path: Path | str = DEFAULT_METADATA_PATH,
) -> tuple[Any, dict[str, Any]]:
    """Load the model artifact and metadata together."""
    return load_model(model_path), load_model_metadata(metadata_path)
