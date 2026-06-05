-- Placeholder BigQuery training view for model development.
-- Future milestones will add labels, split logic, and feature windows.

CREATE OR REPLACE VIEW `project_id.dataset_id.predictive_maintenance_training_view` AS
SELECT
  equipment_id,
  event_timestamp,
  temperature_c,
  vibration_mm_s,
  pressure_kpa,
  operating_hours,
  equipment_type,
  site_id,
  failure_within_window
FROM `project_id.dataset_id.predictive_maintenance_features`;
