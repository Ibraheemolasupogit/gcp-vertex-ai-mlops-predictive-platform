# Explainability

Explainability matters in predictive maintenance because maintenance teams need
to understand why a model flags a machine as risky before they schedule
inspection, downtime, or part replacement. A prediction should support an
operational decision, not behave like a black box.

## Local Explainability Approach

The current local model training stage writes feature importance values to
`outputs/feature_importance.csv`. This gives a lightweight interpretation layer
for the RandomForest classifier by showing which engineered features contributed
most strongly to splits across the trained trees.

This is not a full causal explanation, but it is useful portfolio evidence for
understanding whether the model is relying on plausible maintenance signals.

## Interpreting Important Signals

Likely important signals in a predictive maintenance setting include:

- Temperature: rising operating temperature can indicate overheating, friction,
  cooling issues, or abnormal load.
- Vibration: elevated vibration can indicate bearing wear, imbalance, or
  mechanical degradation.
- Pressure: pressure instability can point to pump, hydraulic, pneumatic, or
  seal problems.
- Runtime: accumulated runtime can reflect wear exposure and duty cycle.
- Maintenance history: recent maintenance, downtime, cost, and risk reduction
  scores can help represent machine condition and intervention history.

The engineered feature table also includes rolling statistics and deltas from
machine baselines, which help distinguish unusual behavior from normal
machine-specific operating profiles.

## Vertex AI Mapping

In a future GCP deployment, explainability evidence could map to:

- Vertex AI Explainable AI for supported model and serving configurations.
- Feature attribution or model monitoring reports attached to Model Registry
  metadata.
- Monitoring dashboards that compare risk drivers over time.
- Model cards or evaluation reports that summarize important features,
  limitations, and intended use.

## Limitations

The current data is fully synthetic, so feature importance should be treated as
workflow evidence rather than production insight. The repository does not claim
that the learned patterns reflect real equipment behavior or validated
production reliability.
