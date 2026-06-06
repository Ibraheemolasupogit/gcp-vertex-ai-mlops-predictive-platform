# Local Model Artifacts

This directory contains local-only model artifacts generated from synthetic
predictive maintenance data.

| File | Purpose |
| --- | --- |
| `predictive_maintenance_model.joblib` | Fitted sklearn pipeline with preprocessing and classifier. |
| `model_metadata.json` | Serving-oriented metadata: feature schema, model path, target, metrics path, and local-only notice. |

These artifacts are prepared for local serving development. They are not
deployed to GCP and should not contain credentials or real project identifiers.
