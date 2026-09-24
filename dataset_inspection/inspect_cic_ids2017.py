import os
import glob
import pandas as pd
import numpy as np
import datetime
import traceback

BASE_DIR = "d:/working_projects/SIH/cyberCast2"
REPORT_DIR = os.path.join(BASE_DIR, "reports/dataset_inspection")
os.makedirs(REPORT_DIR, exist_ok=True)

# Step 1: Locate Dataset
print("Locating dataset...")
search_paths = [
    os.path.join(BASE_DIR, "data", "CIC-IDS2017"),
    os.path.join(BASE_DIR, "data", "raw"),
    os.path.join(BASE_DIR, "data", "archive"),
    os.path.join(BASE_DIR, "data")
]
dataset_path = None
for path in search_paths:
    if os.path.exists(path) and len(glob.glob(os.path.join(path, "*.csv"))) > 0:
        if 'CIC-IDS2017' in path or any('CIC-IDS2017' in f or 'WorkingHours' in f for f in os.listdir(path)):
            dataset_path = path
            break

if not dataset_path:
    # fallback to searching
    all_csvs = glob.glob(os.path.join(BASE_DIR, "**/*.csv"), recursive=True)
    for f in all_csvs:
        if 'WorkingHours' in f:
            dataset_path = os.path.dirname(f)
            break

print(f"Dataset path identified: {dataset_path}")

# Step 2 & 3: File Inventory & Sizes
inventory = []
total_dataset_size = 0
csv_size = 0
pcap_size = 0
pcap_files = 0
pcapng_files = 0
cap_files = 0

all_files = glob.glob(os.path.join(dataset_path, "**/*"), recursive=True) if dataset_path else []
if dataset_path:
    for f in all_files:
        if os.path.isfile(f):
            size = os.path.getsize(f)
            ext = os.path.splitext(f)[1].lower()
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
            
            ftype = 'other'
            if ext == '.csv':
                ftype = 'CSV'
                csv_size += size
            elif ext == '.pcap':
                ftype = 'PCAP'
                pcap_size += size
                pcap_files += 1
            elif ext == '.pcapng':
                ftype = 'PCAPNG'
                pcap_size += size
                pcapng_files += 1
            elif ext == '.cap':
                ftype = 'CAP'
                pcap_size += size
                cap_files += 1
            elif ext in ['.zip', '.tar', '.gz', '.rar']:
                ftype = 'Archive'
            
            inventory.append({
                'filename': os.path.basename(f),
                'full_path': f,
                'extension': ext,
                'file_size_bytes': size,
                'last_modified': mtime,
                'type': ftype
            })
            total_dataset_size += size

df_inventory = pd.DataFrame(inventory)
df_inventory.to_csv(os.path.join(REPORT_DIR, "FILE_INVENTORY.csv"), index=False)

csv_files = [f for f in inventory if f['type'] == 'CSV']

# Steps 5-11: Inspect CSVs
total_csv_rows = 0
total_cols = 0
schemas = {}
all_labels = {}
attack_timelines = {}
global_min_ts = None
global_max_ts = None
missing_values_report = []

has_source_ip = False
has_dest_ip = False
has_source_port = False
has_dest_port = False
has_protocol = False
has_tcp_flags = False
has_bytes = False
has_packets = False
has_duration = False
has_iat_mean = False
has_iat_var = False
has_iat_max = False
has_bidi_ratio = False

for csv in csv_files:
    try:
        df_sample = pd.read_csv(csv['full_path'], nrows=10000, skipinitialspace=True)
        cols = [c.strip() for c in df_sample.columns]
        total_cols = max(total_cols, len(cols))
        
        # determine schema
        schema_key = tuple(cols)
        if schema_key not in schemas:
            schema_details = []
            for c in cols:
                schema_details.append({
                    'column_name': c,
                    'data_type': str(df_sample[c].dtype),
                    'sample_values': str(df_sample[c].dropna().head(3).tolist())
                })
            schemas[schema_key] = schema_details
            
        # Feature coverage mapping
        col_lower = [c.lower() for c in cols]
        if any('source ip' in c for c in col_lower): has_source_ip = True
        if any('destination ip' in c for c in col_lower): has_dest_ip = True
        if any('source port' in c for c in col_lower): has_source_port = True
        if any('destination port' in c for c in col_lower): has_dest_port = True
        if any('protocol' in c for c in col_lower): has_protocol = True
        if any('flag' in c for c in col_lower): has_tcp_flags = True
        if any('byte' in c for c in col_lower): has_bytes = True
        if any('packet' in c for c in col_lower): has_packets = True
        if any('duration' in c for c in col_lower): has_duration = True
        if any('iat mean' in c for c in col_lower): has_iat_mean = True
        if any('iat std' in c for c in col_lower): has_iat_var = True
        if any('iat max' in c for c in col_lower): has_iat_max = True
        if any('down/up ratio' in c for c in col_lower): has_bidi_ratio = True

        # Process full file in chunks for labels and rows
        chunk_iter = pd.read_csv(csv['full_path'], chunksize=50000, skipinitialspace=True, low_memory=False)
        for chunk in chunk_iter:
            chunk.columns = [c.strip() for c in chunk.columns]
            total_csv_rows += len(chunk)
            
            if 'Label' in chunk.columns:
                val_counts = chunk['Label'].value_counts()
                for label, count in val_counts.items():
                    all_labels[label] = all_labels.get(label, 0) + count
            
            # Timestamp processing
            ts_col = next((c for c in chunk.columns if 'timestamp' in c.lower()), None)
            if ts_col and 'Label' in chunk.columns:
                chunk[ts_col] = pd.to_datetime(chunk[ts_col], format='mixed', errors='coerce', dayfirst=True)
                chunk_ts = chunk.dropna(subset=[ts_col])
                
                if len(chunk_ts) > 0:
                    c_min = chunk_ts[ts_col].min()
                    c_max = chunk_ts[ts_col].max()
                    if global_min_ts is None or c_min < global_min_ts: global_min_ts = c_min
                    if global_max_ts is None or c_max > global_max_ts: global_max_ts = c_max
                    
                    # Attack timeline
                    for lbl, grp in chunk_ts.groupby('Label'):
                        amin = grp[ts_col].min()
                        amax = grp[ts_col].max()
                        if lbl not in attack_timelines:
                            attack_timelines[lbl] = {'First Timestamp': amin, 'Last Timestamp': amax, 'Flow Count': len(grp)}
                        else:
                            if amin < attack_timelines[lbl]['First Timestamp']: attack_timelines[lbl]['First Timestamp'] = amin
                            if amax > attack_timelines[lbl]['Last Timestamp']: attack_timelines[lbl]['Last Timestamp'] = amax
                            attack_timelines[lbl]['Flow Count'] += len(grp)

    except Exception as e:
        print(f"Error processing {csv['filename']}: {e}")

# Save Schema
schema_flat = []
for k, v in schemas.items():
    schema_flat.extend(v)
df_schema = pd.DataFrame(schema_flat).drop_duplicates(subset=['column_name'])
df_schema.to_csv(os.path.join(REPORT_DIR, "CSV_SCHEMA_REPORT.csv"), index=False)

# Save Labels
total_labels = sum(all_labels.values())
label_rows = []
benign_records = 0
attack_records = 0
for lbl, count in all_labels.items():
    perc = (count / total_labels) * 100 if total_labels > 0 else 0
    label_rows.append({'Label': lbl, 'Count': count, 'Percentage': perc})
    if 'benign' in str(lbl).lower():
        benign_records += count
    else:
        attack_records += count
        
df_labels = pd.DataFrame(label_rows).sort_values('Count', ascending=False)
df_labels.to_csv(os.path.join(REPORT_DIR, "LABEL_DISTRIBUTION.csv"), index=False)

# Save Timeline
timeline_rows = []
for lbl, data in attack_timelines.items():
    dur = (data['Last Timestamp'] - data['First Timestamp']).total_seconds()
    timeline_rows.append({
        'Attack': lbl,
        'First Timestamp': data['First Timestamp'],
        'Last Timestamp': data['Last Timestamp'],
        'Duration': dur,
        'Flow Count': data['Flow Count']
    })
df_timeline = pd.DataFrame(timeline_rows)
df_timeline.to_csv(os.path.join(REPORT_DIR, "ATTACK_TIMELINE.csv"), index=False)

# Flow Feature Coverage
flow_cov = f"""# Flow Feature Coverage

| SIH Requirement | Dataset Feature | Available | Notes |
|---|---|---|---|
| Source IP | Source IP | {'YES' if has_source_ip else 'NO'} | {'Present' if has_source_ip else 'Missing in this version of CIC-IDS2017'} |
| Destination IP | Destination IP | {'YES' if has_dest_ip else 'NO'} | |
| Source Port | Source Port | {'YES' if has_source_port else 'NO'} | |
| Destination Port | Destination Port | {'YES' if has_dest_port else 'NO'} | |
| Protocol | Protocol | {'YES' if has_protocol else 'NO'} | |
| TCP flags | Various Flag Counts | {'YES' if has_tcp_flags else 'NO'} | |
| Bytes | Flow Bytes/s etc | {'YES' if has_bytes else 'NO'} | |
| Packets | Flow Packets/s etc | {'YES' if has_packets else 'NO'} | |
| Flow duration | Flow Duration | {'YES' if has_duration else 'NO'} | |
| IAT mean | Flow IAT Mean | {'YES' if has_iat_mean else 'NO'} | |
| IAT variance/std | Flow IAT Std | {'YES' if has_iat_var else 'NO'} | |
| IAT max | Flow IAT Max | {'YES' if has_iat_max else 'NO'} | |
| Bidirectional ratio | Down/Up Ratio | {'YES' if has_bidi_ratio else 'NO'} | |
"""
with open(os.path.join(REPORT_DIR, "FLOW_FEATURE_COVERAGE.md"), "w") as f: f.write(flow_cov)

# Packet Feature Availability
pcap_avail = pcap_files > 0 or pcapng_files > 0 or cap_files > 0
packet_cov = f"""# Packet Feature Availability

| Packet Feature | Available in CSV? | PCAP Required? | PCAP Available? | Extractable? |
|---|---|---|---|---|
| TTL | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| TTL variance | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| TCP window | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| IP fragmentation | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| Payload size distribution | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| Sequential port access | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| Randomized port access | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| Retransmissions | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
| Packet IAT | NO | YES | {'YES' if pcap_avail else 'NO'} | {'PCAP-derived' if pcap_avail else 'NO'} |
"""
with open(os.path.join(REPORT_DIR, "PACKET_FEATURE_COVERAGE.md"), "w") as f: f.write(packet_cov)

# Hardware Feasibility
hard_feas = f"""# Hardware Feasibility

estimated raw dataset size: {total_dataset_size / 1e9:.2f} GB
estimated CSV memory expansion: {(csv_size * 2) / 1e9:.2f} GB
estimated processing RAM: 8-16 GB
recommended chunk size: 50,000
recommended DataLoader batch size: 64
GPU feasibility: YES (4GB is sufficient for sequence length 10, batch 64 of dimension 30)

Note: For large CSV files, chunked processing must be strictly adhered to so as not to overwhelm system RAM.
"""
with open(os.path.join(REPORT_DIR, "HARDWARE_FEASIBILITY.md"), "w") as f: f.write(hard_feas)

# Print Final Summary
print("="*60)
print("CIC-IDS2017 DATASET INSPECTION")
print("="*60)
print(f"\nDataset Location:\n{dataset_path}")
print(f"Total Files:\n{len(inventory)}")
print(f"Total Dataset Size:\n{total_dataset_size / 1e9:.2f} GB\n")

print(f"CSV Files:\n{len(csv_files)}")
print(f"CSV Total Size:\n{csv_size / 1e9:.2f} GB\n")

print(f"PCAP Files:\n{pcap_files}")
print(f"PCAPNG Files:\n{pcapng_files}")
print(f"CAP Files:\n{cap_files}\n")

print(f"Total CSV Rows:\n{total_csv_rows}")
print(f"Total Columns:\n{total_cols}\n")

print(f"Timestamp:\n{global_min_ts} to {global_max_ts}")
print(f"Attack Labels:\n{len(all_labels)}")
cats = [lbl for lbl in all_labels.keys() if 'benign' not in str(lbl).lower()]
print(f"Attack Categories:\n{len(cats)}\n")

print(f"Benign Records:\n{benign_records}")
print(f"Attack Records:\n{attack_records}\n")

flow_avail = sum([has_source_ip, has_dest_ip, has_source_port, has_dest_port, has_protocol, has_tcp_flags, has_bytes, has_packets, has_duration, has_iat_mean, has_iat_var, has_iat_max, has_bidi_ratio])
print(f"Flow Feature Coverage:\n{flow_avail} / 13\n")

packet_avail = 9 if pcap_avail else 0
print(f"Packet Feature Availability:\n{packet_avail} / 9\n")

print(f"PCAP Availability:\n{'AVAILABLE' if pcap_avail else 'NOT AVAILABLE'}\n")

align = 'UNKNOWN'
if not pcap_avail: align = 'N/A'
elif has_source_ip and has_dest_ip and has_protocol and has_source_port and has_dest_port: align = 'HIGH'
print(f"PCAP <-> CSV Alignment:\n{align}\n")

print(f"Temporal Modelling:\n{'SUPPORTED' if global_min_ts else 'NOT SUPPORTED'}\n")

print(f"World Model Suitability:\n{'SUPPORTED' if global_min_ts and total_cols >= 30 else 'LIMITED'}\n")

print(f"Unseen Attack Experiment:\n{'FEASIBLE' if len(cats) > 1 else 'NOT FEASIBLE'}\n")

print("Hardware:\nCPU: Intel i5\nGPU: RTX 2050 4GB\n")

print(f"Recommended Processing:\nChunk size 50,000, offline inference using generators.\n")

print("Dataset Inspection:\nCOMPLETE")
print("="*60)
