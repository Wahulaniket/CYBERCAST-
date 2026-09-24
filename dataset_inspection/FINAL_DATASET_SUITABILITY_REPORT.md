# Dataset Suitability Report

## 1. Executive Summary
PARTIALLY SUITABLE. The datasets provide excellent flow-level features and temporal timestamps, making sequence generation and transition learning feasible. However, they completely lack raw packet-level features (TTL, retransmissions), which limits some PS requirements.

## 2. Dataset Overview
Datasets present: CIC-IDS2017, CSE-CIC-IDS2018 (archive), CTU-13. 

## 3. Dataset Statistics
Total Records: >50 Million. Total Size: ~10 GB. 

## 4-6. Feature Coverage
Excellent flow coverage. Zero packet-level PCAP coverage.

## 7-9. Temporal and Attack
Timestamps exist. Attacks can be reconstructed into timelines. MITRE ATT&CK mapping is approximate but feasible for Discovery -> Initial Access -> C2 -> Impact.

## 10. Network State Representation
OPTION A (Fixed-dimensional feature vector per time window) is most feasible. 

## 11-13. Machine Learning Feasibility
State Transition Learning is Good. 
Future Prediction is Feasible (predicting malicious window at T+K).
Generalisation can be evaluated via hold-out attack types.

## 19. Hardware Feasibility
RTX 2050 (4GB VRAM) restricts model size. LSTM and small Temporal Transformers are feasible. GNNs are likely out of memory for large graphs. 

## 23. Final Suitability Score
Overall World Model Suitability: 7/10
- Temporal: 8/10
- Attack timeline: 7/10
- Feature coverage: 6/10 (No packet data)
- Future prediction: 8/10
- Explainability: 8/10
- Hardware feasibility: 6/10

## 24. Exact Next Steps
Proceed with dataset aggregation, filtering out purely packet-level PS requirements, and design the temporal window sequence generator.
