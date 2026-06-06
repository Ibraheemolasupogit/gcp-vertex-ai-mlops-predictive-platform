"""Generate a lightweight local monitoring summary from existing artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "outputs" / "monitoring_summary.json"
LOCAL_ONLY_NOTICE = (
    "Local monitoring summary only. No Cloud Run, Vertex AI, or GCP monitoring "
    "resources are queried."
)


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON if present, otherwise return an empty dictionary."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_monitoring_summary(root: Path = ROOT) -> dict[str, Any]:
    """Build a local monitoring summary from data quality, model, and gate outputs."""
    outputs = root / "outputs"
    data_quality = load_json(outputs / "data_quality_summary.json")
    model_metrics = load_json(outputs / "model_metrics.json")
    approval = load_json(outputs / "deployment_gate_results.json")
    feature_metadata = load_json(outputs / "feature_store_metadata.json")

    metrics = model_metrics.get("metrics", {})
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "data_quality_status": data_quality.get("overall_status", "unknown"),
        "model_metrics_summary": {
            "accuracy": metrics.get("accuracy"),
            "precision": metrics.get("precision"),
            "recall": metrics.get("recall"),
            "f1": metrics.get("f1"),
            "roc_auc": metrics.get("roc_auc"),
            "positive_class_rate": metrics.get("positive_class_rate"),
        },
        "approval_status": approval.get("overall_status", "unknown"),
        "feature_table_metadata": {
            "row_count": feature_metadata.get("row_count"),
            "feature_count": feature_metadata.get("feature_count"),
            "feature_version": feature_metadata.get("feature_version"),
            "entity_keys": feature_metadata.get("entity_keys", []),
            "timestamp_key": feature_metadata.get("timestamp_key"),
        },
        "recommended_monitoring_signals": [
            "request_count",
            "latency",
            "error_rate",
            "prediction_volume",
            "prediction_distribution",
            "risk_band_distribution",
            "input_feature_drift",
            "data_quality_failures",
            "approval_gate_status",
            "retraining_trigger_events",
        ],
        "local_only_notice": LOCAL_ONLY_NOTICE,
    }


def write_monitoring_summary(output_path: Path = OUTPUT_PATH) -> dict[str, Any]:
    """Write the local monitoring summary JSON."""
    summary = build_monitoring_summary()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    """CLI entrypoint."""
    summary = write_monitoring_summary()
    print("Monitoring summary written to outputs/monitoring_summary.json")
    print(f"Data quality status: {summary['data_quality_status']}")
    print(f"Approval status: {summary['approval_status']}")


if __name__ == "__main__":
    main()
