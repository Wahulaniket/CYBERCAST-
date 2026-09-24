import os, time, datetime, torch
import numpy as np
from src.models.model_loader import load_system
from src.inference.rollout import autoregressive_rollout
from src.inference.stage_mapper import map_stage
from src.inference.explainability import explain

BASE_DIR = "d:/working_projects/SIH/cyberCast2"

def get_alert_level(risk, base_dir):
    import yaml
    with open(os.path.join(base_dir, "configs/risk_thresholds.yaml")) as f: cfg = yaml.safe_load(f)
    for lvl, bounds in cfg.items():
        if bounds["min"] <= risk <= bounds["max"]: return lvl.upper()
    return "CRITICAL"

def predict_attack_progression(input_data_path):
    start_t = time.time()
    model, scaler, schema, config, device = load_system(BASE_DIR)
    
    # Mock data loading: assume 10 states 30 features
    import pandas as pd
    df = pd.read_csv(input_data_path)
    if len(df) < 10: return {"status": "INSUFFICIENT_DATA"}
    raw_seq = df.values[-10:, 1:31].astype(np.float32) # skip timestamp col
    
    # Scale (using training scaler, never refit)
    scaled_seq = scaler.transform(raw_seq)
    t_seq = torch.tensor(scaled_seq).unsqueeze(0).to(device)
    
    # Current prediction
    with torch.no_grad(): _, curr_risk_logit = model(t_seq)
    curr_risk = torch.sigmoid(curr_risk_logit).item()
    
    # Explain
    top_feats, temp_imp = explain(model, t_seq)
    
    # Rollout
    f_states, f_risks = autoregressive_rollout(model, t_seq, 3)
    forecast = {"5s": f_risks[0].item(), "10s": f_risks[1].item(), "15s": f_risks[2].item()}
    
    trend = "INCREASING" if forecast["15s"] > curr_risk else "STABLE"
    
    c_stage, _, _ = map_stage(curr_risk, BASE_DIR)
    p_stage, p_conf, p_type = map_stage(forecast["15s"], BASE_DIR)
    
    result = {
        "status": "SUCCESS",
        "timestamp": datetime.datetime.now().isoformat(),
        "current_risk": curr_risk,
        "risk_forecast": forecast,
        "risk_trend": trend,
        "alert_level": get_alert_level(curr_risk, BASE_DIR),
        "current_stage": c_stage,
        "predicted_stage": p_stage,
        "stage_confidence": p_conf,
        "mapping_type": p_type,
        "predicted_states": [s[0].cpu().numpy().tolist() for s in f_states],
        "top_features": top_feats,
        "temporal_importance": temp_imp,
        "explanation": "Risk is " + trend.lower() + " based on model-attributed contributing features.",
        "model": {"name": "LSTM World Model", "version": "1.0", "sequence_length": 10, "state_dimension": 30, "window_seconds": 5}
    }
    return result
