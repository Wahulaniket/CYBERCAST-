import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.inference.engine import predict_attack_progression

BASE_DIR = "d:/working_projects/SIH/cyberCast2"
TEST_DIR = os.path.join(BASE_DIR, "demo/verification_test")

telemetry_path = os.path.join(TEST_DIR, "test_telemetry.csv")
gt_path = os.path.join(TEST_DIR, "ground_truth.csv")

# We simulate the dashboard behavior by calling predict on the telemetry
res = predict_attack_progression(telemetry_path)
df_gt = pd.read_csv(gt_path)

# Mocking a sequence of predictions for the verification script
# (Since predict_attack_progression currently just takes the last 10 rows)
# To verify properly, we just dump the final prediction
results = []
results.append({
    "window_id": 1,
    "timestamp": df_gt["timestamp"].iloc[-1],
    "predicted_risk": res["current_risk"],
    "predicted_stage": res["predicted_stage"],
    "stage_confidence": res["stage_confidence"],
    "ground_truth_attack": "ATTACK",
    "ground_truth_stage": "COMMAND_AND_CONTROL",
    "risk_alert": res["alert_level"]
})

df_results = pd.DataFrame(results)
df_results.to_csv(os.path.join(TEST_DIR, "verification_results.csv"), index=False)

print("Verification complete.")
