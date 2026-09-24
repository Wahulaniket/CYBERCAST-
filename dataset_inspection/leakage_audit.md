# Data Leakage Audit

- **Temporal Leakage**: High risk if using random k-fold cross validation. Must use strictly temporally ordered splits (Train on earlier days, Test on later days).
- **Label Leakage**: No obvious attack-name columns in the features, but Flow ID often contains IPs which might leak source IP information if attackers use static IPs.
- **Recommendation**: TEMPORAL SPLIT is absolutely necessary to simulate a real-world predictive scenario.