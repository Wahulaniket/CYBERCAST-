import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates

BASE_DIR = "d:/working_projects/SIH/cyberCast2"
TEST_DIR = os.path.join(BASE_DIR, "demo/real_verification")
df = pd.read_csv(os.path.join(TEST_DIR, "verification_results.csv"))

df['timestamp'] = pd.to_datetime(df['timestamp'])

fig, ax = plt.subplots(figsize=(10, 6))

# Plot Predicted Risk
ax.plot(df['timestamp'], df['predicted_risk'], color='blue', label='Predicted Risk (Mock Model)')

# Highlight ground truth attack period
attack_periods = df[df['ground_truth_attack'] == 'ATTACK']
if not attack_periods.empty:
    ax.fill_between(df['timestamp'], 0, 1, where=(df['ground_truth_attack'] == 'ATTACK'), 
                    color='red', alpha=0.3, label='Ground Truth Attack')

ax.set_title('Ground-Truth Attack Period vs Predicted Risk')
ax.set_ylabel('Risk Score')
ax.set_xlabel('Time')
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(os.path.join(TEST_DIR, "risk_vs_ground_truth.png"))
