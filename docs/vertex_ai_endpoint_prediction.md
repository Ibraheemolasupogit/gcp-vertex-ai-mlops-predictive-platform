# Vertex AI Endpoint, Online Prediction, And Batch Prediction Readiness

R10 prepares the repository for a future Vertex AI endpoint and prediction
demonstration. It does not create endpoints, deploy models, run prediction jobs,
or execute GCP commands.

## Purpose Of Vertex AI Endpoints

Vertex AI endpoints host registered models for managed online prediction. After
a model is trained, evaluated, and registered, it can be deployed to an endpoint
with serving infrastructure managed by Vertex AI. This gives the MLOps workflow a
clear path from local model development to managed model serving.

## Serving Options

Cloud Run model serving hosts the FastAPI container directly. It is useful for a
custom application API, custom routing, and simple container-first serving.

Vertex AI endpoint serving hosts a registered Vertex AI model behind a managed
prediction endpoint. It is useful when the model lifecycle should stay inside
Vertex AI Model Registry, endpoint deployment, and Vertex AI prediction tooling.

Online prediction sends low-latency request payloads to a deployed model on a
Vertex AI endpoint.

Batch prediction submits a job that reads many prediction records from Cloud
Storage and writes prediction outputs back to Cloud Storage.

## Model Registry To Endpoint Workflow

1. Train a model locally or through Vertex AI custom training.
2. Register the model in Vertex AI Model Registry.
3. Create a Vertex AI endpoint.
4. Deploy the registered model to the endpoint with a deployed model display
   name, machine type, replica counts, and traffic allocation.
5. Send online prediction requests or create batch prediction jobs.

The endpoint deployment template is documented in
`deployment/vertex_ai_endpoint_deployment.template.yaml`.

## Online Prediction Workflow

The future online prediction flow uses:

- A registered model ID from Vertex AI Model Registry.
- A Vertex AI endpoint ID.
- A JSON request shaped with an `instances` array.
- The same feature fields used by the local FastAPI `/predict` contract.

The example request at `examples/vertex_online_prediction_request.json` excludes
target and leakage fields such as `failure_within_label_window`.

Expected response shape depends on the serving container and Vertex AI model
deployment, but should include predictions for each instance. For this project,
the intended logical response mirrors the local API output: predicted class,
probability where available, and risk band.

## Batch Prediction Workflow

The future batch prediction flow uses:

- A registered Vertex AI model ID.
- A Cloud Storage JSONL input URI.
- A Cloud Storage output prefix.
- Batch prediction job configuration through Vertex AI.

The example JSONL records at `examples/vertex_batch_prediction_input.jsonl`
match the local serving feature contract and exclude target labels.

## Relationship To Local FastAPI `/predict`

The local FastAPI API is still the immediate serving contract for local and
Cloud Run workflows. Vertex AI online prediction should use the same model input
features where practical so that local smoke tests, Cloud Run tests, and Vertex
AI request examples remain comparable.

R11 will document the next pattern: a Cloud Run API wrapper in front of a Vertex
AI endpoint. That wrapper is not added in R10.

## Required GCP Services

- Vertex AI API for endpoints, deployed models, online prediction, and batch
  prediction.
- Cloud Storage for batch prediction input and output.
- IAM for endpoint deployment and prediction access.

## Required Artifacts

- Registered model in Vertex AI Model Registry.
- Serving container image associated with the registered model.
- Online prediction request payload.
- Batch prediction input data in Cloud Storage.
- Batch prediction output Cloud Storage location.

## Evidence Screenshots

Capture these only after a real GCP run:

- Vertex AI endpoint page.
- Deployed model on the endpoint.
- Endpoint ID and deployed model details.
- Online prediction request.
- Online prediction response.
- Batch prediction job page.
- Batch output in Cloud Storage.
- Logs or monitoring where available.

## Security Notes

- Do not commit service account keys.
- Use least privilege IAM for endpoint deployment and prediction.
- Use authenticated requests for non-public workloads.
- Keep project IDs, endpoint IDs, and bucket names parameterized or redacted in
  documentation.
- Do not commit `.env` files.

## Limitations

R10 is a readiness and mapping milestone only. It uses synthetic data and does
not create a real Vertex AI endpoint, deploy a model to Vertex AI, run online
prediction, or create a batch prediction job. The Cloud Run API wrapper in front of a Vertex AI endpoint is deferred to R11.
