import os, pytest
from src.inference.engine import predict_attack_progression
BASE_DIR = "d:/working_projects/SIH/cyberCast2"

def test_inference_e2e():
    res = predict_attack_progression(os.path.join(BASE_DIR, "tests/data/sample_flow.csv"))
    assert res["status"] == "SUCCESS"
    assert "current_risk" in res
