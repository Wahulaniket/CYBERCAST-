import torch
def autoregressive_rollout(model, seq, k):
    states, risks = [], []
    curr = seq.clone()
    with torch.no_grad():
        for _ in range(k):
            s_next, r_next = model(curr)
            states.append(s_next)
            risks.append(torch.sigmoid(r_next))
            curr = torch.cat([curr[:, 1:, :], s_next.unsqueeze(1)], dim=1)
    return states, risks
