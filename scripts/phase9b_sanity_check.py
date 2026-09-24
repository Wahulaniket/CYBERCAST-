import os
import json
import pandas as pd
import numpy as np
import datetime

def main():
    unified_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\unified_v2"
    labels_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labels"
    reports_dir = r"D:\working_projects\SIH\cyberCast2\reports"
    
    files = [
        "Monday-WorkingHours_unified.parquet",
        "Tuesday-WorkingHours_unified.parquet",
        "Wednesday-workingHours_unified.parquet",
        "Thursday-WorkingHours_unified.parquet",
        "Friday-WorkingHours_unified.parquet"
    ]
    
    stride_stats = []
    sample_timestamps = {}
    
    for filename in files:
        path = os.path.join(unified_dir, filename)
        if not os.path.exists(path):
            continue
            
        df = pd.read_parquet(path, columns=['window_start'])
        
        # Unique window starts sorted
        starts = np.sort(df['window_start'].unique())
        deltas = np.diff(starts)
        
        if len(deltas) > 0:
            min_delta = float(np.min(deltas))
            max_delta = float(np.max(deltas))
            median_delta = float(np.median(deltas))
            mean_delta = float(np.mean(deltas))
            unique_deltas = len(np.unique(deltas))
            
            # Most common delta
            values, counts = np.unique(deltas, return_counts=True)
            most_common = float(values[np.argmax(counts)])
            
            pct_equal_5 = float(np.sum(deltas == 5.0) / len(deltas)) * 100
            pct_less_5 = float(np.sum(deltas < 5.0) / len(deltas)) * 100
            pct_greater_5 = float(np.sum(deltas > 5.0) / len(deltas)) * 100
        else:
            min_delta = max_delta = median_delta = mean_delta = most_common = 0.0
            unique_deltas = 0
            pct_equal_5 = pct_less_5 = pct_greater_5 = 0.0
            
        # Assuming duration is always exactly 5.0 because we defined it that way
        window_duration = 5.0 
        
        stride_stats.append({
            "Day": filename.split('-')[0],
            "Rows": len(df),
            "Unique Windows": len(starts),
            "Window Duration": window_duration,
            "Median Stride": median_delta,
            "Min Stride": min_delta,
            "Max Stride": max_delta,
            "Most Common Stride": most_common,
            "Pct == 5s": pct_equal_5,
            "Pct < 5s": pct_less_5,
            "Pct > 5s": pct_greater_5,
            "First 20": starts[:20].tolist(),
            "Deltas": deltas[:20].tolist() if len(deltas) > 0 else []
        })
        
    stride_df = pd.DataFrame(stride_stats)
    stride_df.to_json(os.path.join(reports_dir, "stride_stats.json"), indent=2, orient='records')

if __name__ == '__main__':
    main()
