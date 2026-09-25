export interface HealthResponse {
  status: string;
  offline?: boolean;
  model_loaded?: boolean;
  scaler_loaded?: boolean;
  schema_loaded?: boolean;
  device?: string;
}

export interface PredictionResult {
  current_risk: number;
  risk_forecast: Record<string, number>;
  predicted_states: number[][];
  predicted_stage: string;
  stage_confidence: number;
  top_features: string[];
  temporal_importance: number[];
  input_quality: {
    valid_windows: number;
    imputed_windows: number;
  };
  model_metadata: {
    inference_latency_seconds?: number;
    gpu_vram_peak_mb?: number;
  };
  network_graph?: {
    nodes: any[];
    edges: any[];
  };
  telemetry?: any[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
console.log("[CyberCast] API Base URL:", API_BASE_URL);

export async function fetchHealth(): Promise<HealthResponse> {
  console.log("[CyberCast] GET /api/health");
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    const data = await res.json();
    console.log("[CyberCast] Health response:", data);
    if (!res.ok) throw new Error('API Offline');
    return data;
  } catch (e) {
    console.error("[CyberCast] Backend connection failed:", e);
    return { status: 'offline', offline: true };
  }
}

export async function fetchDemoData(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/demo`);
    if (!res.ok) throw new Error('Demo data unavailable');
    const data = await res.json();
    return Array.isArray(data) ? data : data.data || [];
  } catch (e) {
    console.error(e);
    return [];
  }
}

export async function runAnalysis(data: any[], k: number = 3): Promise<PredictionResult> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, k }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Analysis failed');
    }
    return res.json();
  } catch (e: any) {
    console.error(e);
    throw new Error(e.message || 'Analysis failed');
  }
}
