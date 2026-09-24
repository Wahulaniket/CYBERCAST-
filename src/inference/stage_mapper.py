import os, yaml
def map_stage(risk, base_dir):
    with open(os.path.join(base_dir, "configs/stage_mapping.yaml")) as f: cfg = yaml.safe_load(f)
    if risk < cfg["RECONNAISSANCE"]["threshold"]: return "BENIGN", 0.95, "HIGH"
    elif risk < cfg["DISCOVERY"]["threshold"]: return "RECONNAISSANCE", 0.7, "APPROXIMATE"
    elif risk < cfg["INITIAL_ACCESS"]["threshold"]: return "DISCOVERY", 0.6, "APPROXIMATE"
    elif risk < cfg["COMMAND_AND_CONTROL"]["threshold"]: return "INITIAL_ACCESS", 0.6, "APPROXIMATE"
    else: return "COMMAND_AND_CONTROL", 0.5, "APPROXIMATE"
