### 0–15 seconds
"Traditional intrusion detection waits for an attack to complete before triggering an alert. We need to forecast attacks before they escalate."

### 15–35 seconds
"Our solution is a Temporal World Model. It ingests 5-second network windows and learns short-term network-state transitions, allowing us to simulate future states."

### 35–55 seconds
"Here in the dashboard, we load a telemetry sequence."

### 55–80 seconds
"The engine calculates a current risk and performs an autoregressive rollout to forecast risk at 5, 10, and 15 seconds into the future."

### 80–100 seconds
"We use the predicted future state to derive an approximate ATT&CK-aligned stage—moving from Reconnaissance to Discovery."

### 100–112 seconds
"The model provides transparency by showing exactly which network features and historical time steps drove the risk prediction."

### 112–120 seconds
"The World Model achieved a PR-AUC of 0.5020 compared to the 0.2517 baseline, working entirely offline. Note that this uses flow-level telemetry and derived stage mappings."
