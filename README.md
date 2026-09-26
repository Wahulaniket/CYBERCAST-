# CyberCast

### Predictive Cyber Defence Using Temporal Network World Models

CyberCast is an offline AI-based predictive cyber-defence system that learns how network states evolve over time and forecasts future attack risk.

Unlike traditional intrusion detection systems that classify individual flows as benign or malicious, CyberCast models network traffic as a **temporal process**. It converts flow-level and packet-level telemetry into time-windowed network states, learns state-transition dynamics using an LSTM World Model, performs forward simulation, and presents the predicted future risk and supporting evidence through a SOC-oriented dashboard.

---

## 1. Problem

Traditional network intrusion detection commonly treats network traffic as independent observations:

```text
Network Flow → Benign / Malicious
```

This loses the temporal structure of an attack.

Real intrusions evolve through sequences such as:

```text
Reconnaissance
      ↓
Discovery
      ↓
Initial Access
      ↓
Command & Control
      ↓
Lateral Movement / Exfiltration
```

CyberCast instead models the network as an evolving state:

```text
Sₜ → Sₜ₊₁ → Sₜ₊₂ → ...
```

and learns a predictive approximation of:

```text
P(Sₜ₊₁ | Sₜ)
```

The model can then roll forward from the current observed state and estimate future attack risk.

---

# 2. CyberCast Architecture

```text
              Network Telemetry
                     │
          ┌──────────┴──────────┐
          │                     │
     Flow Features        Packet Features
          │                     │
          └──────────┬──────────┘
                     ↓
             5-second windows
                     ↓
          55-D Network State
                     ↓
          10-State Temporal Context
                     ↓
              LSTM World Model
               /           \
              /             \
     State Transition     Future Risk
       Decoder              Head
              \             /
               \           /
                K-Step Rollout
                     ↓
          Future Risk Trajectory
                     ↓
       ATT&CK-Aligned Derived Stage
                     ↓
            Feature Attribution
                     ↓
              SOC Dashboard
```

---

# 3. Key Capabilities

### Temporal Network Modelling

CyberCast represents network behaviour using a sequence of 55-dimensional network states.

Each state represents a non-overlapping 5-second observation window.

The model uses the previous 10 states:

```text
10 × 5 seconds = 50 seconds
```

of temporal context.

### World Model

The core model is an LSTM-based World Model containing:

* temporal encoder
* state-transition decoder
* future-risk prediction head
* autoregressive rollout

The model simultaneously learns:

1. how the network state changes;
2. whether future states indicate increasing attack risk.

### Forward Simulation

CyberCast supports:

```text
K = 1
K = 3
K = 5
K = 10
```

step autoregressive rollout.

This allows the system to examine possible future network-state trajectories rather than only classifying the current observation.

### Explainability

CyberCast uses gradient-based feature attribution to identify traffic features contributing to the prediction.

Examples include:

* TCP flag behaviour
* destination-port activity
* packet timing
* endpoint statistics
* TTL characteristics
* payload characteristics
* retransmission indicators

### ATT&CK-Aligned Interpretation

The dashboard maps predicted behaviour to an **ATT&CK-aligned derived stage**.

Supported stages can include:

* Reconnaissance
* Discovery
* Initial Access
* Command & Control

The mapping is an interpretation derived from the observed/predicted network behaviour.

It is **not claimed as ground-truth MITRE ATT&CK annotation**.

---

# 4. Input Data

CyberCast supports network telemetry derived from:

* PCAP
* PCAPNG
* flow records
* packet-level telemetry

### Flow-level features

Examples include:

* source IP
* destination IP
* source port
* destination port
* protocol
* TCP flags
* bytes
* packets
* flow duration
* packet/flow timing
* endpoint statistics
* bidirectional behaviour

### Packet-level features

Examples include:

* TTL
* TTL variance
* TCP window size
* fragmentation
* payload size
* packet timing
* destination-port behaviour
* retransmission indicators
* TCP flag statistics

---

# 5. Data Processing

The production pipeline is:

```text
PCAP / Flow Telemetry
        ↓
Packet + Flow Feature Extraction
        ↓
Global 5-second Aggregation
        ↓
55-D Network States
        ↓
10-State Sequence
        ↓
StandardScaler
        ↓
World Model
```

The production model requires:

```text
55 features
10 consecutive temporal states
5-second state interval
```

No artificial traffic is injected into the model.

---

# 6. Model Architecture

Current validated World Model v2:

| Component         | Configuration         |
| ----------------- | --------------------- |
| Input dimension   | 55                    |
| Temporal sequence | 10 states             |
| Window size       | 5 seconds             |
| Context           | 50 seconds            |
| Architecture      | LSTM                  |
| Hidden dimension  | 64                    |
| State decoder     | Next-state prediction |
| Risk head         | Future attack risk    |
| Optimizer         | Adam                  |
| Learning rate     | 0.001                 |
| State loss        | Huber                 |
| Risk loss         | Binary Cross Entropy  |
| Loss weights      | 0.5 state / 1.0 risk  |
| Gradient clipping | Enabled               |
| Early stopping    | Enabled               |

The state-transition component predicts the next network state.

The risk head predicts future attack risk at the model's prediction horizon.

---

# 7. Training Dataset

The validated model was trained and evaluated using traffic derived from the CIC-IDS2017 PCAP collection.

The temporal split was:

```text
TRAIN
Monday
Tuesday
Wednesday

VALIDATION
Thursday

TEST
Friday
```

The Friday test set was temporally held out.

The test set also contained attack categories that were not represented in the training days, including:

* DDoS
* PortScan
* Botnet

This provides a held-out-category evaluation, but should not be interpreted as universal unseen-attack generalisation.

---

# 8. Leakage Prevention

The training pipeline uses:

* chronological/day-based splitting
* training-only scaler fitting
* temporal sequence construction
* no test-state leakage into training
* no teacher-forcing leakage during autoregressive evaluation

The independent Phase 9F audit verified:

```text
DATA VALIDATION          PASS
TEST METRICS             PASS
CHECKPOINT INTEGRITY     PASS
EXPLAINABILITY            PASS
CLAIM AUDIT               PASS
```

---

# 9. Benchmark Results

The World Model was compared against a Logistic Regression baseline using the same feature representation.

### Test performance

| Metric              | Logistic Regression | CyberCast World Model |
| ------------------- | ------------------: | --------------------: |
| PR-AUC              |              0.5857 |            **0.6873** |
| F1                  |              0.2569 |            **0.3181** |
| Precision           |                   — |            **0.9261** |
| Recall              |                   — |            **0.1920** |
| False Positive Rate |                   — |            **0.0092** |

Absolute improvement:

```text
PR-AUC: +0.1015
F1:     +0.0612
```

The World Model therefore demonstrated improved ranking and F1 performance over the Logistic Regression baseline on the held-out test set.

At the default 0.5 threshold, recall remains relatively low. Threshold selection therefore represents a practical precision/recall trade-off for deployment.

---

# 10. Attack-Specific Results

Held-out Friday test performance:

| Attack Category |     F1 |
| --------------- | -----: |
| DDoS            | 0.9054 |
| Botnet          | 0.1814 |
| PortScan        | 0.1602 |

The results show that performance varies substantially by attack category.

CyberCast should therefore not be interpreted as equally effective against every attack type.

---

# 11. State-Transition Prediction

The World Model was also evaluated on next-state prediction.

### World Model

```text
MAE  = 0.4315
RMSE = 1.0750
```

### Persistence baseline

```text
MAE  = 0.4407
RMSE = 1.0889
```

These metrics are measured in the **scaled feature space**.

The World Model performed better than the persistence baseline for next-state prediction.

---

# 12. Autoregressive Rollout

The World Model supports recursive future-state simulation.

| Horizon |   RMSE |
| ------- | -----: |
| K=1     | 0.7737 |
| K=3     | 0.8044 |
| K=5     | 0.8194 |
| K=10    | 0.8438 |

These rollout metrics are also measured in scaled state space.

The increasing error across longer horizons illustrates the expected accumulation of uncertainty during recursive prediction.

---

# 13. Early Warning

The evaluated system produced a:

**15-second mean measured early-warning lead time**

on the evaluated test setup.

This is an empirical result from the evaluation procedure and should not be interpreted as a guaranteed warning time for arbitrary networks or attacks.

---

# 14. Explainability

For every prediction, CyberCast can calculate feature attribution using gradients.

The dashboard presents:

```text
WHY IS THE MODEL ALERTING?
```

and displays the traffic features contributing most strongly to the prediction.

The explanation pipeline operates over the temporal sequence, allowing analysts to investigate both:

* which features matter;
* when those features became influential.

---

# 15. SOC Dashboard

CyberCast provides a React + FastAPI SOC interface.

The dashboard is designed around the analyst workflow:

```text
What is happening?
        ↓
How serious is it?
        ↓
What is likely next?
        ↓
Why is the model alerting?
        ↓
What changed over time?
        ↓
What evidence should I investigate?
```

Main dashboard elements include:

* Future Threat Risk
* Future Threat Trajectory
* ATT&CK-aligned derived stage
* temporal context
* model forecast
* feature attribution
* temporal changes
* network evidence
* investigation focus
* World Model visualization
* model performance
* system health

---

# 16. Operating Modes

CyberCast supports three analysis modes.

### Demo Replay

Uses the validated demonstration dataset for deterministic presentation.

```text
DEMO REPLAY
```

### Lab PCAP

Analyzes an uploaded PCAP/PCAPNG capture.

```text
LAB PCAP
```

The PCAP is processed through the same feature and inference pipeline without retraining the model.

### Live Lab

Consumes live authorized laboratory network telemetry.

```text
LIVE LAB
```

The live pipeline is:

```text
Network Traffic
      ↓
Packet Capture
      ↓
5-second State
      ↓
10-State Buffer
      ↓
World Model
      ↓
Prediction
      ↓
WebSocket
      ↓
React Dashboard
```

The live mode is intended for an isolated, authorized cyber-range environment.

---

# 17. Live Lab Demonstration

A recommended demonstration is:

```text
Normal Traffic
      ↓
Reconnaissance
      ↓
Port Scanning
      ↓
Service Discovery
      ↓
CyberCast Prediction
```

The dashboard continuously updates the:

* future-risk trajectory
* temporal context
* ATT&CK-aligned stage
* network evidence
* feature attribution

The attack activity must be performed only against an intentionally configured lab target.

---

# 18. Project Structure

```text
cyberCast2/
│
├── backend/
│   ├── main.py
│   ├── schemas.py
│   └── services/
│       ├── inference_service.py
│       └── live_capture_service.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── hooks/
│   │   │   └── useLiveCapture.ts
│   │   └── pages/
│   │       ├── OverviewPage.tsx
│   │       ├── WorldModelPage.tsx
│   │       ├── ModelPerformancePage.tsx
│   │       └── SystemHealthPage.tsx
│   └── package.json
│
├── src/
│   └── world_model_v2/
│       └── inference.py
│
├── models/
│   ├── world_model_packet_v2.pt
│   ├── scaler_packet_v2.pkl
│   ├── world_model_packet_v2_config.json
│   └── feature_schema_packet_v2.json
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── requirements.txt
│
└── README.md
```

---

# 19. Installation

## Requirements

Recommended environment:

* Windows 10/11
* Python 3.11
* Node.js
* npm
* NVIDIA GPU optional
* Npcap required for Windows live packet capture
* Scapy for live packet capture

The system can run inference on CPU.

GPU acceleration is optional.

---

## Python environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 20. Start the Backend

From the project root:

```powershell
uvicorn backend.main:app --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/api/health
```

---

# 21. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 22. API Endpoints

### Health

```http
GET /api/health
```

### Model information

```http
GET /api/model-info
```

### Demo data

```http
GET /api/demo
```

### Analyze telemetry

```http
POST /api/analyze
```

### Validate input

```http
POST /api/validate
```

### Live capture status

```http
GET /api/live/status
```

### Start live capture

```http
POST /api/live/start
```

### Stop live capture

```http
POST /api/live/stop
```

### Live WebSocket

```text
ws://localhost:8000/ws/live
```

---

# 23. Model Artifacts

The production inference engine uses:

```text
models/world_model_packet_v2.pt
models/scaler_packet_v2.pkl
models/world_model_packet_v2_config.json
models/feature_schema_packet_v2.json
```

These artifacts define the validated production model and preprocessing configuration.

The model expects exactly:

```text
55 features
```

with the schema defined in:

```text
feature_schema_packet_v2.json
```

---

# 24. Reproducibility

The primary training configuration is:

```text
Input features:       55
Sequence length:      10
Window size:          5 sec
Hidden size:          64
Learning rate:        0.001
Optimizer:            Adam
State loss weight:    0.5
Risk loss weight:     1.0
```

Training data split:

```text
Train:
Monday + Tuesday + Wednesday

Validation:
Thursday

Test:
Friday
```

The scaler is fitted using training data only.

---

# 25. Hardware

The development environment used:

```text
CPU:
Intel Core i5 Laptop CPU

GPU:
NVIDIA RTX 2050 Laptop GPU

VRAM:
4 GB

Operating System:
Windows
```

The inference engine supports CPU execution and can automatically use the available GPU.

---

# 26. Performance

Validated inference measurements include:

```text
CPU model inference:       ~0.0072 sec
GPU model inference:       ~0.0007 sec
GPU end-to-end inference:  ~0.0124 sec
Peak GPU VRAM:             ~26 MB
```

These measurements are environment-specific and should not be interpreted as universal deployment performance.

---

# 27. Security and Safety

CyberCast is designed as a defensive analysis system.

The Live Lab mode does not automatically launch attacks.

For live demonstrations:

* use an isolated VM network;
* use an intentionally configured target;
* perform testing only on systems you own or are authorized to test;
* do not scan public systems;
* do not use the Windows host as an attack target unless it has explicitly been configured as a safe lab target.

---

# 28. Limitations

CyberCast currently has several important limitations.

### Dataset dependency

The primary training/evaluation data is based on CIC-IDS2017-derived traffic.

Traffic distributions in real enterprise environments may differ substantially.

### Attack-category variability

Performance varies across attack categories.

DDoS performance was substantially stronger than Botnet and PortScan performance in the evaluated test set.

### Recall

At the default 0.5 threshold:

```text
Recall = 0.1920
```

Therefore the system should not be described as detecting all attacks.

### ATT&CK mapping

The dashboard's stage is:

```text
ATT&CK-aligned derived interpretation
```

rather than ground-truth MITRE ATT&CK labeling.

### Early warning

The measured mean lead time was 15 seconds in the evaluated setup.

It is not a guaranteed warning time for arbitrary attacks.

### Generalisation

The Friday test set included held-out attack categories, but a completely independent external-PCAP deployment evaluation has not been established.

### State metrics

State-transition and rollout error metrics are reported in scaled feature space.

---

# 29. Key Contribution

CyberCast moves from:

```text
Static intrusion classification
```

toward:

```text
Temporal network-state modelling
             +
Future-state simulation
             +
Attack progression interpretation
             +
Explainable SOC decision support
```

The central idea is:

> **Don't only ask whether the current traffic is malicious. Learn how the network is evolving and estimate where that trajectory is heading.**

---

# 30. Project Status

Current validated status:

```text
World Model v2             READY
Inference Engine           READY
Feature Schema             VALIDATED
Autoregressive Rollout     VALIDATED
Explainability             VALIDATED
ATT&CK Mapping             VALIDATED
FastAPI Backend             READY
React SOC Dashboard         READY
Live Lab API                READY
Frontend Build              PASS
Offline Inference           PASS
```

The Live Lab feature provides an additional experimental pathway for evaluating CyberCast against authorized laboratory traffic.

---

# 31. SIH Deliverables

CyberCast is prepared around the required SIH deliverables:

```text
1. Source Code
2. README
3. Architecture Document
4. Technical Presentation
5. Demonstration Video
```

Recommended presentation narrative:

```text
Problem
  ↓
Temporal World Model
  ↓
Predictive Rollout
  ↓
Explainability
  ↓
SOC Dashboard
  ↓
Measured Results
  ↓
Live Lab Demonstration
```

---

## CyberCast

**Predict the trajectory. Explain the evidence. Support the defender.**
