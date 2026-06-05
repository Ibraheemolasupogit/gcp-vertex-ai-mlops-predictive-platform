# Vertex AI Pipeline Design

Future Vertex AI Pipelines should mirror the local workflow rather than replace
it. Local components will become pipeline tasks only after they are implemented,
tested, and given explicit artifact contracts.

The target pipeline includes data preparation, feature creation, training,
evaluation, registry update, batch prediction, monitoring, and reporting steps.
