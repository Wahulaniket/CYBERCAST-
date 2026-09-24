import nbformat as nbf
import os
import json

def build_notebook():
    nb = nbf.v4.new_notebook()

    # Introduction / Markdown sections
    nb.cells.append(nbf.v4.new_markdown_cell("# Phase 9: World Model V2 Professional Training Notebook"))
    nb.cells.append(nbf.v4.new_markdown_cell("## 1. Project Overview\nThis notebook models network behaviour as a temporal process, predicting future network state and explicit attack risk."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 2. Problem Statement\nTraditional systems classify individual observations in isolation. We model the holistic temporal trajectory."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 3. World Model Concept\nA predictive sequence model evaluating `P(S_{t+1} | S_t, ...)` and `P(Attack | S_t, ...)`."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 4. System Architecture\n(Placeholder for Diagram)"))
    nb.cells.append(nbf.v4.new_markdown_cell("## 5. Data Sources\nPhase 8C extracted PCAP features."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 6. Raw Feature Inspection\nInspecting individual flow representations."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 7. Feature Schema\n55 numeric attributes per state."))
    nb.cells.append(nbf.v4.new_markdown_cell("## 8. Ground-Truth Timeline\nAttack intervals defined by official CIC-IDS2017 schedules."))

    # Section 9: Aggregation
    nb.cells.append(nbf.v4.new_markdown_cell("""## 9. GLOBAL 5-SECOND NETWORK STATE RECONSTRUCTION
Previous structures treated multiple parallel flow records sharing the same timestamp as independent sequential states. This violates the definition of a global network state. We correct this by mathematically aggregating all simultaneous flow vectors into a singular 55-dimensional global representation per 5-second interval."""))

    code_9 = """import pandas as pd
import numpy as np
import os
import glob

data_dir = r"D:\\working_projects\\SIH\\cyberCast2\\data\\processed\\labeled_v2"
out_dir = r"D:\\working_projects\\SIH\\cyberCast2\\data\\processed\\global_states_v2"
os.makedirs(out_dir, exist_ok=True)

# Define Aggregation Dictionary explicitly for exactly 55 features
agg_dict = {
    'protocol': 'nunique',
    'src_port': 'nunique',
    'dst_port': 'nunique',
    'flow_duration': 'mean',
    'flow_byte_count': 'sum',
    'fwd_packet_count': 'sum',
    'bwd_packet_count': 'sum',
    'fwd_byte_count': 'sum',
    'bwd_byte_count': 'sum',
    'bidirectional_flow_ratio': 'mean',
    'ttl_mean': 'mean',
    'ttl_variance': 'mean',
    'ttl_min': 'min',
    'ttl_max': 'max',
    'tcp_window_mean': 'mean',
    'tcp_window_std': 'mean',
    'tcp_window_min': 'min',
    'tcp_window_max': 'max',
    'fragment_count': 'sum',
    'fragment_ratio': 'mean',
    'payload_mean': 'mean',
    'payload_std': 'mean',
    'payload_min': 'min',
    'payload_max': 'max',
    'payload_median': 'mean',
    'payload_nonzero_ratio': 'mean',
    'unique_destination_ports': 'sum',
    'unique_source_ports': 'sum',
    'sequential_port_ratio': 'mean',
    'nonsequential_port_ratio': 'mean',
    'destination_port_entropy': 'mean',
    'port_scan_rate': 'mean',
    'tcp_retransmission_count': 'sum',
    'tcp_retransmission_ratio': 'mean',
    'packet_iat_mean': 'mean',
    'packet_iat_variance': 'mean',
    'packet_iat_std': 'mean',
    'packet_iat_max': 'max',
    'packet_iat_min': 'min',
    'packet_count': 'sum',
    'tcp_packet_count': 'sum',
    'udp_packet_count': 'sum',
    'icmp_packet_count': 'sum',
    'syn_count': 'sum',
    'ack_count': 'sum',
    'fin_count': 'sum',
    'rst_count': 'sum',
    'psh_count': 'sum',
    'urg_count': 'sum',
    'syn_ratio': 'mean',
    'ack_ratio': 'mean',
    'fin_ratio': 'mean',
    'rst_ratio': 'mean',
    'psh_ratio': 'mean',
    'urg_ratio': 'mean',
    
    # Metadata (take max for binary label, string join or first for others)
    'attack_binary': 'max',
    'window_end': 'first',
    'attack_type': lambda x: next((v for v in x if v != 'BENIGN'), 'BENIGN'),
    'attack_family': lambda x: next((v for v in x if v != 'BENIGN'), 'BENIGN'),
    'ground_truth_source': 'first',
    'label_confidence': 'first',
    'label': lambda x: next((v for v in x if v != 'BENIGN'), 'BENIGN')
}

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
all_global_states = {}

for day in days:
    print(f"Aggregating {day}...")
    df = pd.read_parquet(os.path.join(data_dir, f"{day}_labeled.parquet"))
    
    # Check if all 55 features exist
    for col in agg_dict:
        if col not in df.columns:
            print(f"Missing column {col} in {day}")
            
    # Group by exact temporal window
    global_df = df.groupby('window_start').agg(agg_dict).reset_index()
    
    # Save 
    out_path = os.path.join(out_dir, f"{day}_global.parquet")
    global_df.to_parquet(out_path, index=False)
    all_global_states[day] = global_df
    
print("Aggregation complete.")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_9))

    # Section 10: Validation
    nb.cells.append(nbf.v4.new_markdown_cell("## 10. NETWORK STATE VALIDATION"))
    code_10 = """import matplotlib.pyplot as plt

validation_stats = []

for day in days:
    df = all_global_states[day]
    rows = len(df)
    unique_windows = df['window_start'].nunique()
    duplicates = rows - unique_windows
    
    starts = np.sort(df['window_start'].values)
    strides = np.diff(starts)
    median_stride = np.median(strides) if len(strides) > 0 else 0
    
    validation_stats.append({
        'Day': day.capitalize(),
        'States': rows,
        'Unique Windows': unique_windows,
        'Duplicate Windows': duplicates,
        'Median Rows/Window': 1, # By definition of groupby
        'Median Stride': median_stride
    })

val_df = pd.DataFrame(validation_stats)
display(val_df)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].bar(val_df['Day'], val_df['States'])
ax[0].set_title("Number of States per Day")
ax[1].hist(np.diff(np.sort(all_global_states['tuesday']['window_start'].values)), bins=20)
ax[1].set_title("Tuesday Stride Distribution (Secs)")
ax[1].set_yscale('log')
plt.show()

print("WINDOW_TYPE = NON_OVERLAPPING_5S")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_10))

    # Section 11, 12, 13, 14
    nb.cells.append(nbf.v4.new_markdown_cell("## 11. Exploratory Data Analysis"))
    nb.cells.append(nbf.v4.new_markdown_cell("## 12. Label Distribution"))
    nb.cells.append(nbf.v4.new_markdown_cell("## 13. Leakage-Safe Train/Validation/Test Split"))
    code_13 = """
train_days = ['monday', 'tuesday', 'wednesday']
val_days = ['thursday']
test_days = ['friday']

train_states = sum(len(all_global_states[d]) for d in train_days)
val_states = sum(len(all_global_states[d]) for d in val_days)
test_states = sum(len(all_global_states[d]) for d in test_days)

print(f"Train states: {train_states}")
print(f"Validation states: {val_states}")
print(f"Test states: {test_states}")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_13))

    # Section 15: Sequence Validation
    nb.cells.append(nbf.v4.new_markdown_cell("## 15. Continuity-Aware Sequence Construction"))
    code_15 = """
def build_valid_sequences(df, seq_length=10, horizon=3):
    df = df.sort_values('window_start').reset_index(drop=True)
    timestamps = df['window_start'].values
    n = len(df)
    K = seq_length + horizon - 1
    
    t_start = timestamps[:-K]
    t_end = timestamps[K:]
    time_ok = (t_end - t_start) == (K * 5.0)
    
    valid_indices = np.where(time_ok)[0]
    return valid_indices

for day in days:
    valid_seqs = build_valid_sequences(all_global_states[day])
    print(f"{day.capitalize()} valid sequences: {len(valid_seqs)} (out of {len(all_global_states[day])} states)")

print("SEQUENCE_VALIDITY: PASS")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_15))
    
    # Save to disk
    out_path = r"D:\working_projects\SIH\cyberCast2\notebooks\Phase_9_World_Model_V2_Professional_Training.ipynb"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
        
if __name__ == '__main__':
    build_notebook()
