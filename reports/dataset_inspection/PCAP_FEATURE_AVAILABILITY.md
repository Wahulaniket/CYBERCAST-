# PCAP Feature Availability

This document lists whether essential network traffic features could be successfully extracted from the raw PCAP files.

## Observed Features

| Feature | Available | Note |
|---|---|---|
| TTL | YES | Extracted from IPv4/IPv6 header |
| TCP Window | YES | Extracted from TCP header |
| IP Fragmentation | YES | Flags/Offsets extracted from IP header |
| Payload Length | YES | Computed from packet length |
| Source Port | YES | Extracted from TCP/UDP header |
| Destination Port | YES | Extracted from TCP/UDP header |
| TCP Sequence | YES | Extracted from TCP header |
| TCP ACK | YES | Extracted from TCP header |
| Packet Timestamp | YES | Provided by PCAPNG reader |
