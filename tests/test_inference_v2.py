import pytest
import os
import pandas as pd
import numpy as np
import torch
from src.world_model_v2.inference import InferenceEngine

@pytest.fixture
def test_data():
    data_path = r"D:\working_projects\SIH\cyberCast2\data\processed\global_states_v2\friday_global.parquet"
    if os.path.exists(data_path):
        return pd.read_parquet(data_path).head(100)
    else:
        pytest.skip("Test data not found")

@pytest.fixture
def engine():
    model_path = r"D:\working_projects\SIH\cyberCast2\models\world_model_packet_v2.pt"
    scaler_path = r"D:\working_projects\SIH\cyberCast2\models\scaler_packet_v2.pkl"
    return InferenceEngine(model_path, scaler_path, device='cpu')

def test_model_loading(engine):
    assert engine.model is not None
    assert engine.input_size == 55

def test_feature_validation(engine, test_data):
    X, quality = engine._validate_and_preprocess(test_data)
    assert X.shape == (10, 55)
    assert quality['feature_count'] == 55

def test_sequence_validation(engine, test_data):
    # Pass valid sequence
    result = engine.predict_attack_progression(test_data, k=1)
    assert result.input_quality['sequence_valid'] is True

    # Pass invalid sequence (break timestamp gap)
    bad_data = test_data.copy()
    bad_data.loc[bad_data.index[-1], 'window_start'] += 10.0
    with pytest.raises(ValueError, match="Invalid sequence gaps"):
        engine.predict_attack_progression(bad_data)

def test_cpu_inference(engine, test_data):
    result = engine.predict_attack_progression(test_data, k=1)
    assert 0 <= result.current_risk <= 1
    assert result.model_metadata['device'] == 'cpu'
    assert result.model_metadata['inference_latency_seconds'] > 0

def test_gpu_inference(test_data):
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    model_path = r"D:\working_projects\SIH\cyberCast2\models\world_model_packet_v2.pt"
    scaler_path = r"D:\working_projects\SIH\cyberCast2\models\scaler_packet_v2.pkl"
    engine_gpu = InferenceEngine(model_path, scaler_path, device='cuda')
    result = engine_gpu.predict_attack_progression(test_data, k=1)
    assert result.model_metadata['device'] == 'cuda'
    assert result.model_metadata['gpu_vram_peak_mb'] >= 0

def test_rollout(engine, test_data):
    result = engine.predict_attack_progression(test_data, k=5)
    assert len(result.predicted_states) == 5
    assert len(result.risk_forecast) == 6 # current + 5 steps

def test_explainability(engine, test_data):
    result = engine.predict_attack_progression(test_data, k=1)
    assert len(result.top_features) == 10
    assert len(result.temporal_importance) == 10
    assert result.top_features[0] in engine.feature_cols

def test_attack_stage_mapping(engine, test_data):
    result = engine.predict_attack_progression(test_data, k=1)
    valid_stages = ["RECONNAISSANCE", "DISCOVERY", "INITIAL_ACCESS", "COMMAND_AND_CONTROL", "INSUFFICIENT_EVIDENCE"]
    assert result.predicted_stage in valid_stages
    assert 0 <= result.stage_confidence <= 1
