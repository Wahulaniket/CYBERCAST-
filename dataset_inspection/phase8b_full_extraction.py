import sys
import os
import time
import dpkt
import psutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from packet_extractor import process_packet, extract_features_from_window

pcap_dir = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\PCAPs\pcaps"
output_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\packet_features"
os.makedirs(output_dir, exist_ok=True)

def flush_window(windows, window_idx, rows):
    if window_idx in windows:
        for flow_key, state in windows[window_idx].items():
            f = extract_features_from_window(flow_key, window_idx, state)
            rows.append(f)
        del windows[window_idx]

def extract_features(filename, pcap_path, is_validation=False):
    print(f"\nProcessing {filename}...")
    start_time = time.time()
    
    windows = {}
    current_max_window_index = -1
    last_flushed_idx = -1
    rows = []
    
    packet_count = 0
    window_count = 0
    process = psutil.Process(os.getpid())
    peak_mem = process.memory_info().rss
    
    parquet_path = os.path.join(output_dir, filename.replace('.pcap', '_packet_features.parquet'))
    pq_writer = None
    schema = None
    
    try:
        with open(pcap_path, 'rb') as f:
            reader = dpkt.pcapng.Reader(f)
            for i, (ts, buf) in enumerate(reader):
                window_idx = process_packet(ts, buf, windows)
                packet_count += 1
                
                if window_idx > current_max_window_index:
                    if current_max_window_index == -1:
                        last_flushed_idx = window_idx - 3
                    current_max_window_index = window_idx
                    
                # Flush windows older than max - 2 (10s jitter allowed)
                while last_flushed_idx < current_max_window_index - 2:
                    last_flushed_idx += 1
                    if last_flushed_idx in windows:
                        flush_window(windows, last_flushed_idx, rows)
                        
                        # Periodically write to parquet
                        if len(rows) >= 10000:
                            window_count += len(rows)
                            df = pd.DataFrame(rows)
                            table = pa.Table.from_pandas(df)
                            if pq_writer is None:
                                schema = table.schema
                                pq_writer = pq.ParquetWriter(parquet_path, schema)
                            pq_writer.write_table(table)
                            rows = []
                
                if i % 100000 == 0:
                    current_mem = process.memory_info().rss
                    if current_mem > peak_mem:
                        peak_mem = current_mem
                        
                if is_validation and packet_count >= 10000:
                    break
                    
    except Exception as e:
        print(f"Error parsing {filename} at packet {packet_count}: {e}")

    # Flush remaining windows
    for idx in sorted(list(windows.keys())):
        flush_window(windows, idx, rows)
        
    if len(rows) > 0:
        window_count += len(rows)
        df = pd.DataFrame(rows)
        table = pa.Table.from_pandas(df)
        if pq_writer is None:
            schema = table.schema
            pq_writer = pq.ParquetWriter(parquet_path, schema)
        pq_writer.write_table(table)
        
    if pq_writer is not None:
        pq_writer.close()
        
    end_time = time.time()
    current_mem = process.memory_info().rss
    if current_mem > peak_mem:
        peak_mem = current_mem
        
    print(f"Finished {filename}")
    print(f"Packets processed: {packet_count}")
    print(f"Windows emitted: {window_count}")
    print(f"Processing time: {end_time - start_time:.2f} s")
    print(f"Peak RAM: {peak_mem / (1024*1024):.2f} MB")
    
    return {
        'file': filename,
        'packets': packet_count,
        'windows': window_count,
        'time': end_time - start_time,
        'ram': peak_mem / (1024*1024)
    }

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'validation'
    
    files = [
        "Monday-WorkingHours.pcap",
        "Tuesday-WorkingHours.pcap",
        "Wednesday-workingHours.pcap",
        "Thursday-WorkingHours.pcap",
        "Friday-WorkingHours.pcap"
    ]
    
    if mode == 'validation':
        print("Running validation on Monday...")
        extract_features("Monday-WorkingHours.pcap", os.path.join(pcap_dir, "Monday-WorkingHours.pcap"), is_validation=True)
        # Check validation output
        df = pd.read_parquet(os.path.join(output_dir, "Monday-WorkingHours_packet_features.parquet"))
        print("\nValidation Dataset shape:", df.shape)
        print(df.head())
    elif mode == 'full':
        print("Running full extraction...")
        stats = []
        for filename in files:
            path = os.path.join(pcap_dir, filename)
            s = extract_features(filename, path)
            stats.append(s)
            
        print("\nFULL EXTRACTION DONE")
        print(stats)
