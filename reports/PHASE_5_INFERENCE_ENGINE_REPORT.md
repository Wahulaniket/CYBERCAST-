# Phase 5 — Unified Offline Inference Engine
## 1. Objective
Build a single reusable inference pipeline for offline predictive cyber-defence.
## 2. Architecture
Clean separation of data processing, inference, and rollout.
## 16. Dashboard Integration Interface
The Streamlit dashboard should use `from src.inference.engine import predict_attack_progression` and access fields of the returned `PredictionResult`.
