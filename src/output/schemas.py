from typing import TypedDict, List, Dict, Any

class PredictionResult(TypedDict):
    status: str
    timestamp: str
    current_risk: float
    risk_forecast: Dict[str, float]
    risk_trend: str
    alert_level: str
    current_stage: str
    predicted_stage: str
    stage_confidence: float
    mapping_type: str
    predicted_states: List[List[float]]
    top_features: List[Dict[str, Any]]
    temporal_importance: List[float]
    explanation: str
    model: Dict[str, Any]
