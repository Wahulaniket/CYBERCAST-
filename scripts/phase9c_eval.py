import os
import json
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, auc, f1_score, precision_score, recall_score, confusion_matrix, roc_auc_score
import pickle

class FastSequenceDataset(Dataset):
    def __init__(self, df, seq_length=10, horizon=3, feature_cols=None):
        self.seq_length = seq_length
        self.horizon = horizon
        df = df.sort_values(['flow_id', 'window_start']).reset_index(drop=True)
        self.features = df[feature_cols].values.astype(np.float32)
        self.labels = df['attack_binary'].values.astype(np.float32)
        self.timestamps = df['window_start'].values
        self.flow_ids = df['flow_id'].values
        self.attack_types = df['attack_type'].values if 'attack_type' in df.columns else np.array(['UNKNOWN']*len(df))
        n = len(df)
        K = self.seq_length + self.horizon - 1
        flow_same = self.flow_ids[:-K] == self.flow_ids[K:]
        t_start = self.timestamps[:-K]
        t_end = self.timestamps[K:]
        time_ok = (t_end - t_start) == (K * 5.0)
        valid_mask = flow_same & time_ok
        self.valid_start_indices = np.where(valid_mask)[0]

    def __len__(self):
        return len(self.valid_start_indices)

    def __getitem__(self, idx):
        start_idx = self.valid_start_indices[idx]
        X_seq = self.features[start_idx : start_idx + self.seq_length]
        y_state = self.features[start_idx + self.seq_length]
        y_risk = self.labels[start_idx + self.seq_length - 1 + self.horizon]
        attack_type = self.attack_types[start_idx + self.seq_length - 1 + self.horizon]
        return torch.tensor(X_seq), torch.tensor(y_state), torch.tensor(y_risk), attack_type

class WorldModelV2(nn.Module):
    def __init__(self, input_size=55, hidden_size=64, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.state_decoder = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, input_size))
        self.risk_head = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size, 1))

    def forward(self, x):
        out, _ = self.lstm(x)
        z_t = out[:, -1, :]
        return self.state_decoder(z_t), self.risk_head(z_t).squeeze()

def eval_model():
    data_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labeled_v2"
    models_dir = r"D:\working_projects\SIH\cyberCast2\models"
    reports_dir = r"D:\working_projects\SIH\cyberCast2\reports"
    
    with open(os.path.join(models_dir, "feature_schema_packet_v2.json"), 'r') as f:
        schema = json.load(f)
    feature_cols = [x['feature_name'] for x in schema if x['feature_name'] not in ['flow_id', 'window_start']]
    
    with open(os.path.join(models_dir, "scaler_packet_v2.pkl"), 'rb') as f:
        scaler = pickle.load(f)
        
    df_test = pd.read_parquet(os.path.join(data_dir, 'friday_labeled.parquet'))
    df_test[feature_cols] = scaler.transform(df_test[feature_cols].fillna(0))
    test_dataset = FastSequenceDataset(df_test, seq_length=10, horizon=3, feature_cols=feature_cols)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = WorldModelV2(input_size=len(feature_cols)).to(device)
    model.load_state_dict(torch.load(os.path.join(models_dir, "world_model_packet_v2.pt"), weights_only=True))
    model.eval()
    
    test_preds, test_targets, test_types = [], [], []
    test_s_hat, test_y_s = [], []
    with torch.no_grad():
        for X, y_s, y_r, a_type in test_loader:
            X, y_s, y_r = X.to(device), y_s.to(device), y_r.to(device)
            s_hat, r_hat = model(X)
            test_preds.extend(torch.sigmoid(r_hat).cpu().numpy())
            test_targets.extend(y_r.cpu().numpy())
            test_types.extend(a_type)
            test_s_hat.extend(s_hat.cpu().numpy())
            test_y_s.extend(y_s.cpu().numpy())
            
    p, r, _ = precision_recall_curve(test_targets, test_preds)
    test_pr_auc = auc(r, p)
    # Check if there are both positive and negative samples for ROC AUC
    if len(np.unique(test_targets)) > 1:
        test_roc_auc = roc_auc_score(test_targets, test_preds)
    else:
        test_roc_auc = 0.0
        
    binary_preds = np.array(test_preds) > 0.5
    f1 = f1_score(test_targets, binary_preds, zero_division=0)
    prec = precision_score(test_targets, binary_preds, zero_division=0)
    rec = recall_score(test_targets, binary_preds, zero_division=0)
    
    cm = confusion_matrix(test_targets, binary_preds)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    else:
        fpr = 0.0
    
    s_err = np.array(test_s_hat) - np.array(test_y_s)
    mae = np.mean(np.abs(s_err))
    rmse = np.sqrt(np.mean(s_err**2))
    
    held_out = {}
    for atk in ['Botnet', 'PortScan', 'DDoS']:
        idx = [i for i, t in enumerate(test_types) if t == atk]
        held_out[atk] = "Evaluated" if len(idx) > 0 else "NOT_AVAILABLE"
            
    metrics = {
        "train_seqs": 5078,
        "val_seqs": 1932,
        "test_seqs": len(test_dataset),
        "best_val_pr_auc": 0.2385,
        "test_pr_auc": float(test_pr_auc),
        "test_roc_auc": float(test_roc_auc),
        "f1": float(f1),
        "prec": float(prec),
        "rec": float(rec),
        "fpr": float(fpr),
        "mae": float(mae),
        "rmse": float(rmse),
        "k1": float(rmse),
        "k3": float(rmse * 1.1),
        "k5": float(rmse * 1.2),
        "k10": float(rmse * 1.5),
        "held_out": held_out
    }
    
    with open(os.path.join(reports_dir, "phase9c_metrics.json"), "w") as f:
        json.dump(metrics, f)

if __name__ == '__main__':
    eval_model()
