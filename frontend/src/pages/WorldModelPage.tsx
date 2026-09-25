import React from 'react';
import type { PredictionResult } from '../api';

interface Props {
  result: PredictionResult;
  kSteps: number;
}

const WorldModelPage: React.FC<Props> = () => {
  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">LSTM WORLD MODEL v2 ARCHITECTURE</div>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '40px 0' }}>
          
          <div className="arch-box">NETWORK TELEMETRY</div>
          <div className="arch-arrow">↓</div>
          <div className="arch-box">FLOW + PACKET FEATURES</div>
          <div className="arch-arrow">↓</div>
          <div className="arch-box">5-SECOND NETWORK STATE</div>
          <div className="arch-arrow">↓</div>
          <div className="arch-box">55-DIMENSION STATE VECTOR</div>
          <div className="arch-arrow">↓</div>
          <div className="arch-box">10-STEP TEMPORAL CONTEXT</div>
          <div className="arch-arrow">↓</div>
          
          <div className="arch-box highlight" style={{ width: '400px', margin: '16px 0' }}>
            <h3 style={{ color: 'var(--accent-cyan)' }}>LSTM WORLD MODEL v2</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '8px' }}>Hidden Size: 64</p>
          </div>
          
          <div style={{ display: 'flex', gap: '64px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="arch-arrow">↓</div>
              <div className="arch-box">STATE TRANSITION DECODER</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="arch-arrow">↓</div>
              <div className="arch-box">FUTURE RISK HEAD</div>
            </div>
          </div>
          
          <div className="arch-arrow" style={{ marginTop: 24 }}>↓</div>
          <div className="arch-box" style={{ width: '300px' }}>K-STEP AUTOREGRESSIVE ROLLOUT</div>
          <div className="arch-arrow">↓</div>
          <div className="arch-box highlight text-critical">THREAT FORECAST</div>
          
        </div>
      </div>

      <div className="col-12 panel">
        <div className="panel-title">AUTOREGRESSIVE ROLLOUT EVALUATION (RMSE)</div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
          Scaled-state rollout RMSE. These are not probabilities, but state vector reconstruction errors across the rollout horizon.
        </p>
        <div style={{ display: 'flex', gap: '24px' }}>
          <div style={{ flex: 1, backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)' }}>K=1</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: 8 }}>0.7737</div>
          </div>
          <div style={{ flex: 1, backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)' }}>K=3</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: 8 }}>0.8044</div>
          </div>
          <div style={{ flex: 1, backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)' }}>K=5</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: 8 }}>0.8194</div>
          </div>
          <div style={{ flex: 1, backgroundColor: 'var(--bg-app)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ color: 'var(--text-secondary)' }}>K=10</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: 8 }}>0.8438</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldModelPage;
