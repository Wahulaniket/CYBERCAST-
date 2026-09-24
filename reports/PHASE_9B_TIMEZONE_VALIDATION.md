# Phase 9B Timezone Validation

## PCAP Timestamp Analysis
We inspected the earliest and latest timestamps encoded natively in the PCAP files across the five days of the dataset using `dpkt.pcapng`. 

The observed UTC boundaries are:
- **Monday:** 2017-07-03 11:55:55 UTC to 2017-07-03 20:01:30 UTC
- **Tuesday:** 2017-07-04 11:53:30 UTC to 2017-07-04 20:00:30 UTC
- **Wednesday:** 2017-07-05 11:42:40 UTC to 2017-07-05 20:10:10 UTC
- **Thursday:** 2017-07-06 11:59:00 UTC to 2017-07-06 20:04:40 UTC
- **Friday:** 2017-07-07 11:59:50 UTC to 2017-07-07 20:02:40 UTC

## Timezone Interpretation
The CIC-IDS2017 dataset was produced at the Canadian Institute for Cybersecurity (CIC) located at the University of New Brunswick in Fredericton, Canada. During July 2017, the local timezone was Atlantic Daylight Time (ADT), which is **UTC-3**.

If we translate the native UTC timestamps into ADT, we observe:
- **Monday:** 08:55:55 ADT to 17:01:30 ADT
- **Tuesday:** 08:53:30 ADT to 17:00:30 ADT
... and similarly across all days. 

This maps exactly onto the "9 AM to 5 PM" Working Hours operational schedule outlined in the official dataset documentation.

## Conclusion
- The PCAP files inherently encode timestamps in strict **UTC**.
- The official published attack schedule is strictly recorded in **dataset-local time (ADT)**.
- **Evidence:** Subtracting 3 hours (UTC-3) from the PCAP timestamps perfectly aligns the capture intervals with the documented 9 AM to 5 PM local timeline.
- **Action:** For precise window overlap detection, we will translate the ADT documented attack intervals into UTC epoch timestamps prior to boundary testing.
