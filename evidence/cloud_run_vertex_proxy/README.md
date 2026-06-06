# Cloud Run To Vertex AI Proxy Evidence

Add real screenshots or command outputs here only after a real Cloud Run to
Vertex AI endpoint proxy demonstration has been performed. Do not add fake
screenshots, credentials, service account keys, or unredacted project
identifiers.

Evidence to capture later:

- Cloud Run service environment variables showing proxy mode.
- Cloud Run service account permissions for Vertex AI prediction.
- Vertex AI endpoint ID.
- Cloud Run `/health` response showing vertex endpoint mode.
- `/predict` request sent through Cloud Run.
- Vertex AI endpoint prediction logs.
- Cloud Logging correlation ID evidence across Cloud Run and Vertex AI.
- Error handling or timeout evidence if available.

R11 only prepares the proxy design and local stub interface. It does not deploy
Cloud Run, call Vertex AI, or require credentials.
