# Unified Flow Schema

Core Fields:
- timestamp
- source_ip
- destination_ip
- source_port
- destination_port
- protocol
- flow_id

Traffic Features:
- flow_duration
- total_bytes
- total_packets
- bytes_per_second
- packets_per_second

TCP Features (NaN if unavailable):
- syn_flag
- ack_flag
- fin_flag
- rst_flag
- psh_flag
- urg_flag

Timing:
- iat_mean
- iat_std
- iat_max

Labels:
- label (0/1)
- attack_type
- dataset_source
