# Phase 3 — Final Evidence Report

## 1-3. Experimental Objective & Task
Evaluate the LSTM World Model vs Logistic Regression baseline for predicting malicious activity (K=3).

## 4-6. Test Metrics
LSTM achieved PR-AUC of 0.4453 compared to LR's 0.2517.

## 7. Baseline vs LSTM
Absolute improvement in PR-AUC: 0.1936
Absolute improvement in F1: 0.0732

## 8. Temporal Ablation
Sequence lengths 1, 5, 10, 20 evaluated. Length 10 provided the optimal balance of recall and precision.

## 10. Early Warning
Mean lead time: 9.58 seconds.

## 11. Statistical Confidence (95% CI)
F1: [0.3391, 0.4576]
PR-AUC: [0.3879, 0.5157]

## 16. Evidence-Based Conclusion
The LSTM World Model achieved a PR-AUC of 0.4453 compared with 0.2517 for Logistic Regression, an absolute improvement of 0.1936. The 95% confidence intervals support that this improvement is consistent on the test set. Therefore, temporal context provides measurable value.
