import os
import json
import pandas as pd
import datetime

def main():
    unified_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\unified_v2"
    labels_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labels"
    reports_dir = r"D:\working_projects\SIH\cyberCast2\reports"
    
    with open(os.path.join(labels_dir, "cicids2017_attack_timeline.json"), 'r') as f:
        timeline = json.load(f)
        
    days = [
        ("Monday-WorkingHours_unified.parquet", "2017-07-03", "monday"),
        ("Tuesday-WorkingHours_unified.parquet", "2017-07-04", "tuesday"),
        ("Wednesday-workingHours_unified.parquet", "2017-07-05", "wednesday"),
        ("Thursday-WorkingHours_unified.parquet", "2017-07-06", "thursday"),
        ("Friday-WorkingHours_unified.parquet", "2017-07-07", "friday")
    ]
    
    pcap_bounds = {}
    for filename, date_str, prefix in days:
        path = os.path.join(unified_dir, filename)
        if os.path.exists(path):
            df = pd.read_parquet(path, columns=['window_start'])
            p_min = df['window_start'].min()
            p_max = df['window_start'].max() + 5.0
            pcap_bounds[date_str] = (p_min, p_max)
            
    report_lines = []
    report_lines.append("| Day | Attack | Documented ADT Start | Documented ADT End | Converted UTC Start | Converted UTC End | Inside PCAP? |")
    report_lines.append("| --- | ------ | -------------------- | ------------------ | ------------------- | ----------------- | ------------ |")
    
    all_inside = True
    
    for ev in timeline['events']:
        date_str = ev['date']
        dt_start_str = f"{date_str} {ev['start']}"
        dt_end_str = f"{date_str} {ev['end']}"
        
        dt_start_adt = datetime.datetime.strptime(dt_start_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
        dt_end_adt = datetime.datetime.strptime(dt_end_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
        
        utc_start = dt_start_adt.timestamp()
        utc_end = dt_end_adt.timestamp()
        
        dt_start_utc_str = datetime.datetime.fromtimestamp(utc_start, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        dt_end_utc_str = datetime.datetime.fromtimestamp(utc_end, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        p_min, p_max = pcap_bounds.get(date_str, (0, 0))
        
        inside = (utc_start >= p_min) and (utc_end <= p_max)
        if not inside:
            all_inside = False
            
        report_lines.append(f"| {date_str} | {ev['attack']} | {dt_start_str} | {dt_end_str} | {dt_start_utc_str} | {dt_end_utc_str} | {inside} |")
        
    with open(os.path.join(reports_dir, "timeline_check.md"), "w") as f:
        f.write("\n".join(report_lines))

if __name__ == '__main__':
    main()
