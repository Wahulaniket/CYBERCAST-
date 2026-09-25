import React from 'react';
import type { HealthResponse, PredictionResult } from '../api';

interface Props {
  health: HealthResponse;
  result: PredictionResult | null;
}

const SystemHealthPage: React.FC<Props> = ({ health, result }) => {
  const latency = result?.model_metadata?.inference_latency_seconds 
    ? (result.model_metadata.inference_latency_seconds * 1000).toFixed(1) 
    : 'N/A';
  
  const vram = result?.model_metadata?.gpu_vram_peak_mb
    ? result.model_metadata.gpu_vram_peak_mb.toFixed(1)
    : 'N/A';

  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">SYSTEM HEALTH & PERFORMANCE (MEASURED VALIDATION RESULTS)</div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginTop: 16 }}>
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Inference Engine</div>
            <div className={`kpi-value ${health.status === 'operational' ? 'text-healthy' : 'text-critical'}`} style={{ marginTop: 8, fontSize: '1.2rem' }}>
              {health.status === 'operational' ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>
          
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Model Checkpoint</div>
            <div className={`kpi-value ${health.model_loaded ? 'text-healthy' : 'text-critical'}`} style={{ marginTop: 8, fontSize: '1.2rem' }}>
              {health.model_loaded ? 'VALID' : 'MISSING'}
            </div>
          </div>
          
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Scaler</div>
            <div className={`kpi-value ${health.scaler_loaded ? 'text-healthy' : 'text-critical'}`} style={{ marginTop: 8, fontSize: '1.2rem' }}>
              {health.scaler_loaded ? 'VALID' : 'MISSING'}
            </div>
          </div>

          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Feature Schema</div>
            <div className="kpi-value text-info" style={{ marginTop: 8, fontSize: '1.2rem' }}>
              {health.schema_loaded ? '55 FEATURES' : 'DEFAULT SCHEMA'}
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginTop: 20 }}>
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>CPU Inference</div>
            <div className="kpi-value text-primary" style={{ marginTop: 8, fontSize: '1.2rem' }}>~7 ms</div>
          </div>
          
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>GPU Model</div>
            <div className="kpi-value text-primary" style={{ marginTop: 8, fontSize: '1.2rem' }}>~0.7 ms</div>
          </div>
          
          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>GPU End-to-End</div>
            <div className="kpi-value text-primary" style={{ marginTop: 8, fontSize: '1.2rem' }}>~12 ms</div>
          </div>

          <div style={{ backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Peak GPU VRAM</div>
            <div className="kpi-value text-primary" style={{ marginTop: 8, fontSize: '1.2rem' }}>~26 MB</div>
          </div>
        </div>
        
        <div style={{ marginTop: 24, fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
          * Hardware utilization and latency metrics are measured validation results from Phase 9F. Last measured live latency: {latency} ms (VRAM: {vram} MB).
        </div>
      </div>
    </div>
  );
};

export default SystemHealthPage;
