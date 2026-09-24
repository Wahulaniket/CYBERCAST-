# CIC-IDS2017 PCAP Inventory Report

## 1. Overview
This report documents the findings from inspecting the raw PCAP files for the CIC-IDS2017 dataset.

## 2. File Verification
- **Total Expected Size:** ~52.3 GB
- **Total Actual Size:** 52.43 GB
- **Format:** PCAPNG

## 3. Parsing Status
The files were parsed sequentially using `dpkt.pcapng` without loading entire files into RAM.

| File | Status | Packets | Duration (s) | Peak RAM (MB) | Time (s) |
|---|---|---|---|---|---|
| Monday-WorkingHours.pcap | PASS | 11,709,971 | 29135.87 | 23.17 | 306.72 |
| Tuesday-WorkingHours.pcap | PASS | 11,551,954 | 29218.71 | 23.74 | 286.99 |
| Wednesday-workingHours.pcap | PASS | 13,788,878 | 30457.70 | 24.08 | 162.23 |
| Thursday-WorkingHours.pcap | PASS | 9,322,025 | 29145.87 | 24.16 | 220.72 |
| Friday-WorkingHours.pcap | PASS | 9,997,874 | 28981.57 | 24.23 | 200.01 |

## 4. Hardware Feasibility
Peak RAM never exceeded 25 MB because packets were processed sequentially and aggressively discarded. Complete processing over 52.43 GB of raw network data took ~20 minutes on CPU (Intel i5). CPU and Disk throughput are well-aligned for robust data-pipelining.
