# Cloud Run API In Front Of Vertex AI Endpoint

R11 prepares a Cloud Run-to-Vertex AI proxy design for the existing FastAPI
service. The local API remains the default serving path. No Cloud Run deployment,
Vertex AI endpoint call, credentials, or GCP commands are used in this milestone.

## Purpose

Putting Cloud Run in front of a Vertex AI endpoint gives the project an
application API layer while keeping model lifecycle management in Vertex AI. The
Cloud Run service can validate requests, apply API-specific response formatting,
add correlation IDs, enforce authentication policy, and route prediction calls
to a managed Vertex AI endpoint.

## Cloud Run Direct Serving Versus Vertex Proxy

Serve directly from Cloud Run when the FastAPI container owns the model artifact
and prediction logic. This is simple, portable, and useful for the current local
and Cloud Run serving path.

Proxy to Vertex AI when the model is registered and deployed through Vertex AI
Model Registry and endpoints. This is useful when model versioning, endpoint
deployment, and prediction lifecycle evidence should remain in Vertex AI.

## Architecture

```text
Client
  -> Cloud Run FastAPI API
  -> Vertex AI Endpoint
  -> Cloud Logging / Cloud Monitoring
  -> IAM-controlled service-to-service access
```

The Cloud Run service account would need permission to call Vertex AI prediction
for the target endpoint.

## Request Flow

1. Client sends a request to Cloud Run `/predict`.
2. Cloud Run validates the request using the existing prediction schema.
3. Cloud Run transforms the request to Vertex AI `instances` format.
4. Cloud Run calls the configured Vertex AI endpoint.
5. Cloud Run normalises the Vertex AI response into the existing API response
   shape.
6. Cloud Run returns the response to the client with request metadata.

The transformation examples are in `examples/vertex_proxy_request.json` and
`examples/vertex_proxy_response.json`.

## Authentication Options

- Public Cloud Run endpoint for a controlled portfolio demonstration.
- Authenticated Cloud Run for non-public workloads.
- Cloud Run service account with Vertex AI prediction permission.
- Optional client identity validation before forwarding prediction requests.

## Environment Variables

- `PREDICTION_MODE`: `local_model` or `vertex_endpoint`.
- `ENABLE_VERTEX_PROXY`: must be `true` to use proxy mode.
- `VERTEX_PROJECT_ID`: GCP project containing the Vertex AI endpoint.
- `VERTEX_ENDPOINT_REGION`: Vertex AI endpoint region.
- `VERTEX_ENDPOINT_ID`: Vertex AI endpoint ID.
- `REQUEST_TIMEOUT_SECONDS`: prediction request timeout.

The placeholder template is `deployment/cloud_run_vertex_proxy.env.example`.

## Error Handling And Retries

The future real proxy should:

- Return clear client errors for invalid input.
- Return service errors for endpoint configuration problems.
- Use short timeouts and bounded retries for transient Vertex AI failures.
- Log request IDs and correlation IDs without logging sensitive payloads.
- Preserve enough metadata to trace Cloud Run and Vertex AI logs together.

## Logging And Correlation IDs

Cloud Run should generate or forward a request ID. That ID should be included in
application logs and, where practical, request metadata sent to Vertex AI. Later
evidence should show that a Cloud Run `/predict` request can be correlated with
the downstream Vertex AI prediction call.

## Evidence Screenshots

Capture these only after a real deployment:

- Cloud Run service environment variables.
- Cloud Run service account IAM permissions.
- Vertex AI endpoint ID.
- Cloud Run `/health` response showing vertex endpoint mode.
- Cloud Run `/predict` request and normalised response.
- Vertex AI endpoint prediction logs.
- Cloud Logging correlation evidence.
- Error handling or timeout evidence if available.

## Security Notes

- Do not commit service account keys.
- Use least privilege IAM for the Cloud Run service account.
- Use authenticated Cloud Run for non-public workloads.
- Keep project IDs, endpoint IDs, and service account identities parameterized or
  redacted in docs and evidence.
- Do not commit `.env` files.

## Limitations

R11 is a readiness and design milestone only. It uses a local dry-run Vertex AI
client stub, synthetic data, and placeholder configuration. It does not deploy
Cloud Run, call a live Vertex AI endpoint, or require credentials.
