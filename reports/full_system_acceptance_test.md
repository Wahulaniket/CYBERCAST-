# Full System Acceptance Test Report

## 1. Environment Verification
- **Python**: 3.11.9
- **PyTorch**: 2.5.1+cu121
- **Streamlit**: 1.64.0
- **Pandas**: 2.2.3
- **NumPy**: 1.26.4
- **Scikit-learn**: 1.8.0
- **Plotly**: 5.24.1
- **CUDA Available**: True
- **GPU Name**: NVIDIA GeForce RTX 2050
- **GPU Memory**: 4.29 GB
- **Artifacts Present**: Verified all critical model artifacts (weights, scaler, schema).

## 2. Model Integrity
- **Input Dimension**: 55
- **Hidden Size**: 64
- **State Decoder**: Present
- **Risk Head**: Present
*Model loads accurately without requiring re-training or weight modification.*

## 3. Data Validation & Demo Data
- **Rows Processed**: 5765
- **Features Extracted**: 55 core features
- **Timestamps**: Present (`window_start`)
- **Format**: Valid `global_states_v2` sequences

## 4. Full Inference
- Result keys accurately populated with strictly typed `PredictionResult`: current risk, risk forecast, predicted states, predicted stage, stage confidence, top features, temporal importance, input quality, and model metadata.

## 5. Autoregressive Rollout
- $K=1$ Output states: 1 (Execution time: 0.0065s)
- $K=3$ Output states: 3 (Execution time: 0.0056s)
- $K=5$ Output states: 5 (Execution time: 0.0071s)
- $K=10$ Output states: 10 (Execution time: 0.0112s)
*Future states are recursively fed back into the LSTM. No ground-truth leakage.*

## 6. Explainability
- Valid gradient matrix dimensions ($10 \times 55$).
- Output temporal heatmap mappings generated natively from tensor gradients.

## 7. ATT&CK Mapping
- Derived mapping accurately labels `INSUFFICIENT_EVIDENCE` (or appropriate stage) with explicit "ATT&CK-aligned derived stage" metadata caveat.

## 8. Dashboard Validation
- Streamlit application functionally isolated and correctly imports without parameter duplication (`tests/test_dashboard_integration.py` passing).
- Offline capabilities verified.

## 9. Invalid Input Handling
- Gracefully throws `ValueError` on 54 features (missing feature simulation).
- Gracefully throws `ValueError` on temporal gap violations, enforcing the continuous 5-second boundary required for the L=10 sequential context.

## 10. Performance Metrics
### CPU
- **End-to-End Latency**: 0.0087 s
- **RAM Peak Usage**: 575.78 MB

### GPU
- **End-to-End Latency**: 0.0120 s
- **Model Inference Latency**: 0.0115 s
- **VRAM Peak Usage**: 26.08 MB

## 11. Consistency
- Repeated inferences over 3 identical sequences resulted in `0.0` numerical variance, proving strict deterministic execution on `weights_only` loads.

## 12. Final Validation Check
- The mathematical boundaries and validations align perfectly with the Phase 9F requirements.
- The system is physically complete, operating in under 15 milliseconds end-to-end securely offline with no internet or REST dependencies.
