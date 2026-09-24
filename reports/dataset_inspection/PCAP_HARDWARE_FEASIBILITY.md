# PCAP Hardware Feasibility

## Hardware
- **CPU:** Intel i5
- **GPU:** RTX 2050 4 GB VRAM (Not used for this phase)

## Processing Strategy
- Sequential processing using streaming parser (`dpkt.pcapng`)
- Bounded RAM usage approach

## Metrics
- Peak RAM usage remained well within system limits.
- Processing is CPU and Disk bound.

## Conclusion
Streaming analysis is viable on this hardware.
