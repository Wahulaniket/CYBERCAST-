import os
import json
import pandas as pd
import numpy as np

DATA_DIR = "d:/working_projects/SIH/cyberCast2/data"
OUT_DIR = "d:/working_projects/SIH/cyberCast2/dataset_inspection"

def get_file_list():
    files = []
    for root, _, filenames in os.walk(DATA_DIR):
        for f in filenames:
            if f.endswith('.csv') or f.endswith('.parquet'):
                files.append(os.path.join(root, f))
    return files

def check_feature_types(columns):
    cols_lower = [c.lower() for c in columns]
    has_time = any('time' in c or 'date' in c for c in cols_lower)
    has_label = any('label' in c or 'class' in c or 'attack' in c for c in cols_lower)
    has_attack = has_label # Often same
    has_flow = any('flow' in c or 'ip' in c or 'port' in c for c in cols_lower)
    has_packet = any('pkt' in c or 'packet' in c or 'ttl' in c for c in cols_lower)
    return has_time, has_label, has_attack, has_flow, has_packet

def phase0():
    files = get_file_list()
    inventory = []
    for f in files:
        size = os.path.getsize(f)
        ftype = 'CSV' if f.endswith('.csv') else 'Parquet'
        
        # Read a chunk to get columns
        try:
            if ftype == 'CSV':
                # Just read 100 rows for schema
                df = pd.read_csv(f, nrows=100)
                # Count rows fast for csv? Too slow for 4GB. We will estimate or skip exact count if too large.
                # Actually, we can just say "TBD" or use a rough estimate based on size for now.
                rows = "Unknown (large)"
            else:
                df = pd.read_parquet(f)
                rows = len(df)
            
            cols = df.columns.tolist()
            mem = size # roughly size on disk
            has_time, has_label, has_attack, has_flow, has_packet = check_feature_types(cols)
            
            inventory.append({
                "filename": os.path.basename(f),
                "filepath": f,
                "file type": ftype,
                "size": size,
                "number of rows": rows,
                "number of columns": len(cols),
                "estimated memory usage": f"{size / (1024*1024):.2f} MB",
                "timestamp availability": has_time,
                "label availability": has_label,
                "attack information availability": has_attack,
                "packet/flow information availability": f"Flow: {has_flow}, Packet: {has_packet}"
            })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    with open(os.path.join(OUT_DIR, 'dataset_inventory.json'), 'w') as out_f:
        json.dump(inventory, out_f, indent=4)
        
    print("Phase 0 done.")

def assign_role(col):
    col_l = col.lower()
    if 'time' in col_l or 'date' in col_l: return 'timestamp'
    if 'src' in col_l and 'ip' in col_l: return 'source_ip'
    if 'dst' in col_l and 'ip' in col_l: return 'destination_ip'
    if 'src' in col_l and 'port' in col_l: return 'source_port'
    if 'dst' in col_l and 'port' in col_l: return 'destination_port'
    if 'proto' in col_l: return 'protocol'
    if 'flag' in col_l: return 'tcp_flag'
    if 'byte' in col_l: return 'bytes'
    if 'pkt' in col_l or 'packet' in col_l: return 'packets'
    if 'duration' in col_l: return 'duration'
    if 'iat' in col_l: return 'IAT'
    if 'ttl' in col_l: return 'TTL'
    if 'window' in col_l or 'win' in col_l: return 'window_size'
    if 'payload' in col_l: return 'payload_size'
    if 'retro' in col_l or 'retrans' in col_l: return 'retransmission'
    if 'label' in col_l: return 'label'
    if 'attack' in col_l: return 'attack_type'
    if 'id' in col_l: return 'identifier'
    return 'unknown'

def phase1():
    files = get_file_list()
    # To avoid massive processing, we'll combine schemas from all datasets, 
    # but sample up to 10,000 rows from each to get stats.
    all_schema_info = []
    
    for f in files:
        ftype = 'CSV' if f.endswith('.csv') else 'Parquet'
        try:
            if ftype == 'CSV':
                # Use a larger chunk for stats
                df = pd.read_csv(f, nrows=10000, skipinitialspace=True)
            else:
                df = pd.read_parquet(f).sample(min(10000, os.path.getsize(f)), replace=True) if os.path.getsize(f) > 10000 else pd.read_parquet(f)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            for col in df.columns:
                series = df[col]
                dtype = str(series.dtype)
                missing = series.isna().sum()
                missing_pct = missing / len(series) * 100
                nunique = series.nunique()
                
                is_num = pd.api.types.is_numeric_dtype(series)
                if is_num:
                    min_v = series.min()
                    max_v = series.max()
                    mean_v = series.mean()
                    std_v = series.std()
                    median_v = series.median()
                else:
                    min_v, max_v, mean_v, std_v, median_v = None, None, None, None, None
                
                constant_flag = (nunique <= 1)
                role = assign_role(col)
                
                all_schema_info.append({
                    'dataset': os.path.basename(os.path.dirname(f)),
                    'feature': col,
                    'dtype': dtype,
                    'missing_count': missing,
                    'missing_percentage': missing_pct,
                    'unique_count': nunique,
                    'min': min_v,
                    'max': max_v,
                    'mean': mean_v,
                    'std': std_v,
                    'median': median_v,
                    'constant_flag': constant_flag,
                    'potential_role': role
                })
        except Exception as e:
            print(f"Error in Phase 1 for {f}: {e}")
            
    schema_df = pd.DataFrame(all_schema_info)
    # Deduplicate by dataset and feature to avoid huge files
    schema_df = schema_df.drop_duplicates(subset=['dataset', 'feature'])
    schema_df.to_csv(os.path.join(OUT_DIR, 'schema_report.csv'), index=False)
    print("Phase 1 done.")

if __name__ == '__main__':
    phase0()
    phase1()
