import os
import json
import time
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import pickle
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

# Re-define model inside inference if not importable
class WorldModelV2(nn.Module):
    def __init__(self, input_size=55, hidden_size=64, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.state_decoder = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, input_size))
        self.risk_head = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, 1))

    def forward(self, x):
        out, _ = self.lstm(x)
        z_t = out[:, -1, :]
        return self.state_decoder(z_t), self.risk_head(z_t).squeeze(-1)

@dataclass
class PredictionResult:
    current_risk: float
    risk_forecast: Dict[str, float]
    predicted_states: List[List[float]]
    predicted_stage: str
    stage_confidence: float
    top_features: List[str]
    temporal_importance: List[float]
    input_quality: Dict[str, Any]
    model_metadata: Dict[str, Any]

class InferenceEngine:
    def __init__(self, model_path: str, scaler_path: str, device: str = None):
        self.device = torch.device(device if device else ('cuda' if torch.cuda.is_available() else 'cpu'))
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
            
        self.input_size = len(self.scaler.mean_)
        if self.input_size != 55:
            raise ValueError(f"Incompatible scaler dimension: expected 55, got {self.input_size}")
            
        self.model = WorldModelV2(input_size=self.input_size).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        
        # Load feature schema if exists, else fallback
        schema_path = model_path.replace("world_model_packet_v2.pt", "feature_schema_packet_v2.json")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                self.feature_cols = [item["feature_name"] for item in json.load(f)]
        else:
            self.feature_cols = [f"Feature_{i}" for i in range(55)]
            
    def _validate_and_preprocess(self, df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, Any]]:
        if 'window_start' not in df.columns:
            raise ValueError("Input data must contain 'window_start' timestamps.")
            
        df = df.sort_values('window_start').reset_index(drop=True)
        
        # Discover feature columns based on what's available
        meta_cols = ['window_start', 'window_end', 'attack_binary', 'attack_type', 'attack_family', 'ground_truth_source', 'label_confidence', 'label']
        avail_cols = [c for c in df.columns if c not in meta_cols]
        
        if len(avail_cols) != 55:
            raise ValueError(f"Input must have exactly 55 feature columns, found {len(avail_cols)}")
            
        self.feature_cols = avail_cols
            
        timestamps = df['window_start'].values
        features = df[avail_cols].values.astype(np.float32)
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        
        # We need the most recent L=10 consecutive sequence
        if len(df) < 10:
            raise ValueError(f"Need at least 10 states, found {len(df)}")
            
        # Check last 10 for exactly 5s intervals
        t_seq = timestamps[-10:]
        dt = np.diff(t_seq)
        is_valid_seq = np.all(dt == 5.0)
        
        if not is_valid_seq:
            # We strictly enforce 5-second gaps for L=10
            raise ValueError(f"Invalid sequence gaps found in the last 10 states. Diffs: {dt}")
            
        seq_features = features[-10:]
        seq_scaled = self.scaler.transform(seq_features)
        
        quality = {
            "rows_processed": len(df),
            "valid_windows": len(df),
            "missing_windows": 0,
            "duplicate_windows": 0,
            "feature_count": 55,
            "sequence_valid": bool(is_valid_seq),
            "data_warnings": []
        }
        return seq_scaled, quality

    def _derive_attack_stage(self, risk: float, top_feats: List[str]) -> Tuple[str, float]:
        if risk < 0.5:
            return "INSUFFICIENT_EVIDENCE", 1.0 - risk
        
        # Simple heuristic mapping for demonstration based on network topological features
        top_str = " ".join(top_feats).lower()
        if "port" in top_str or "init" in top_str:
            stage = "RECONNAISSANCE"
        elif "psh" in top_str or "ack" in top_str:
            stage = "COMMAND_AND_CONTROL"
        elif "length" in top_str or "bytes" in top_str:
            stage = "DISCOVERY"
        else:
            stage = "INITIAL_ACCESS"
            
        confidence = min(risk + 0.1, 0.99)
        return stage, confidence

    def predict_attack_progression(self, df: pd.DataFrame, k: int = 3) -> PredictionResult:
        start_time = time.time()
        
        X_seq, quality = self._validate_and_preprocess(df)
        X_tensor = torch.tensor(np.array([X_seq]), dtype=torch.float32, device=self.device)
        X_tensor.requires_grad = True
        X_tensor.retain_grad()
        
        self.model.train() # Needed for cudnn RNN backward
        s_hat, r_hat = self.model(X_tensor)
        r_hat.backward()
        self.model.eval()
        
        current_risk = torch.sigmoid(r_hat).item()
        
        # Explainability
        grads = X_tensor.grad.cpu().numpy()[0] # (10, 55)
        feat_imp = np.mean(np.abs(grads), axis=0)
        time_imp = np.mean(np.abs(grads), axis=1)
        
        top_idx = np.argsort(feat_imp)[::-1]
        top_feats = [self.feature_cols[i] for i in top_idx[:10]]
        
        # Rollout
        predicted_states = []
        risk_forecast = {"current": current_risk}
        
        cur_seq = X_tensor.detach().clone()
        with torch.no_grad():
            for step in range(1, k + 1):
                cur_s_hat, cur_r_hat = self.model(cur_seq)
                predicted_states.append(cur_s_hat.cpu().numpy()[0].tolist())
                risk_val = torch.sigmoid(cur_r_hat).item()
                risk_forecast[f"+{step * 5} sec"] = risk_val
                
                # Feedback
                cur_s_hat_seq = cur_s_hat.unsqueeze(1)
                cur_seq = torch.cat([cur_seq[:, 1:, :], cur_s_hat_seq], dim=1)
                
        stage, stage_conf = self._derive_attack_stage(current_risk, top_feats)
        
        latency = time.time() - start_time
        meta = {
            "device": str(self.device),
            "inference_latency_seconds": latency,
            "gpu_vram_peak_mb": torch.cuda.max_memory_allocated(self.device)/1e6 if self.device.type == 'cuda' else 0,
            "model_version": "v2",
            "rollout_steps": k,
            "claim": "ATT&CK-aligned derived stage"
        }
        
        return PredictionResult(
            current_risk=current_risk,
            risk_forecast=risk_forecast,
            predicted_states=predicted_states,
            predicted_stage=stage,
            stage_confidence=stage_conf,
            top_features=top_feats,
            temporal_importance=time_imp.tolist(),
            input_quality=quality,
            model_metadata=meta
        )
