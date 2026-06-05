-- Placeholder BigQuery monitoring queries.
-- Future milestones will compare recent prediction data against reference windows.

SELECT
  DATE(prediction_timestamp) AS prediction_date,
  COUNT(*) AS prediction_count,
  AVG(predicted_failure_probability) AS avg_failure_probability
FROM `project_id.dataset_id.batch_predictions`
GROUP BY prediction_date
ORDER BY prediction_date DESC;
