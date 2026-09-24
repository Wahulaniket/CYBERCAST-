import torch, os, json, pickle, yaml
from src.models.world_model import TemporalWorldModel

def load_system(base_dir):
    with open(os.path.join(base_dir, "configs/inference.yaml")) as f: config = yaml.safe_load(f)
    with open(os.path.join(base_dir, "models/feature_schema.json")) as f: schema = json.load(f)
    with open(os.path.join(base_dir, "models/scaler.pkl"), "rb") as f: scaler = pickle.load(f)
    
    device = torch.device("cuda" if torch.cuda.is_available() and config["device"] in ["auto", "cuda"] else "cpu")
    model = TemporalWorldModel(features=config["state_dimension"]).to(device)
    model.load_state_dict(torch.load(os.path.join(base_dir, "models/world_model.pt"), map_location=device, weights_only=True))
    model.eval()
    return model, scaler, schema, config, device
