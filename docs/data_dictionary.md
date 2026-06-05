# Data Dictionary

Milestone 2 introduces fully synthetic predictive maintenance datasets. The
data is generated locally from configuration and does not represent real
equipment, customers, facilities, or cloud resources.

## machines.csv

Purpose: Describes the synthetic equipment fleet and baseline operating profile.

Grain: One row per machine.

Primary key: `machine_id`

Key relationships: Referenced by `sensor_readings.machine_id`,
`maintenance_events.machine_id`, and `failure_events.machine_id`.

| Column | Description |
| --- | --- |
| `machine_id` | Synthetic machine identifier. |
| `machine_type` | Equipment category such as pump, compressor, conveyor, generator, or hydraulic press. |
| `installation_date` | Synthetic installation date used to derive age-related risk. |
| `site_id` | Synthetic facility identifier. |
| `manufacturer` | Synthetic manufacturer name. |
| `expected_lifetime_years` | Expected operating lifetime for the machine type. |
| `criticality` | Operational impact category: low, medium, high, or critical. |
| `baseline_temperature` | Normal operating temperature profile for the machine. |
| `baseline_vibration` | Normal vibration profile for the machine. |
| `baseline_pressure` | Normal pressure profile for the machine. |

Generation notes: Baselines vary by machine type, manufacturer, site,
criticality, and machine age. Values are intentionally plausible, not calibrated
to real equipment.

## sensor_readings.csv

Purpose: Provides time-series sensor readings for future ingestion, feature
engineering, training, and monitoring work.

Grain: One row per machine per configured reading timestamp.

Primary key: `reading_id`

Key relationships: `machine_id` references `machines.machine_id`.

| Column | Description |
| --- | --- |
| `reading_id` | Synthetic sensor reading identifier. |
| `machine_id` | Machine associated with the reading. |
| `timestamp` | Reading timestamp at the configured frequency. |
| `temperature` | Synthetic operating temperature. |
| `vibration` | Synthetic vibration level. |
| `pressure` | Synthetic pressure measurement. |
| `runtime_hours` | Accumulated runtime hours. |
| `energy_consumption` | Synthetic energy consumption value. |
| `operating_load` | Relative machine load between low and full utilization. |

Generation notes: Readings include normal variation, type-specific operating
profiles, increased runtime, and degradation patterns before generated failures.

## maintenance_events.csv

Purpose: Captures synthetic maintenance activity for future lifecycle and
retraining workflows.

Grain: One row per maintenance event.

Primary key: `maintenance_id`

Key relationships: `machine_id` references `machines.machine_id`.

| Column | Description |
| --- | --- |
| `maintenance_id` | Synthetic maintenance event identifier. |
| `machine_id` | Machine maintained. |
| `maintenance_date` | Date maintenance occurred. |
| `maintenance_type` | Preventive, corrective, inspection, or emergency maintenance. |
| `technician_team` | Synthetic maintenance team identifier. |
| `downtime_hours` | Downtime caused by the maintenance event. |
| `parts_replaced` | Synthetic part category replaced during maintenance. |
| `maintenance_cost` | Synthetic maintenance cost. |
| `risk_reduction_score` | Approximate future risk reduction from the event. |

Generation notes: Preventive and inspection events are planned. Corrective and
emergency events are linked to generated failures, with higher costs and
downtime for more severe work.

## failure_events.csv

Purpose: Records synthetic failures that can later be used for labels,
evaluation, monitoring, and retraining examples.

Grain: One row per failure event.

Primary key: `failure_id`

Key relationships: `machine_id` references `machines.machine_id`.

| Column | Description |
| --- | --- |
| `failure_id` | Synthetic failure identifier. |
| `machine_id` | Machine that failed. |
| `failure_date` | Date the failure occurred. |
| `failure_type` | Failure category such as overheating, bearing wear, pressure system failure, electrical fault, or vibration-related failure. |
| `severity` | Minor, moderate, major, or critical severity. |
| `root_cause` | Synthetic root cause associated with the failure category. |
| `downtime_hours` | Downtime caused by the failure. |
| `repair_cost` | Synthetic repair cost. |

Generation notes: Failure probability is influenced by age and criticality.
Sensor readings in the days before failures include temperature, vibration, and
pressure anomalies where relevant.
