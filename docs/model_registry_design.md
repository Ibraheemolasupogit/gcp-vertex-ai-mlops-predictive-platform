# Model Registry Design

The local registry will track model version, training data reference, metrics,
approval state, and artifact paths. This creates a clean promotion workflow
before any Vertex AI Model Registry integration is added.

Registry states are expected to include candidate, approved, archived, and
rejected.
