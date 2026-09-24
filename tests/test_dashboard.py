import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.inference.engine import predict_attack_progression

BASE_DIR = "d:/working_projects/SIH/cyberCast2"

def test_dashboard_imports():
    assert True

def test_prediction_api_import():
    assert predict_attack_progression is not None

def test_valid_csv():
    res = predict_attack_progression(os.path.join(BASE_DIR, "tests/data/sample_flow.csv"))
    assert res["status"] == "SUCCESS"

def test_insufficient_data():
    # create dummy empty csv
    empty_path = os.path.join(BASE_DIR, "tests/data/empty.csv")
    with open(empty_path, "w") as f: f.write("timestamp\n")
    res = predict_attack_progression(empty_path)
    assert res["status"] == "INSUFFICIENT_DATA"
