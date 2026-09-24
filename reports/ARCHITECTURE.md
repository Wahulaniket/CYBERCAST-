# AI Cyber Defence Architecture

## 1. Problem
Traditional intrusion detection often evaluates individual traffic observations. The project instead models network behaviour as a temporal process, forecasting malicious activity before later stages.

## 2. Proposed Solution
A temporal World Model that learns short-term network-state transitions and forecasts future malicious-activity risk.

## 3. Input
Flow-level telemetry aggregated into a 30-dimensional state representation. 

## 4. Temporal State
- 5-second windows
- 10-state sequence
- 50-second historical context

## 5. World Model
- LSTM sequence encoder
- Latent network state extraction (Z_t)
- State transition decoder predicting S_hat(t+1)
- Risk prediction head

## 6. Future Simulation
Autoregressive rollout feeding predicted S_hat(t+1) back into the sequence to forecast K steps ahead, without future ground-truth leakage.

## 7. Explainability
Feature attribution via gradients through time, allowing temporal importance and feature contribution to be surfaced to the defender.

## 8. ATT&CK Alignment
Approximate behavioural mapping derived from predicted network-state characteristics. It is not direct ground-truth classification.

## 9. Dashboard
Offline Streamlit defender interface for decision support.

## 10. Limitations
Current implementation primarily uses flow-level temporal telemetry. Packet-level features require PCAP-derived input and are not fabricated when unavailable. ATT&CK mapping is approximate.
