# Cloud Composer / Airflow Continuous Training Design

R12 prepares a Cloud Composer and Airflow continuous training design for the
predictive maintenance platform. It does not deploy Cloud Composer, run Airflow,
submit Vertex AI jobs, or execute GCP commands.

## Purpose Of Continuous Training

Continuous training keeps a model lifecycle responsive to changing data,
operating conditions, and business risk. In predictive maintenance, equipment
behavior can shift as machines age, operating loads change, maintenance
procedures improve, or new failure modes appear. A scheduled and event-aware
training workflow gives the platform a controlled way to evaluate whether a new
candidate model should be created and reviewed.

## Retraining Triggers

- Scheduled retraining, such as weekly or monthly model refresh.
- New data arrival in Cloud Storage, BigQuery, or a feature table.
- Feature drift, such as a change in temperature, vibration, pressure, or load
  distributions.
- Prediction drift, such as a change in risk band distribution.
- Performance degradation, such as falling recall for failure detection.
- Manual approval trigger from an operator, data scientist, or reviewer.

## Cloud Composer Architecture

```text
Cloud Composer environment
  -> Airflow DAG
  -> Cloud Storage data and model artifact locations
  -> BigQuery or feature table source
  -> Vertex AI custom training
  -> Metrics and evaluation outputs
  -> Approval gates
  -> Vertex AI Model Registry candidate version
  -> Optional reviewer notification
```

The Composer service account should be scoped to the minimum permissions needed
to read data, submit Vertex AI training jobs, inspect outputs, and update model
registry metadata.

## Airflow Task Sequence

1. `check_new_data`: confirm that new telemetry, features, or drift signals are
   available.
2. `validate_data`: run schema and data quality checks before training.
3. `build_features`: build or reference the latest model-ready feature table.
4. `submit_vertex_training_job`: submit a parameterized Vertex AI custom
   training job.
5. `collect_training_metrics`: collect metrics, reports, and model metadata.
6. `run_approval_gates`: evaluate whether the candidate model is acceptable.
7. `register_candidate_model`: register or stage the candidate model version.
8. `notify_reviewer`: notify a reviewer or operations channel with results.

The skeleton DAG is stored at
`airflow/dags/predictive_maintenance_continuous_training_dag.py`.

## Configuration

The placeholder Composer environment settings are in
`deployment/composer.env.example`. The DAG-specific placeholder configuration is
in `airflow/dags/config/continuous_training_config.example.yaml`.

Both files use placeholders only and should be copied into local, uncommitted
configuration before a real demonstration.

## Evidence Screenshots

Capture these only after a real Cloud Composer demonstration:

- Composer environment page.
- DAG graph view.
- DAG run success.
- Task logs.
- Vertex AI training job triggered by the DAG.
- Model Registry candidate version.
- Approval gate output.
- Reviewer notification output if implemented.

## Security Notes

- Do not commit service account keys.
- Use a least privilege Composer service account.
- Use Secret Manager or Composer environment configuration for secrets only if
  secrets are required later.
- Keep project IDs, bucket names, and service account identities parameterized or
  redacted in docs and evidence.
- Do not commit `.env` files.

## Limitations

R12 is a design and skeleton milestone only. It uses synthetic data, placeholder
configuration, and safe task functions. No real Composer environment is created,
no DAG run is started, and no Vertex AI or GCP command is executed. Vertex AI Pipelines and Kubeflow design are deferred to R13.
