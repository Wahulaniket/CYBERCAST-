import os
import zipfile
import json
import pandas as pd
import pyarrow.parquet as pq

def inspect_alignment():
    report = {
        "packet_parquet_files": [],
        "parquet_schemas": {},
        "parquet_stats": {},
        "flow_csv_files": [],
        "flow_csv_columns": [],
        "csv_timestamp_available": False,
        "csv_ip_available": False,
        "csv_port_available": False,
        "csv_label_available": False
    }

    parquet_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\packet_features"
    if os.path.exists(parquet_dir):
        for f in os.listdir(parquet_dir):
            if f.endswith(".parquet"):
                report["packet_parquet_files"].append(f)
                p = os.path.join(parquet_dir, f)
                try:
                    pf = pq.ParquetFile(p)
                    schema = pf.schema_arrow
                    report["parquet_schemas"][f] = schema.names
                    
                    # Check min/max timestamp by reading just window_start column
                    df_win = pf.read(columns=['window_start', 'flow_id']).to_pandas()
                    report["parquet_stats"][f] = {
                        "num_rows": len(df_win),
                        "min_timestamp": float(df_win['window_start'].min()),
                        "max_timestamp": float(df_win['window_start'].max()),
                        "unique_windows": int(df_win['window_start'].nunique()),
                        "unique_flows": int(df_win['flow_id'].nunique())
                    }
                except Exception as e:
                    report["parquet_schemas"][f] = f"Error reading file: {e}"

    csv_zip = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\CSVs\MachineLearningCSV.zip"
    if os.path.exists(csv_zip):
        with zipfile.ZipFile(csv_zip, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            report["flow_csv_files"] = csv_files
            if csv_files:
                with z.open(csv_files[0]) as f:
                    df_csv = pd.read_csv(f, nrows=5)
                    cols = [c.strip() for c in df_csv.columns]
                    report["flow_csv_columns"] = cols
                    
                    report["csv_timestamp_available"] = any("timestamp" in c.lower() for c in cols)
                    report["csv_ip_available"] = any("ip" in c.lower() for c in cols)
                    report["csv_port_available"] = any("port" in c.lower() for c in cols)
                    report["csv_label_available"] = any("label" in c.lower() for c in cols)
                    
                    report["csv_sample_data"] = df_csv.head(1).to_dict(orient='records')

    reports_dir = r"D:\working_projects\SIH\cyberCast2\reports"
    os.makedirs(reports_dir, exist_ok=True)
    with open(os.path.join(reports_dir, "PHASE_8C_ALIGNMENT_INSPECTION.json"), "w") as f:
        json.dump(report, f, indent=4)

if __name__ == "__main__":
    inspect_alignment()
