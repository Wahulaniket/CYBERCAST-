import torch
def explain(model, seq):
    model.train() # allow gradients
    seq.requires_grad_(True)
    _, risk = model(seq)
    risk.backward()
    model.eval()
    grads = seq.grad[0].cpu().detach().numpy()
    seq.requires_grad_(False)
    
    temp_imp = [float(v) for v in abs(grads).sum(axis=1)]
    # top 5 features overall
    total_feat_imp = abs(grads).sum(axis=0)
    top_idxs = total_feat_imp.argsort()[-5:][::-1]
    top_features = [{"feature": f"Feature_{idx}", "time_offset": 0, "input_value": float(seq[0, -1, idx]), "attribution": float(total_feat_imp[idx]), "direction": "increases_risk" if grads[-1, idx] > 0 else "decreases_risk"} for idx in top_idxs]
    return top_features, temp_imp
