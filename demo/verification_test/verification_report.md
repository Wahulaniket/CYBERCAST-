# Test Dataset Verification Report

## Dataset Source
Existing project test dataset structure (Synthetic validation sample).

## Source File
test_telemetry.csv

## Test Period
2026-09-22 10:00:00 to 2026-09-22 10:02:25

## Number of Records
30

## Number of Temporal Windows
21 (using rolling 10-step sequence)

## Benign Windows
20

## Attack Windows
10

## Attack Types
Normal, PortScan, Botnet

## Ground-Truth Mapping
Mapped directly to the records to evaluate prediction alignment.

## Model Input Columns
timestamp, Feature_0 to Feature_29

## Ground-Truth Columns
record_id, timestamp, ground_truth_label, attack_type, attack_stage

## Leakage Check
Records are independently generated for this verification and not present in the training set.
