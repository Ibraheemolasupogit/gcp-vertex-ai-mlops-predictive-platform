"""Vertex AI Pipelines / Kubeflow skeleton for predictive maintenance MLOps.

This module is intentionally safe to import without Kubeflow Pipelines
installed. Component bodies are placeholders and do not make GCP calls.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

try:  # pragma: no cover - Kubeflow is intentionally optional for local tests.
    from kfp import dsl
except ImportError:  # pragma: no cover
    dsl = None  # type: ignore[assignment]

F = TypeVar("F", bound=Callable[..., Any])


def _component(func: F) -> F:
    """Decorate with KFP component only when the SDK is installed."""
    if dsl is None:
        return func
    return dsl.component(func)  # type: ignore[return-value]


def _pipeline(func: F) -> F:
    """Decorate with KFP pipeline only when the SDK is installed."""
    if dsl is None:
        return func
    return dsl.pipeline(name="predictive-maintenance-mlops-pipeline")(func)  # type: ignore[return-value]


@_component
def validate_data_component(feature_table_uri: str) -> str:
    """Placeholder for validating source data and feature-table readiness."""
    return f"Would validate data quality for feature table: {feature_table_uri}"


@_component
def build_features_component(feature_table_uri: str) -> str:
    """Placeholder for building or resolving the model-ready feature table."""
    return f"Would build or resolve feature table artifact: {feature_table_uri}"


@_component
def train_model_component(feature_table_uri: str, model_output_uri: str) -> str:
    """Placeholder for submitting managed model training."""
    return (
        "Would train predictive maintenance model using "
        f"{feature_table_uri} and write artifact to {model_output_uri}"
    )


@_component
def evaluate_model_component(model_output_uri: str) -> str:
    """Placeholder for collecting model metrics and evaluation outputs."""
    return f"Would evaluate model artifact from: {model_output_uri}"


@_component
def run_approval_gates_component(
    minimum_f1: float,
    minimum_recall: float,
) -> str:
    """Placeholder for applying deployment approval thresholds."""
    return (
        "Would run approval gates with "
        f"minimum_f1={minimum_f1} and minimum_recall={minimum_recall}"
    )


@_component
def register_model_component(model_display_name: str, model_output_uri: str) -> str:
    """Placeholder for registering a candidate model version."""
    return (
        "Would register candidate model "
        f"{model_display_name} from artifact URI {model_output_uri}"
    )


@_component
def generate_model_card_component(model_display_name: str) -> str:
    """Placeholder for generating a model-card-style evidence artifact."""
    return f"Would generate model card for {model_display_name}"


@_pipeline
def predictive_maintenance_mlops_pipeline(
    feature_table_uri: str = "gs://your-bucket/data/feature_table.csv",
    model_output_uri: str = "gs://your-bucket/models/predictive-maintenance/",
    model_display_name: str = "predictive-maintenance-model",
    minimum_f1: float = 0.80,
    minimum_recall: float = 0.80,
) -> list[str] | None:
    """Placeholder pipeline definition for the predictive maintenance workflow."""
    validation = validate_data_component(feature_table_uri)
    features = build_features_component(feature_table_uri)
    training = train_model_component(feature_table_uri, model_output_uri)
    evaluation = evaluate_model_component(model_output_uri)
    approval = run_approval_gates_component(minimum_f1, minimum_recall)
    registration = register_model_component(model_display_name, model_output_uri)
    model_card = generate_model_card_component(model_display_name)

    if dsl is None:
        return [
            validation,
            features,
            training,
            evaluation,
            approval,
            registration,
            model_card,
        ]
    return None
