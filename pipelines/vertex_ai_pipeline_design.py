"""Placeholder for future Vertex AI Pipeline component mapping.

This module intentionally contains no cloud execution code. Later milestones
can translate local steps into Vertex AI Pipeline components once the local
workflow is implemented and tested.
"""

LOCAL_TO_VERTEX_AI_MAPPING = {
    "data_generation": "Cloud Storage sample artifact preparation",
    "ingestion": "Dataflow or BigQuery ingestion component",
    "features": "BigQuery feature table component",
    "training": "Vertex AI custom training job",
    "registry": "Vertex AI Model Registry upload and metadata",
    "prediction": "Vertex AI Batch Prediction job",
    "monitoring": "Vertex AI Model Monitoring and BigQuery checks",
}
