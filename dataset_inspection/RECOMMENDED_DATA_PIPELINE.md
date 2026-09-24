# Recommended Data Pipeline
RAW DATA -> Filter out broken rows -> Keep Timestamps, IPs, Ports, Protocol, Flow Stats
-> Sort by Timestamp -> Group by 5-second Time Windows
-> Extract aggregate statistics per window (State S_t)
-> Construct sequences of length L=10
-> Target: Malicious label at T+K (K=1 to 5)
-> Model: Small LSTM or Temporal Transformer
-> Explainability: SHAP on the aggregated features
