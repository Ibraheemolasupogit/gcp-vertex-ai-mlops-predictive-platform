# Repository Health Check

Use this checklist before presenting the repository.

## Local Pipeline

```bash
scripts/run_all_local.sh
```

This should generate synthetic data, validate data, build features, train and
evaluate the model, run approval gates, and run local prediction.

## Individual Commands

```bash
python3 scripts/generate_demo_data.py
python3 scripts/run_data_validation.py
python3 scripts/run_feature_engineering.py
python3 scripts/run_training_pipeline.py
python3 scripts/run_approval_gates.py
python3 scripts/run_local_prediction.py
python3 scripts/generate_monitoring_summary.py
```

## Tests And Lint

```bash
python3 -m pytest
python3 -m ruff check .
```

## API Local Check

```bash
python3 scripts/run_api_local.py
```

Then check `/health` and `/predict` with the examples in `examples/`.

## Docker Static Check

```bash
python3 -m pytest tests/test_docker_config.py
```

Docker runtime testing is optional and depends on local Docker availability.

## Documentation And Evidence Check

Review `docs/deployment_evidence_checklist.md` and `docs/screenshot_evidence_guide.md`.
Evidence folders should contain only real screenshots or redacted command
outputs. Fake screenshots should not be committed.

## Ready For Presentation

The repository is ready for presentation when tests pass, local scripts run, docs
are consistent, no credentials are present, and evidence folders clearly separate
planned screenshots from captured deployment proof.
