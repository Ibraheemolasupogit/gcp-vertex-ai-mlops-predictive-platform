# Pipeline Components Placeholder

The future local pipeline will be implemented as small, testable components.
Each component should accept explicit inputs, write predictable artifacts, and
be independently runnable before it is mapped to a Vertex AI Pipeline task.

| Local Component | Future Vertex AI Mapping | Purpose |
| --- | --- | --- |
| Data generation | Cloud Storage artifact preparation | Create sample predictive maintenance datasets |
| Ingestion | Dataflow / BigQuery | Load and validate input data |
| Features | BigQuery transformations | Create training and prediction features |
| Training | Vertex AI Training | Train candidate models |
| Registry | Vertex AI Model Registry | Track versions and approval metadata |
| Prediction | Vertex AI Batch Prediction | Score equipment failure risk |
| Monitoring | Vertex AI Model Monitoring | Detect drift and retraining signals |
