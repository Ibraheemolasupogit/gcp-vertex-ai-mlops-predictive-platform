from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from vertex_mlops_platform.prediction.model_loader import (
    load_model,
    load_model_metadata,
)
from vertex_mlops_platform.prediction.predictor import (
    predict_batch,
    predict_single,
)
from vertex_mlops_platform.prediction.schemas import (
    PredictionInputError,
    validate_prediction_record,
)
from vertex_mlops_platform.training.train_model import (
    build_model_metadata,
    load_model_config,
    save_model,
    save_model_metadata,
    train_predictive_maintenance_model,
)

ROOT = Path(__file__).resolve().parents[1]


def _feature_subset() -> pd.DataFrame:
    feature_table = pd.read_csv(ROOT / "data" / "processed" / "feature_table.csv")
    positive_rows = feature_table[feature_table["failure_within_label_window"] == 1].head(80)
    negative_rows = feature_table[feature_table["failure_within_label_window"] == 0].head(80)
    return pd.concat([positive_rows, negative_rows], ignore_index=True)


def _small_model_bundle(tmp_path) -> tuple[object, dict[str, object]]:
    config = load_model_config(ROOT / "configs" / "model_config.yaml")
    config["classifier"]["n_estimators"] = 10
    feature_table = _feature_subset()
    artifacts = train_predictive_maintenance_model(feature_table, config)
    model_path = save_model(artifacts["model"], tmp_path / "model.joblib")
    metadata = build_model_metadata(
        artifacts,
        config,
        model_artifact_path=model_path,
        approval_status="test",
    )
    save_model_metadata(metadata, tmp_path / "model_metadata.json")
    return load_model(model_path), load_model_metadata(tmp_path / "model_metadata.json")


def _sample_request(metadata: dict[str, object]) -> dict[str, object]:
    request_path = ROOT / "data" / "sample" / "prediction_request.json"
    request = json.loads(request_path.read_text(encoding="utf-8"))
    return {column: request[column] for column in metadata["feature_columns"]}


def test_model_metadata_can_be_generated_and_loaded(tmp_path) -> None:
    _, metadata = _small_model_bundle(tmp_path)

    assert metadata["model_name"] == "predictive_maintenance_classifier"
    assert metadata["model_version"] == "local-v1"
    assert metadata["feature_columns"]
    assert metadata["categorical_features"]
    assert metadata["numeric_features"]
    assert "local_only_notice" in metadata


def test_trained_model_artifact_can_be_loaded(tmp_path) -> None:
    model, _ = _small_model_bundle(tmp_path)

    assert hasattr(model, "predict")


def test_sample_prediction_request_has_required_fields(tmp_path) -> None:
    _, metadata = _small_model_bundle(tmp_path)
    request = _sample_request(metadata)

    assert set(metadata["feature_columns"]).issubset(request)
    assert metadata["target_column"] not in request


def test_single_prediction_returns_expected_keys(tmp_path) -> None:
    model, metadata = _small_model_bundle(tmp_path)
    prediction = predict_single(model, metadata, _sample_request(metadata))

    assert {"prediction_class", "prediction_probability", "risk_band"} == set(prediction)
    assert prediction["risk_band"] in {"low", "medium", "high", "critical"}


def test_batch_prediction_works_on_small_dataframe(tmp_path) -> None:
    model, metadata = _small_model_bundle(tmp_path)
    request = _sample_request(metadata)
    batch = pd.DataFrame([request, request])

    predictions = predict_batch(model, metadata, batch)

    assert len(predictions) == 2
    assert {"prediction_class", "prediction_probability", "risk_band"}.issubset(
        predictions.columns
    )


def test_prediction_utilities_do_not_require_api_or_cloud_modules(tmp_path) -> None:
    model, metadata = _small_model_bundle(tmp_path)

    prediction = predict_single(model, metadata, _sample_request(metadata))

    assert prediction["risk_band"] in {"low", "medium", "high", "critical"}


def test_missing_model_artifact_raises_clear_error(tmp_path) -> None:
    missing_path = tmp_path / "missing.joblib"

    with pytest.raises(FileNotFoundError, match="Model artifact not found"):
        load_model(missing_path)


def test_target_column_is_not_required_and_rejected_if_supplied(tmp_path) -> None:
    _, metadata = _small_model_bundle(tmp_path)
    request = _sample_request(metadata)
    validate_prediction_record(request, metadata)
    request[metadata["target_column"]] = 1

    with pytest.raises(PredictionInputError, match="must not include target column"):
        validate_prediction_record(request, metadata)
