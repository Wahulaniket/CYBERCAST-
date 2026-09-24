import pytest
import sys
import os

# To test the dashboard logic indirectly, we can test app imports and some functions
def test_app_imports():
    try:
        import app
        assert True
    except Exception as e:
        pytest.fail(f"App import failed: {str(e)}")

def test_inference_reused():
    # Make sure we didn't duplicate the logic inside app.py by reading the file
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "from src.world_model_v2.inference import InferenceEngine" in content
    assert "class WorldModelV2" not in content # Logic should not be duplicated
    assert "nn.LSTM" not in content

def test_dashboard_offline_mode():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "requests.get" not in content
    assert "http://" not in content
    assert "https://" not in content
