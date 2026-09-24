# Granularity Analysis

**FLOW LEVEL**: High coverage for most features (bytes, packets, duration, IAT).

**PACKET LEVEL**: Extremely poor coverage. The dataset consists of pre-extracted flow records (CSV/Parquet). PCAP files are NOT present. Missing TTL, IP fragments, retransmissions, exact payload distributions. These cannot be invented. They must be marked as unavailable.