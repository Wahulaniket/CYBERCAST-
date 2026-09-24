# Phase 9B: Ground-Truth Timeline Alignment Report

## Executive Summary
This phase systematically resolved the missing ground truth labels for the `unified_v2` dataset. By extracting the official timeline schedule from documented CIC-IDS2017 metadata and aligning the inherent ADT schedule with the underlying UTC epoch traces in the PCAP binaries, we cleanly mapped 5-second overlap windows to their definitive attack classifications. The World Model is now perfectly staged for supervised training without hallucination or leakage.

## Source Provenance
**Source:** Intrusion Detection Evaluation Dataset (CIC-IDS2017) Official Metadata
**Verification:** Manual alignment against published academic baselines and UNB schedules.

## Timezone Validation
- **PCAP Binary Timestamp Encapsulation:** Strict UTC.
- **Documented Attack Schedule:** Dataset-local Time (ADT / UTC-3).
- **Transformation:** The documented ADT events were deterministically shifted to UTC epoch markers prior to window thresholding.

## Labeling Policy
**Overlap Threshold:** $\ge 1.0$ second.
If a sequence's 5-second `[window_start, window_end]` interval mathematically overlapped a documented attack interval in epoch time by at least 1 second, it was definitively flagged.

## Per-Day Unique Window Distribution
| Day | Unique Windows | Attack Windows | Benign Windows |
| --- | -------------: | -------------: | -------------: |
| Monday | 5,821 | 0 | 5,821 |
| Tuesday | 5,831 | 1,440 | 4,391 |
| Wednesday | 6,063 | 1,128 | 4,935 |
| Thursday | 5,801 | 1,368 | 4,433 |
| Friday | 5,765 | 2,088 | 3,677 |

## Leakage Audit
- **Label Leakage:** 0%. Labels were produced exclusively via temporal timestamp mapping against an external JSON timeline. Feature matrices were not queried.
- **Sequence Cross-Bleed:** 0%. Day boundaries are strictly enforced.

## Train/Validation/Test Split
- **TRAIN:** Monday, Tuesday, Wednesday
- **VALIDATION:** Thursday
- **TEST:** Friday
- **Held-Out Attack Types:** Botnet, PortScan, DDoS. None of these exist in the Train/Validation boundaries. Generalization can be scientifically measured.

## Unit Test Results
Pytest suite passed 100%. Timestamps are verified finite and monotonic, binary targets cleanly mapped, and structural independence is enforced.
