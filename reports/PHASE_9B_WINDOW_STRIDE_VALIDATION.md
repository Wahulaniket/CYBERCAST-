# Phase 9B Window Stride Validation

| Day | Rows | Window Duration | Median Stride | Min Stride | Max Stride | Window Type |
| --- | ---: | --------------: | ------------: | ---------: | ---------: | ----------- |
| Monday | 795,929 | 5.0 | 5.0 | 5.0 | 25.0 | NON_OVERLAPPING_5S |
| Tuesday | 720,406 | 5.0 | 5.0 | 5.0 | 15.0 | NON_OVERLAPPING_5S |
| Wednesday | 970,998 | 5.0 | 5.0 | 5.0 | 60.0 | NON_OVERLAPPING_5S |
| Thursday | 747,123 | 5.0 | 5.0 | 5.0 | 15.0 | NON_OVERLAPPING_5S |
| Friday | 989,670 | 5.0 | 5.0 | 5.0 | 15.0 | NON_OVERLAPPING_5S |

## Sample Timestamps (Monday)
| window_start | window_end | delta_to_next_window |
| ------------ | ---------- | -------------------- |
| 1499082955.0 | 1499082960.0 | 25.0 |
| 1499082980.0 | 1499082985.0 | 15.0 |
| 1499082995.0 | 1499083000.0 | 5.0 |
| 1499083000.0 | 1499083005.0 | 5.0 |
| 1499083005.0 | 1499083010.0 | 10.0 |
| 1499083015.0 | 1499083020.0 | 5.0 |
| 1499083020.0 | 1499083025.0 | 5.0 |
| 1499083025.0 | 1499083030.0 | 5.0 |
| 1499083030.0 | 1499083035.0 | 5.0 |
| 1499083035.0 | 1499083040.0 | 5.0 |

**Note:** Gaps > 5.0 seconds simply represent natural silence / absence of traffic in the dataset, but the windows themselves do not overlap.
