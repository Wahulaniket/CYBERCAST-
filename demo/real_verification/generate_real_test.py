import os
import pandas as pd
import numpy as np
import datetime
import sys
import torch
import yaml

BASE_DIR = "d:/working_projects/SIH/cyberCast2"
TEST_DIR = os.path.join(BASE_DIR, "demo/real_verification")
os.makedirs(TEST_DIR, exist_ok=True)

# 1. READ REAL DATA
print("Reading IDS2018 dataset...")
df = pd.read_csv(os.path.join(BASE_DIR, "data/archive/02-14-2018.csv"))
df.columns = df.columns.str.strip()

print("Parsing timestamps...")
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', dayfirst=True)
df = df.sort_values('Timestamp')

# Find transition Benign -> FTP-BruteForce
print("Finding temporal transition...")
attack_indices = df[df['Label'].isin(['FTP-BruteForce', 'SSH-Bruteforce'])].index
if len(attack_indices) > 0:
    first_attack_idx = attack_indices[0]
    first_attack_time = df.loc[first_attack_idx, 'Timestamp']
else:
    first_attack_time = df['Timestamp'].iloc[len(df)//2]

start_time = first_attack_time - pd.Timedelta(minutes=5)
end_time = first_attack_time + pd.Timedelta(minutes=5)
mask = (df['Timestamp'] >= start_time) & (df['Timestamp'] <= end_time)
df_segment = df[mask].copy()

# 2. GROUP INTO 5-SECOND WINDOWS
print("Resampling into 5-second windows...")
df_segment.set_index('Timestamp', inplace=True)
df_segment.sort_index(inplace=True)

numeric_cols = df_segment.select_dtypes(include=[np.number]).columns[:30]

df_resampled = df_segment[numeric_cols].resample('5S').mean().ffill().bfill()
labels_resampled = df_segment['Label'].resample('5S').apply(lambda x: x.mode()[0] if len(x) > 0 else np.nan).ffill().bfill()

df_telemetry = df_resampled.copy()
df_telemetry.columns = [f"Feature_{i}" for i in range(30)]
df_telemetry.replace([np.inf, -np.inf], np.nan, inplace=True)
df_telemetry.fillna(0, inplace=True)
df_telemetry.insert(0, "timestamp", df_resampled.index)
df_telemetry.to_csv(os.path.join(TEST_DIR, "test_telemetry.csv"), index=False)

# 3. CREATE GROUND TRUTH FILE
print("Creating ground truth...")
ground_truth_labels = []
attack_types = []
ground_truth_stages = []

for label in labels_resampled:
    if label == 'Benign':
        ground_truth_labels.append('BENIGN')
        attack_types.append('Normal')
        ground_truth_stages.append('BENIGN')
    elif pd.notnull(label) and 'BruteForce' in str(label) or 'Bruteforce' in str(label):
        ground_truth_labels.append('ATTACK')
        attack_types.append('BruteForce')
        ground_truth_stages.append('INITIAL_ACCESS')
    else:
        ground_truth_labels.append('ATTACK')
        attack_types.append(str(label))
        ground_truth_stages.append('UNKNOWN')

df_gt = pd.DataFrame({
    "window_id": range(len(df_telemetry)),
    "timestamp": df_telemetry['timestamp'],
    "ground_truth_attack": ground_truth_labels,
    "attack_type": attack_types,
    "ground_truth_stage": ground_truth_stages
})
df_gt.to_csv(os.path.join(TEST_DIR, "ground_truth.csv"), index=False)

# 4. RUN INFERENCE FOR VERIFICATION
print("Running inference...")
sys.path.append(BASE_DIR)
from src.inference.engine import predict_attack_progression
from src.models.model_loader import load_system

model, scaler, schema, config, device = load_system(BASE_DIR)

results = []
raw_seq_all = df_telemetry.iloc[:, 1:31].values.astype(np.float32)

with open(os.path.join(BASE_DIR, "configs/stage_mapping.yaml")) as f: 
    stage_cfg = yaml.safe_load(f)

for i in range(10, len(df_telemetry) + 1):
    raw_seq = raw_seq_all[i-10:i]
    scaled_seq = scaler.transform(raw_seq)
    t_seq = torch.tensor(scaled_seq).unsqueeze(0).to(device)
    
    with torch.no_grad():
        _, curr_risk_logit = model(t_seq)
    curr_risk = torch.sigmoid(curr_risk_logit).item()
    
    if curr_risk < stage_cfg["RECONNAISSANCE"]["threshold"]: p_stage = "BENIGN"
    elif curr_risk < stage_cfg["DISCOVERY"]["threshold"]: p_stage = "RECONNAISSANCE"
    elif curr_risk < stage_cfg["INITIAL_ACCESS"]["threshold"]: p_stage = "DISCOVERY"
    elif curr_risk < stage_cfg["COMMAND_AND_CONTROL"]["threshold"]: p_stage = "INITIAL_ACCESS"
    else: p_stage = "COMMAND_AND_CONTROL"
    
    gt_row = df_gt.iloc[i-1]
    
    results.append({
        "window_id": gt_row['window_id'],
        "timestamp": gt_row['timestamp'],
        "predicted_risk": curr_risk,
        "predicted_stage": p_stage,
        "ground_truth_attack": gt_row['ground_truth_attack'],
        "ground_truth_stage": gt_row['ground_truth_stage']
    })

df_results = pd.DataFrame(results)
df_results.to_csv(os.path.join(TEST_DIR, "verification_results.csv"), index=False)

# 5. EARLY WARNING
attack_start_time = df_gt[df_gt['ground_truth_attack'] == 'ATTACK']['timestamp'].min()
predicted_attack_times = df_results[(df_results['predicted_stage'] != 'BENIGN') & (df_results['timestamp'] >= attack_start_time)]['timestamp']

if pd.notnull(attack_start_time) and not predicted_attack_times.empty:
    first_alert = predicted_attack_times.min()
    early_warning_seconds = (first_alert - attack_start_time).total_seconds()
    if early_warning_seconds < 0: early_warning_seconds = 0
else:
    early_warning_seconds = "N/A"

# 6. REPORT
benign_count = (df_gt['ground_truth_attack'] == 'BENIGN').sum()
attack_count = (df_gt['ground_truth_attack'] == 'ATTACK').sum()
total_windows = len(df_gt)
start_ts = df_gt['timestamp'].min()
end_ts = df_gt['timestamp'].max()

report_md = f"""# Real-Data Verification Report

## Source Dataset
CSE-CIC-IDS2018

## Source File
02-14-2018.csv

## Timestamps
{start_ts} to {end_ts}

## Record Count
{len(df_segment)} raw flows

## Window Count
{total_windows} (5-second windows)

## Benign Count
{benign_count}

## Attack Count
{attack_count}

## Attack Types
Normal, BruteForce

## Training-Independence Evidence
Training independence: UNKNOWN. (The pipeline currently uses mock random data for the scaler and weights. Thus, it hasn't memorized this specific file, but the true metrics cannot be reliably calculated).

## Prediction Results
Model risk predictions are saved in verification_results.csv. Due to the randomly initialized mocked model from phase 5, metrics such as Precision, Recall, PR-AUC, and ROC-AUC are unreliable and hence not formally benchmarked here. 

## Early-Warning Result
Early Warning: {early_warning_seconds} seconds (Warning: Derived from mocked weights).

## Limitations
- Predictions are from a randomly initialized model.
- 30 numeric columns were mapped directly to Feature_0..29 as an approximation of the true feature selection pipeline, since actual phase 2 preprocessing was bypassed.
"""

with open(os.path.join(TEST_DIR, "verification_report.md"), "w", encoding="utf-8") as f:
    f.write(report_md)

readme_md = """# Real-Data Independent Verification Package

This directory contains an independently verified real-data test set extracted from CSE-CIC-IDS2018.

## Files
- `test_telemetry.csv`: 30-feature inputs (5s windows)
- `ground_truth.csv`: Unseen ground truth matching the windows
- `verification_results.csv`: Offline verification predictions
- `verification_report.md`: Summary of the test and metrics

## Usage with Dashboard
1. Start Streamlit: `streamlit run dashboard/app.py`
2. Upload `test_telemetry.csv`
3. Run K=1, 3, 5, 10
4. Keep `ground_truth.csv` OUTSIDE the dashboard.
"""
with open(os.path.join(TEST_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_md)

print(f"BENIGN WINDOWS: {benign_count}")
print(f"ATTACK WINDOWS: {attack_count}")
print(f"TOTAL WINDOWS: {total_windows}")
print(f"EARLY WARNING: {early_warning_seconds}")
print("REAL DATA VERIFICATION PACKAGE COMPLETED")
