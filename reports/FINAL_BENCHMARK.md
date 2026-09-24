# Final Benchmark Results

| Model               |   PR-AUC |  ROC-AUC |       F1 | Precision |   Recall |      FPR | Accuracy |
| ------------------- | -------: | -------: | -------: | --------: | -------: | -------: | -------: |
| Logistic Regression |   0.2517 |      N/A |   0.3294 |    0.2515 |   0.4771 |   0.5041 |      N/A |
| LSTM                |   0.4771 |      N/A |   0.4026 |    0.4718 |   0.3511 |   0.1396 |      N/A |
| LSTM World Model    |   0.5020 |      N/A |      N/A |       N/A |      N/A |      N/A |      N/A |

### World Model Validation Table
| Validation                      | Result |
| ------------------------------- | ------ |
| State transition learning       | PASS   |
| Persistence baseline comparison | PASS   |
| Autoregressive rollout          | PASS   |
| Teacher forcing leakage         | NONE   |
| Risk prediction                 | PASS   |
| Explainability                  | PASS   |
| ATT&CK-aligned mapping          | PASS   |
| CPU inference                   | PASS   |
| GPU inference                   | PASS   |
| Offline execution               | PASS   |
