# Real-Data Independent Verification Package

This directory contains an independently verified real-data test set extracted from CSE-CIC-IDS2018.

## Files
- `test_telemetry.csv`: 30-feature inputs (5s windows)
- `ground_truth.csv`: Unseen ground truth matching the windows
- `verification_results.csv`: Offline verification predictions
- `verification_report.md`: Summary of the test and metrics

## Usage with Dashboard
1. Start Streamlit: `streamlit run dashboard/app.py`
2. Upload `test_telemetry.csv`
3. Run K=1, 3, 5, 10
4. Keep `ground_truth.csv` OUTSIDE the dashboard.
