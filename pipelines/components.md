# Vertex AI Pipeline Component Mapping

These component definitions describe how the existing local MLOps workflow would
map to future Kubeflow / Vertex AI Pipeline components. They are design
artifacts only and do not submit pipeline jobs.

| Component | Purpose | Inputs | Outputs | Local Module Mapping | Future Vertex AI / Kubeflow Mapping |
| --- | --- | --- | --- | --- | --- |
| `validate_data_component` | Validate source data and feature-table readiness | Feature table URI, data quality config | Validation summary | `src/vertex_mlops_platform/ingestion/validate_schema.py` | KFP component producing data quality artifact |
| `build_features_component` | Build or resolve model-ready feature table | Validated source data, feature config | Feature table artifact | `src/vertex_mlops_platform/features/` | KFP component writing BigQuery or Cloud Storage feature artifact |
| `train_model_component` | Train candidate model | Feature table URI, model config | Model artifact | `src/vertex_mlops_platform/training/train_model.py` | Vertex AI custom training component |
| `evaluate_model_component` | Calculate metrics and reports | Model artifact, holdout data | Metrics JSON, evaluation report | `src/vertex_mlops_platform/training/evaluate_model.py` | KFP component emitting metrics and metadata |
| `run_approval_gates_component` | Apply deployment thresholds | Metrics, data quality summary, gate config | Approval result | `src/vertex_mlops_platform/training/approval_gates.py` | KFP component deciding candidate status |
| `register_model_component` | Register candidate model metadata | Approved artifact, metrics, labels | Registry metadata | `deployment/vertex_ai_model_registry_metadata.template.json` | Vertex AI Model Registry upload task |
| `generate_model_card_component` | Produce portfolio-ready model card evidence | Model metadata, metrics, limitations | Model card artifact | `reports/evaluation_report.md` and future docs | KFP component writing model documentation artifact |
