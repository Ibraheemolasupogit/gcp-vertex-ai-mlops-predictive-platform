# Architecture

This project starts as a local-first MLOps platform for predictive maintenance.
The intended architecture separates data generation, ingestion, features,
training, registry, prediction, monitoring, serving, and reporting into distinct
modules so each workflow can be tested before cloud mapping.

The scaffold avoids credentials and cloud execution. Later milestones will add
local behavior first, then document how the same responsibilities map to GCP
services.
