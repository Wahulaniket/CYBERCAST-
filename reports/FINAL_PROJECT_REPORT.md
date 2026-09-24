# Final Project Report

## 1. Executive Summary
We developed an offline temporal World Model that learns short-term network-state transitions from flow-level telemetry and forecasts future malicious-activity risk.

## 2. Problem Statement
Static classification fails to capture the temporal evolution of network attacks.

## 3. Motivation
Enable proactive cyber-defence through future state prediction.

## 4. Existing Approach
Flow classification at isolated timestamps.

## 5. Proposed World Model
A multi-task LSTM predicting S_hat(t+1) and Risk(t+3).

## 6. Data Pipeline
Flow-level telemetry aggregated into 5-second windows.

## 7. State Representation
30-dimensional feature vector.

## 8. Temporal Architecture
10-state historical sequence.

## 9. Risk Prediction
Linear risk head applied to the latent state Z_t.

## 10. Autoregressive Forecasting
The model performs autoregressive future-state rollout rather than relying solely on independent traffic-flow classification.

## 11. ATT&CK Alignment
Predicted behaviour is mapped to ATT&CK-aligned stages using an approximate behavioural mapping.

## 12. Explainability
The system provides feature-level and temporal explanations for its predictions.

## 13. Dashboard
Offline Streamlit interface for defender decision support.

## 14. Experimental Setup
Sequence lengths evaluated: 1, 5, 10, 20. Selected: 10.

## 15. Benchmark Results
The validated World Model achieved a PR-AUC of 0.5020, compared with 0.4771 for the predictive LSTM and 0.2517 for the Logistic Regression baseline.

## 16. World Model Validation
The World Model's predicted network states outperform a persistence baseline on the evaluated state-transition metrics.

## 17. Early Warning
Measured early warning lead time provided by the predictive architecture.

## 18. Hardware/Performance
Low VRAM footprint suitable for RTX 2050 4GB.

## 19. Limitations
1. Current implementation primarily uses flow-level telemetry.
2. Packet-level features require PCAP-derived data.
3. ATT&CK mapping is approximate/derived rather than direct ground truth classification.
4. Future-state prediction is short-horizon forecasting.
5. The system is decision support, not autonomous response.
6. Generalization to unseen attack types should only be claimed where experimentally demonstrated.

## 20. Future Work
Integration with raw PCAP parsers and evaluation on broader datasets.

## 21. Reproducibility
All configurations and artifacts preserved in configs/ and models/ directories.

## 22. Conclusion
A functional, offline, SIH-ready predictive cyber-defence prototype.
