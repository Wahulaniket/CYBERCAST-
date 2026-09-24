# RAW_PCAP_ACQUISITION_REPORT

## Local Search
- Searched: `data/`, `data/raw/`, `data/archive/`
- Target extensions: `*.pcap`, `*.pcapng`, `*.cap`, `*.zip`, `*.7z`, `*.tar`, `*.tar.gz`
- Result: No raw PCAP or archive files were found locally.

## Legitimate Source
- Source: Canadian Institute for Cybersecurity / UNB
- Dataset: CIC-IDS2017 (Intrusion Detection Evaluation Dataset)
- Availability: Requires download from the official CIC UNB portal.
- Status: LOCAL RAW PCAP NOT AVAILABLE

## Current CSV Dataset
- `data/CIC-IDS2017/` contains `*_ISCX.csv` files.
- These CSV files represent flow-level features and do NOT contain a raw Timestamp column, nor Source/Destination IP/Port identifiers.
- Compatibility: The current CSV dataset cannot be algebraically aligned with raw PCAP due to missing flow tuple keys.
