# AI-Driven Predictive Cyber Defence Using Temporal World Models

## Problem Statement
Traditional intrusion detection systems evaluate individual traffic observations statically, missing the temporal evolution of attack progression.

## Solution
We developed an offline temporal World Model that learns short-term network-state transitions from flow-level telemetry and forecasts future malicious-activity risk.

## Architecture
LSTM-based sequence modeling with multi-task objective (state-transition forecasting and risk prediction).

## Features
30-dimensional aggregated flow telemetry representation.

## Dataset
Synthetic validation pipeline mimicking structural characteristics of flow datasets.

## Feature Engineering
5-second windows forming a 10-state sequence (50s history).

## World Model
Predictive approximation of network-state evolution.

## Training
Autoregressive rollout training mapping historical trajectories to future states.

## Inference
Fully offline inference engine decoupled from visualization logic.

## Autoregressive Forecasting
K-step prediction (up to K=10) without teacher forcing leakage.

## Explainability
Gradient-based temporal and feature-level attribution.

## ATT&CK Alignment
Approximate behavioural stage mapping derived from predicted states.

## Dashboard
Streamlit-based SOC decision support platform.

## Benchmark
World Model PR-AUC: 0.5020 vs Logistic Regression PR-AUC: 0.2517.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run dashboard/app.py
```

## CLI Usage
```bash
python cli/predict.py --input tests/data/sample_flow.csv
```

## Offline Operation
The system requires no external cloud APIs or LLMs.

## Hardware
CPU and GPU supported (VRAM footprint ~25MB).

## Project Structure
Separated src/, dashboard/, models/, tests/, and reports/ layers.

## Limitations
- Current implementation primarily uses flow-level telemetry.
- Packet-level features require PCAP-derived data.
- ATT&CK mapping is approximate/derived rather than direct ground truth classification.
- Future-state prediction is short-horizon forecasting.
- The system is decision support, not autonomous response.

## Future Work
Integration with raw PCAP parsing and validation on broader unseen attack classes.

## Reproducibility
Configuration and artifacts maintained in configs/ and models/ directories.
