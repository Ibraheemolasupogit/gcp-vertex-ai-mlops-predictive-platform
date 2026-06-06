"""Configuration helpers for local model and Vertex AI proxy serving modes."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ

LOCAL_MODEL_MODE = "local_model"
VERTEX_ENDPOINT_MODE = "vertex_endpoint"
_VERTEX_ALIASES = {"vertex", "vertex_endpoint"}


@dataclass(frozen=True)
class ProxyConfig:
    """Runtime prediction mode configuration for the serving API."""

    prediction_mode: str = LOCAL_MODEL_MODE
    enable_vertex_proxy: bool = False
    project_id: str | None = None
    region: str | None = None
    endpoint_id: str | None = None
    request_timeout_seconds: int = 30

    @property
    def vertex_enabled(self) -> bool:
        """Return whether requests should use the Vertex AI proxy path."""
        return self.prediction_mode == VERTEX_ENDPOINT_MODE and self.enable_vertex_proxy


def load_proxy_config(env: dict[str, str] | None = None) -> ProxyConfig:
    """Load proxy configuration from environment variables.

    The default is local model serving. Vertex settings are validated only when
    proxy mode is explicitly enabled so local tests never require GCP values or
    credentials.
    """
    source = environ if env is None else env
    raw_mode = source.get("PREDICTION_MODE", LOCAL_MODEL_MODE).strip().lower()
    prediction_mode = _normalize_prediction_mode(raw_mode)
    enable_vertex_proxy = _as_bool(source.get("ENABLE_VERTEX_PROXY", "false"))

    config = ProxyConfig(
        prediction_mode=prediction_mode,
        enable_vertex_proxy=enable_vertex_proxy,
        project_id=source.get("VERTEX_PROJECT_ID") or source.get("PROJECT_ID"),
        region=source.get("VERTEX_ENDPOINT_REGION") or source.get("REGION"),
        endpoint_id=source.get("VERTEX_ENDPOINT_ID"),
        request_timeout_seconds=int(source.get("REQUEST_TIMEOUT_SECONDS", "30")),
    )
    if config.vertex_enabled:
        _validate_vertex_config(config)
    return config


def _normalize_prediction_mode(raw_mode: str) -> str:
    if raw_mode in _VERTEX_ALIASES:
        return VERTEX_ENDPOINT_MODE
    if raw_mode == LOCAL_MODEL_MODE:
        return LOCAL_MODEL_MODE
    raise ValueError(
        "PREDICTION_MODE must be 'local_model', 'vertex', or 'vertex_endpoint'."
    )


def _validate_vertex_config(config: ProxyConfig) -> None:
    missing = [
        name
        for name, value in {
            "VERTEX_PROJECT_ID or PROJECT_ID": config.project_id,
            "VERTEX_ENDPOINT_REGION or REGION": config.region,
            "VERTEX_ENDPOINT_ID": config.endpoint_id,
        }.items()
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing Vertex AI proxy configuration: {joined}")


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}
