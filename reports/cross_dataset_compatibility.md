# Cross Dataset Compatibility
- **CIC-IDS2017 & CSE-CIC-IDS2018**: Highly compatible. Both generated using CICFlowMeter. Schemas align nicely.
- **CTU-13**: Incompatible directly at feature level (Argus flow vs CICFlowMeter). Missing crucial TCP flags and IAT stats.
- **Conclusion**: Train on IDS2017, Test on IDS2018 is highly viable. CTU-13 requires a reduced subset of common features (bytes, packets, duration, protocol).
