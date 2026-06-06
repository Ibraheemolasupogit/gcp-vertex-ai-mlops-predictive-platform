"""Run a local single-record prediction smoke test."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vertex_mlops_platform.prediction.model_loader import load_model_bundle  # noqa: E402
from vertex_mlops_platform.prediction.predictor import predict_single  # noqa: E402


def main() -> int:
    """Load the local model bundle and score the sample request."""
    model, metadata = load_model_bundle(
        model_path=PROJECT_ROOT / "models" / "predictive_maintenance_model.joblib",
        metadata_path=PROJECT_ROOT / "models" / "model_metadata.json",
    )
    request_path = PROJECT_ROOT / "data" / "sample" / "prediction_request.json"
    request = json.loads(request_path.read_text(encoding="utf-8"))
    prediction = predict_single(model, metadata, request)

    print(json.dumps(prediction, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
