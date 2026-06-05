"""Local model training for the predictive maintenance classifier."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_CONFIG_PATH = PROJECT_ROOT / "configs" / "model_config.yaml"


def load_model_config(config_path: Path | str = DEFAULT_MODEL_CONFIG_PATH) -> dict[str, Any]:
    """Load local model training configuration."""
    config_path = Path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Model config file not found: {config_path}")
    with config_path.open() as config_file:
        config = yaml.safe_load(config_file)
    return dict(config)


def load_feature_table(path: Path | str) -> pd.DataFrame:
    """Load the model-ready feature table."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Feature table not found: {path}. Run scripts/run_feature_engineering.py first."
        )
    return pd.read_csv(path, parse_dates=["timestamp"])


def train_predictive_maintenance_model(
    feature_table: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Train a deterministic RandomForest classifier and return training artifacts."""
    training_config = config["training"]
    target_column = training_config["target_column"]
    if target_column not in feature_table.columns:
        raise ValueError(f"Target column not found in feature table: {target_column}")

    x, y, feature_columns = _split_features_and_target(feature_table, training_config)
    numeric_features = x.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [column for column in x.columns if column not in numeric_features]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=float(training_config["test_size"]),
        random_state=int(training_config["random_state"]),
        stratify=y if y.nunique() > 1 else None,
    )

    model = _build_pipeline(numeric_features, categorical_features, config)
    model.fit(x_train, y_train)

    return {
        "model": model,
        "x_train": x_train,
        "x_test": x_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_columns": feature_columns,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }


def save_model(model: Pipeline, output_path: Path | str) -> Path:
    """Persist a trained model artifact locally."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    return output_path


def _split_features_and_target(
    feature_table: pd.DataFrame,
    training_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    excluded_columns = set(training_config["excluded_columns"])
    target_column = training_config["target_column"]
    leakage_columns = excluded_columns | {target_column}
    feature_columns = [
        column for column in feature_table.columns if column not in leakage_columns
    ]
    return feature_table[feature_columns], feature_table[target_column].astype(int), feature_columns


def _build_pipeline(
    numeric_features: list[str],
    categorical_features: list[str],
    config: dict[str, Any],
) -> Pipeline:
    classifier_config = config["classifier"]
    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=int(classifier_config["n_estimators"]),
        max_depth=classifier_config["max_depth"],
        min_samples_leaf=int(classifier_config["min_samples_leaf"]),
        class_weight=classifier_config["class_weight"],
        random_state=int(config["training"]["random_state"]),
        n_jobs=1,
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])
