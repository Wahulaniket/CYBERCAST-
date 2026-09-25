import os
import pandas as pd
from typing import Dict, Any, Tuple
from src.world_model_v2.inference import InferenceEngine, PredictionResult

MODEL_PATH = r"d:\working_projects\SIH\cyberCast2\models\world_model_packet_v2.pt"
SCALER_PATH = r"d:\working_projects\SIH\cyberCast2\models\scaler_packet_v2.pkl"
DEMO_PATH = r"d:\working_projects\SIH\cyberCast2\data\processed\global_states_v2\friday_global.parquet"

class InferenceService:
    def __init__(self):
        self.engine = None
        self.model_loaded = False
        self.scaler_loaded = False
        self.schema_loaded = False
        self.device = "unknown"
        
    def load(self, device="auto"):
        try:
            self.engine = InferenceEngine(MODEL_PATH, SCALER_PATH, device=None if device=="auto" else device)
            self.model_loaded = True
            self.scaler_loaded = True
            
            # Check schema
            schema_path = MODEL_PATH.replace("world_model_packet_v2.pt", "feature_schema_packet_v2.json")
            if os.path.exists(schema_path):
                self.schema_loaded = True
                
            self.device = str(self.engine.device)
            return True
        except Exception as e:
            print(f"Failed to load engine: {e}")
            return False

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "operational" if self.engine else "error",
            "offline": True,
            "model_loaded": self.model_loaded,
            "scaler_loaded": self.scaler_loaded,
            "schema_loaded": self.schema_loaded,
            "device": self.device
        }

    def get_model_info(self) -> Dict[str, Any]:
        if not self.engine:
            return {}
            
        return {
            "model_version": "World Model v2",
            "input_feature_count": self.engine.input_size,
            "hidden_size": 64,
            "sequence_length": 10,
            "window_duration": "5 sec",
            "supported_rollout_k_values": [1, 3, 5, 10],
            "explainability_method": "Gradient-based",
            "supported_stages": ["RECONNAISSANCE", "COMMAND_AND_CONTROL", "DISCOVERY", "INITIAL_ACCESS"]
        }

    def get_demo_data(self) -> pd.DataFrame:
        if not os.path.exists(DEMO_PATH):
            raise FileNotFoundError("Demo dataset not found.")
        # Return a small subset for speed as in original app.py
        return pd.read_parquet(DEMO_PATH).head(300)

    def analyze(self, df: pd.DataFrame, k: int) -> PredictionResult:
        if not self.engine:
            raise RuntimeError("Inference engine not loaded.")
        return self.engine.predict_attack_progression(df, k=k)

inference_service = InferenceService()
