import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.inference.engine import predict_attack_progression

BASE_DIR = "d:/working_projects/SIH/cyberCast2"
TEST_DIR = os.path.join(BASE_DIR, "demo/real_verification")

telemetry_path = os.path.join(TEST_DIR, "test_telemetry.csv")
gt_path = os.path.join(TEST_DIR, "ground_truth.csv")

# Simulate dashboard inference
res = predict_attack_progression(telemetry_path)
df_gt = pd.read_csv(gt_path)

# Dump final prediction for verification
results = []
results.append({
    "window_id": len(df_gt)-1,
    "timestamp": df_gt["timestamp"].iloc[-1],
    "predicted_risk": res["current_risk"],
    "predicted_stage": res["predicted_stage"],
    "stage_confidence": res["stage_confidence"],
    "ground_truth_attack": df_gt["ground_truth_attack"].iloc[-1],
    "ground_truth_stage": df_gt["ground_truth_stage"].iloc[-1],
    "risk_alert": res["alert_level"]
})

df_results = pd.DataFrame(results)
df_results.to_csv(os.path.join(TEST_DIR, "verification_results.csv"), index=False)

print("Real verification complete.")
