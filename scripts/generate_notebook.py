import nbformat as nbf
import os
import json

nb = nbf.v4.new_notebook()

# Section 1
nb.cells.append(nbf.v4.new_markdown_cell("""# PHASE 9 — PROFESSIONAL ML TRAINING NOTEBOOK
## Flow + Packet World Model V2

---
## SECTION 1 — Project Overview

### Problem
Traditional intrusion detection classifies individual traffic observations in isolation. This project instead models network behaviour as a temporal process.

Define:
$S_t$ = network state at time $t$

The learned transition model approximates:
$$P(S_{t+1} | S_t, \dots, S_{t-L+1})$$
where $L$ is the temporal context length. The model additionally estimates future attack risk at horizon $H$.

**Note**: This is a *learned predictive approximation* of network-state dynamics, not a causal model. It provides future attack-risk estimates, not direct attacker intent.
"""))

# Section 2
nb.cells.append(nbf.v4.new_markdown_cell("""## SECTION 2 — System Architecture Diagram

```mermaid
graph TD
    %% OBSERVATION
    A[Raw PCAP] --> B(Streaming Packet Parser)
    B --> C(Flow Feature Extraction)
    B --> D(Packet Feature Extraction)
    C --> E[5-second Temporal State]
    D --> E
    E --> F[Unified Feature Vector]
    
    %% MODEL
    F --> G[Normalization / Scaling]
    G --> H[Sequence Builder]
    H --> I[Temporal LSTM]
    
    %% FORECAST
    I --> J[State Decoder]
    I --> K[Risk Head]
    
    J --> L[S t+1 forecast]
    K --> M[P Attack]
    
    L --> N[K-Step Rollout]
    M --> O[Attack Progression Forecast]
    
    %% DECISION SUPPORT
    N --> P[Explainability]
    O --> Q[ATT&CK-aligned Stage]
```
"""))

# Section 3
nb.cells.append(nbf.v4.new_markdown_cell("""## SECTION 3 — Data Pipeline Diagram

```mermaid
graph LR
    A[Raw PCAP] --> B[packet parsing]
    B --> C[flow aggregation]
    B --> D[packet aggregation]
    C --> E[5-second windows]
    D --> E
    E --> F[unified state]
    F --> G[train/validation/test splits]
    G --> H[sequences]
    H --> I[Model]
    
    Z[Separate Ground Truth Labels] --> G
    
    classDef feature fill:#e1f5fe,stroke:#01579b;
    classDef label fill:#fce4ec,stroke:#880e4f;
    class F feature;
    class Z label;
```
*Note: Labels are strictly kept outside the unified feature matrix (FEATURES ≠ LABELS).*
"""))

# Section 4
nb.cells.append(nbf.v4.new_markdown_cell("## SECTION 4 — Dataset Validation"))
nb.cells.append(nbf.v4.new_code_cell("""import pandas as pd
import json
import os
import glob

data_dir = r"D:\\working_projects\\SIH\\cyberCast2\\data\\processed\\unified_v2"
manifest_path = os.path.join(data_dir, "manifest.json")

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

print("=== MANIFEST SUMMARY ===")
print(json.dumps(manifest, indent=2))

parquet_files = glob.glob(os.path.join(data_dir, "*.parquet"))
total_rows = 0
total_size = 0

for pf in parquet_files:
    size = os.path.getsize(pf)
    total_size += size
    df_sample = pd.read_parquet(pf, columns=['window_start'])
    total_rows += len(df_sample)

print(f"\\nActual Parquet Files Found: {len(parquet_files)}")
print(f"Actual Total Rows (Windows): {total_rows}")
print(f"Actual Disk Size: {total_size / (1024*1024):.2f} MB")
"""))

# Section 5
nb.cells.append(nbf.v4.new_markdown_cell("## SECTION 5 — Feature Schema"))
nb.cells.append(nbf.v4.new_code_cell("""schema_path = r"D:\\working_projects\\SIH\\cyberCast2\\models\\feature_schema_packet_v2.json"
with open(schema_path, 'r') as f:
    schema = json.load(f)

df_schema = pd.DataFrame(schema)
display(df_schema[['feature_name', 'source', 'aggregation', 'data_type']])
"""))

# Section 6
nb.cells.append(nbf.v4.new_markdown_cell("## SECTION 6 — Exploratory Data Analysis"))
nb.cells.append(nbf.v4.new_code_cell("""import matplotlib.pyplot as plt
import seaborn as sns
import pyarrow.parquet as pq

# Load a sample of Monday for EDA
df_eda = pd.read_parquet(os.path.join(data_dir, "Monday-WorkingHours_unified.parquet"))

features_to_plot = ['packet_count', 'flow_byte_count', 'ttl_variance', 'syn_ratio', 'payload_mean']

fig, axes = plt.subplots(1, len(features_to_plot), figsize=(20, 4))
for ax, feat in zip(axes, features_to_plot):
    if feat in df_eda.columns:
        sns.histplot(df_eda[feat].replace([float('inf'), float('-inf')], pd.NA).dropna(), bins=50, ax=ax)
        ax.set_title(feat)
        ax.set_yscale('log')
plt.tight_layout()
plt.show()

# Correlation Matrix
corr_cols = features_to_plot + ['destination_port_entropy', 'tcp_retransmission_ratio', 'packet_iat_mean']
corr_data = df_eda[corr_cols].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr_data, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Heatmap (Selected Features)")
plt.show()
"""))

# Section 7
nb.cells.append(nbf.v4.new_markdown_cell("""## SECTION 7 — Ground Truth Validation

### Label Verification
Checking if ground truth labels have been perfectly aligned onto the newly constructed 5-second overlapping contiguous windows.
"""))
nb.cells.append(nbf.v4.new_code_cell("""# Check label alignment status
if "NOT_YET_ALIGNED" in manifest.get('label_status', ''):
    print("LABEL_STATUS = NOT_READY")
    print("STOPPING NOTEBOOK EXECUTION.")
    print("\\nREASON: Labels from the original CSV datasets cannot be reliably mapped to the unified PCAP windows at this time because the original CSVs completely scrubbed exact IP addresses and microsecond timestamps. Fabricating or hallucinating label overlays would violate strict scientific and project rules.")
else:
    print("LABEL_STATUS = READY")
"""))

# Create dirs and save
os.makedirs(r"D:\working_projects\SIH\cyberCast2\notebooks", exist_ok=True)
notebook_path = r"D:\working_projects\SIH\cyberCast2\notebooks\Phase_9_World_Model_V2_Professional_Training.ipynb"
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
