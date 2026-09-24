# Feature Engineering Pipeline

1. Numeric Conversion: Convert string metrics to float32.
2. Timestamp Parsing: Convert to UNIX epoch.
3. NaN Handling: Impute missing TCP flags with 0, missing numericals with 0 or NaN.
4. Infinity Handling: Replace `inf` with the 99th percentile value of the feature.
5. IP Handling: Extract unique IP/Port counts per time window.
6. Derived Features:
   - `port_scan_rate`: unique_dst_ports / window_duration
   - `syn_failure_ratio`: (syn_flags - ack_flags) / syn_flags
   - `bytes_per_flow`: total_bytes / flow_count
