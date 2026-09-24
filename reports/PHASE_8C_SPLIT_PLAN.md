# Temporal Split Plan for Unified Packet + Flow Data

## Leakage Risks in Random Splits
Network attacks, particularly multi-stage campaigns, port scans, and DDoS events, are intrinsically temporal. Randomly splitting individual 5-second network state windows across training and test sets would inevitably place chunks of the *same* continuous attack into both splits. This guarantees severe temporal leakage, inflating test metrics and falsely claiming generalization.

## Planned Temporal Separation Strategy
The optimal strategy strictly isolates entire days of traffic into training, validation, and test datasets.

### Proposed Split:
- **Training Set:** Monday (Benign only), Tuesday (Benign + Brute Force), Wednesday (Benign + Web Attacks).
- **Validation Set:** Thursday (Benign + Infiltration/Web Attacks).
- **Test Set:** Friday (Benign + DDoS, PortScan, Botnet).

### Rationale:
1. **Unseen Attack Generalization:** Friday contains distinct attack typologies (DDoS, Botnet) that differ procedurally from the Tuesday/Wednesday traffic. Holding Friday strictly out as the Test Set forces the model to generalize to structurally novel attacks.
2. **Temporal Independence:** Splitting by day guarantees zero session bleed. No flow state from an ongoing attack on Friday can leak into Thursday's validation split.
3. **Data Imbalance Management:** Monday establishes strong baseline benign representations. Tuesday and Wednesday provide initial structural deviations.

### Conclusion
This temporal separation strategy correctly evaluates predictive cyber-defense against unseen future states without introducing temporal or identifier leakage.
