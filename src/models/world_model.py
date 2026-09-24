import torch.nn as nn
class TemporalWorldModel(nn.Module):
    def __init__(self, features=30):
        super(TemporalWorldModel, self).__init__()
        self.lstm = nn.LSTM(features, 64, 1, batch_first=True)
        self.state_decoder = nn.Linear(64, features)
        self.risk_head = nn.Linear(64, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        Z_t = out[:, -1, :] 
        return self.state_decoder(Z_t), self.risk_head(Z_t)
