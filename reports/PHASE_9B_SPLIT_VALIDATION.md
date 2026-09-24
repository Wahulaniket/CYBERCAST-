# Phase 9B Split Validation

## Split Definitions
- **TRAIN:** Monday, Tuesday, Wednesday
- **VALIDATION:** Thursday
- **TEST:** Friday

## Attack Categories per Split
### Training Attack Types
- FTP-Patator
- SSH-Patator
- DoS-Slowloris
- DoS-SlowHTTPTest
- DoS-Hulk
- DoS-GoldenEye
- Heartbleed

### Validation Attack Types
- Web-BruteForce
- Web-XSS
- Web-SQLInjection
- Infiltration

### Test Attack Types
- Botnet
- PortScan
- DDoS

## Held-Out Attack Verification
- **TEST-ONLY ATTACK TYPES:** `[Botnet, PortScan, DDoS]`
- None of the Friday attack typologies appear in the Training or Validation splits.
- **HELD_OUT_ATTACK_TYPE = TRUE**

## Sequence Boundaries
- Sequences of length `L=10` are constructed continuously within a single dataset-day.
- No sequence is permitted to cross midnight (e.g., from Monday 23:59:59 to Tuesday 00:00:00).
- This ensures zero temporal session bleed between train, validation, and test boundaries.
