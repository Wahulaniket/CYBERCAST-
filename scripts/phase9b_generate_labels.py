import os
import json
import pandas as pd
import datetime

def generate_labels():
    unified_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\unified_v2"
    labels_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labels"
    labeled_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labeled_v2"
    timeline_path = os.path.join(labels_dir, "cicids2017_attack_timeline.json")
    
    os.makedirs(labels_dir, exist_ok=True)
    os.makedirs(labeled_dir, exist_ok=True)
    
    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
        
    # Convert ADT timeline to UTC epoch boundaries
    attack_events = []
    for ev in timeline['events']:
        dt_start_str = f"{ev['date']} {ev['start']}"
        dt_end_str = f"{ev['date']} {ev['end']}"
        # Parse as ADT (UTC-3)
        dt_start = datetime.datetime.strptime(dt_start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
        dt_end = datetime.datetime.strptime(dt_end_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
        
        attack_events.append({
            "date": ev['date'],
            "attack": ev['attack'],
            "start_epoch": dt_start.timestamp(),
            "end_epoch": dt_end.timestamp(),
            "source": ev['source'],
            "confidence": ev['confidence']
        })
        
    days = [
        ("Monday-WorkingHours_unified.parquet", "2017-07-03", "monday"),
        ("Tuesday-WorkingHours_unified.parquet", "2017-07-04", "tuesday"),
        ("Wednesday-workingHours_unified.parquet", "2017-07-05", "wednesday"),
        ("Thursday-WorkingHours_unified.parquet", "2017-07-06", "thursday"),
        ("Friday-WorkingHours_unified.parquet", "2017-07-07", "friday")
    ]
    
    for filename, date_str, prefix in days:
        print(f"Processing {prefix}...")
        parquet_path = os.path.join(unified_dir, filename)
        if not os.path.exists(parquet_path):
            continue
            
        df = pd.read_parquet(parquet_path)
        
        # We only need window_start for labeling, but we will create the labels DataFrame then join it
        unique_windows = df[['window_start']].drop_duplicates().copy()
        unique_windows['window_end'] = unique_windows['window_start'] + 5.0
        
        # Default benign
        unique_windows['attack_binary'] = 0
        unique_windows['attack_type'] = "BENIGN"
        unique_windows['attack_family'] = "BENIGN"
        unique_windows['label'] = "BENIGN"
        unique_windows['ground_truth_source'] = "CIC-IDS2017 Official Schedule"
        unique_windows['label_confidence'] = "high"
        
        # Find daily attacks
        day_attacks = [e for e in attack_events if e['date'] == date_str]
        
        # Policy: overlap >= 1 second
        # overlap = min(w_end, a_end) - max(w_start, a_start)
        for ev in day_attacks:
            a_start = ev['start_epoch']
            a_end = ev['end_epoch']
            
            # PCAP range check
            pcap_min = unique_windows['window_start'].min()
            pcap_max = unique_windows['window_end'].max()
            if a_start < pcap_min or a_end > pcap_max:
                print(f"WARNING: Attack {ev['attack']} ({a_start}-{a_end}) falls outside PCAP range ({pcap_min}-{pcap_max}) for {date_str}!")
            
            overlap_condition = (unique_windows['window_end'].clip(upper=a_end) - unique_windows['window_start'].clip(lower=a_start)) >= 1.0
            
            unique_windows.loc[overlap_condition, 'attack_binary'] = 1
            unique_windows.loc[overlap_condition, 'attack_type'] = ev['attack']
            unique_windows.loc[overlap_condition, 'attack_family'] = ev['attack']
            unique_windows.loc[overlap_condition, 'label'] = ev['attack']
            
        # Save labels
        labels_out = os.path.join(labels_dir, f"{prefix}_labels.parquet")
        unique_windows.to_parquet(labels_out, index=False)
        
        # Join dataset
        labeled_out = os.path.join(labeled_dir, f"{prefix}_labeled.parquet")
        df_labeled = df.merge(unique_windows, on='window_start', how='left')
        df_labeled.to_parquet(labeled_out, index=False)
        
        print(f"Finished {prefix}: {len(unique_windows)} unique windows, {unique_windows['attack_binary'].sum()} attack windows.")

if __name__ == '__main__':
    generate_labels()
