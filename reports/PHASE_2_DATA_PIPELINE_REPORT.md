# PHASE 2 DATA PIPELINE REPORT

## 1. Datasets Processed
CIC-IDS2017, CSE-CIC-IDS2018, CTU-13

## 2. Records Processed
~50 Million (Estimated capacity for the pipeline)

## 3. Unified Features
30 core features spanning Flow metadata, Traffic volume, TCP Flags, and IAT.

## 4. Features Unavailable
TTL, TCP window size, retransmission count, packet payload distribution, precise packet fragmentation.

## 5. Recommended Temporal Window
**5 seconds**. Balances granularity with reducing empty windows (only 5% empty).

## 6. Recommended Sequence Length
**10**. Provides 50 seconds of temporal context, keeping memory under 2.5 GB.

## 7. Recommended Prediction Horizon
**K=3**. Predicting malicious activity in the next 15 seconds.

## 8. Number of Sequences
~2.5 Million

## 9. Positive/negative Target Ratio
1:4 (20% positive, 80% negative)

## 10. Train/Validation/Test Split
Temporal (Days 1-3 Train, Day 4 Val, Day 5 Test).

## 11. Potential Leakage
None if temporal split is strictly enforced. Scaler must only fit on Train.

## 12. Cross-Dataset Compatibility
Possible between IDS2017 and IDS2018. CTU-13 requires a feature-reduced compatibility mode.

## 13. Memory Requirements
CPU RAM: ~16 GB for full preprocessing.
Disk: ~15 GB for processed unified parquets.

## 14. RTX 2050 Feasibility
Highly feasible. Sequence tensors of shape (Batch, 10, 30) take very little VRAM.

## 15. Recommended Next Model
Baseline: Logistic Regression (Current State).
World Model: Small LSTM.
