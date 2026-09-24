## SLIDE 1 — PROBLEM
> From Intrusion Detection to Predictive Cyber Defence
* Traditional IDS is largely observation/classification oriented
* Attack progression unfolds over time
* Static flow classification misses temporal relationships
* Need to forecast malicious activity before later stages
Traffic → State → Temporal Evolution → Future Risk

## SLIDE 2 — SOLUTION
> Temporal World Model
Network Telemetry → 5s State Windows → 10-Step Sequence → LSTM World Model → Latent Network State → Future State + Risk
* 30-dimensional state
* 5-second window
* 10-state sequence
* K≤10 rollout

## SLIDE 3 — HOW IT WORKS
> Predicting Attack Progression
Current Network State → World Model → Autoregressive Rollout → Future Network States → Risk Forecast → ATT&CK-Aligned Stage
* Feature attribution
* Temporal importance
* Stage interpretation

## SLIDE 4 — RESULTS
> Experimental Results
* World Model PR-AUC: 0.5020
* LSTM PR-AUC: 0.4771
* Logistic Regression PR-AUC: 0.2517
* Mean early warning lead time: 9.58 seconds
* State prediction outperforms persistence baseline.

## SLIDE 5 — DEMO / IMPACT
> Defender Decision Support
Telemetry → Risk Forecast → Attack Stage → Why? → Defender Action
* Offline operation
* CPU/GPU support
* Explainability
* SOC-style dashboard
* Enterprise/CII applicability
* Limitation: Flow-level data; approximate mappings.
