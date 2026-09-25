from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    data: List[Dict[str, Any]]
    device: str = "auto"
    k: int = 3

class HealthResponse(BaseModel):
    status: str
    offline: bool
    model_loaded: bool
    scaler_loaded: bool
    schema_loaded: bool
    device: str

class ModelInfoResponse(BaseModel):
    model_version: str
    input_feature_count: int
    hidden_size: int
    sequence_length: int
    window_duration: str
    supported_rollout_k_values: List[int]
    explainability_method: str
    supported_stages: List[str]

class PredictionResponse(BaseModel):
    current_risk: float
    risk_forecast: Dict[str, float]
    predicted_states: List[List[float]]
    predicted_stage: str
    stage_confidence: float
    top_features: List[str]
    temporal_importance: List[float]
    input_quality: Dict[str, Any]
    model_metadata: Dict[str, Any]
    network_graph: Optional[Dict[str, Any]] = None
    telemetry: Optional[List[Dict[str, Any]]] = None
