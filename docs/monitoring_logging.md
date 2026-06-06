# Monitoring And Logging

Monitoring deployed ML APIs is about detecting service issues, model behavior
changes, and data quality problems before they become operational risk.

## Cloud Run Signals

For the FastAPI serving container on Cloud Run, useful platform signals include:

- Request count.
- Request latency.
- Error rate.
- Container startup and cold start behavior.
- Revision traffic allocation.
- Revision-specific request logs.

These signals help verify whether a deployment is healthy and whether canary or
traffic-splitting changes behave as expected.

## Model Monitoring Signals

For predictive maintenance, model-focused monitoring should include:

- Prediction volume by time period.
- Prediction distribution.
- Risk band distribution.
- Input feature drift for temperature, vibration, pressure, runtime, operating
  load, and maintenance history.
- Data quality failures from validation checks.
- Retraining triggers from drift, degraded metrics, or operational thresholds.

## Vertex AI Monitoring Mapping

In a future Vertex AI deployment, monitoring evidence could map to:

- Vertex AI endpoint logs.
- Batch prediction job outputs.
- Vertex AI Model Monitoring or drift checks where configured.
- Cloud Logging entries for prediction requests.
- Cloud Monitoring charts for endpoint or Cloud Run behavior.

## Evidence Screenshots

Capture real evidence only after deployment:

- Cloud Run request count, latency, and error charts.
- Cloud Run revision traffic and logs.
- Vertex AI endpoint prediction logs.
- Batch prediction output location.
- Drift or model monitoring dashboards if configured.
- Data quality and approval gate output after retraining.

## Limitations

This repository currently generates local summaries only. No real Cloud Run,
Vertex AI endpoint, model monitoring job, or Cloud Monitoring dashboard is
created in R14.
