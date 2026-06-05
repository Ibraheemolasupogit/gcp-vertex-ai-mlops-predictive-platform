-- Placeholder BigQuery feature table definition for predictive maintenance.
-- Replace project and dataset names during a future cloud deployment milestone.

CREATE OR REPLACE TABLE `project_id.dataset_id.predictive_maintenance_features` AS
SELECT
  equipment_id,
  event_timestamp,
  temperature_c,
  vibration_mm_s,
  pressure_kpa,
  operating_hours,
  equipment_type,
  site_id
FROM `project_id.dataset_id.processed_equipment_events`
WHERE event_timestamp IS NOT NULL;
