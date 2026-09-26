import { useState, useEffect, useRef } from 'react';
import type { PredictionResult } from '../api';

export function useLiveCapture() {
  const [liveStatus, setLiveStatus] = useState<any>({ status: 'STOPPED' });
  const [liveResult, setLiveResult] = useState<PredictionResult | null>(null);
  const [wsError, setWsError] = useState<string | null>(null);
  const [telemetryHistory, setTelemetryHistory] = useState<any[]>([]);
  const [buildingContextData, setBuildingContextData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/live/status');
      const data = await res.json();
      setLiveStatus(data);
    } catch (e) {
      console.error("Failed to fetch live status");
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const connectWs = () => {
    if (wsRef.current) return;
    const ws = new WebSocket('ws://localhost:8000/ws/live');
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'live_prediction') {
          // Wrap into PredictionResult format
          setBuildingContextData(null);
          
          let nextTelemetry: any[] = [];
          setTelemetryHistory(prev => {
            const updated = [...prev, msg.network_evidence];
            if (updated.length > 20) updated.shift();
            nextTelemetry = updated;
            return updated;
          });

          setLiveResult({
            current_risk: msg.future_risk,
            risk_forecast: msg.risk_forecast || {},
            predicted_states: msg.predicted_states || [],
            predicted_stage: msg.stage,
            stage_confidence: msg.future_risk + 0.1, // mock
            top_features: msg.top_features || [],
            temporal_importance: msg.temporal_importance || [],
            input_quality: { valid_windows: 10, imputed_windows: 0 },
            model_metadata: {
              inference_latency_seconds: 0.1,
              gpu_vram_peak_mb: 0
            },
            network_graph: { nodes: [], edges: [] },
            telemetry: nextTelemetry // Using telemetryHistory from updated state
          });
        } else if (msg.type === 'building_context') {
            setBuildingContextData(msg);
        } else if (msg.type === 'error') {
            setWsError(msg.message);
        }
      } catch (e) {
        console.error("WS parse error", e);
      }
    };
    ws.onerror = () => setWsError("WebSocket connection error");
    ws.onclose = () => {
      wsRef.current = null;
      setTimeout(connectWs, 3000); // Reconnect
    };
    wsRef.current = ws;
  };

  useEffect(() => {
    connectWs();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const startCapture = async (interfaceName: string) => {
    try {
      setWsError(null);
      await fetch('http://localhost:8000/api/live/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interface: interfaceName })
      });
      fetchStatus();
    } catch (e: any) {
      setWsError(e.message);
    }
  };

  const stopCapture = async () => {
    try {
      await fetch('http://localhost:8000/api/live/stop', { method: 'POST' });
      fetchStatus();
    } catch (e) {
      console.error(e);
    }
  };

  return { liveStatus, liveResult, buildingContextData, wsError, startCapture, stopCapture, telemetryHistory };
}
