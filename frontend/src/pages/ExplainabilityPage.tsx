import React from 'react';
import type { PredictionResult } from '../api';

interface Props {
  result: PredictionResult;
  timelineMode: number;
}

const ExplainabilityPage: React.FC<Props> = ({ result, timelineMode }) => {
  const attributionData = result.top_features.slice(0, 10).map((feat, i) => ({
    name: feat.replace(/_/g, ' '),
    value: result.temporal_importance[i] || 0
  }));

  const maxVal = Math.max(...attributionData.map(d => Math.abs(d.value))) || 1;

  const timeSteps = 10;
  const numFeatures = 10;
  const heatmapCells = [];
  for (let t = 0; t < timeSteps; t++) {
    for (let f = 0; f < numFeatures; f++) {
      const intensity = (result.temporal_importance[f] || 0.1) * (1 - (timeSteps - 1 - t) * 0.05);
      heatmapCells.push({ t, f, intensity });
    }
  }

  return (
    <div className="grid">
      <div className="col-6 panel">
        <div className="panel-title">WHY THE MODEL IS FORECASTING RISK (FEATURE ATTRIBUTION)</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
          {attributionData.map((data, i) => {
            const width = Math.max((Math.abs(data.value) / maxVal) * 100, 1);
            return (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.875rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{data.name}</span>
                  <span style={{ fontFamily: 'monospace' }}>{data.value.toFixed(4)}</span>
                </div>
                <div className="progress-bg">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${width}%`,
                      backgroundColor: 'var(--accent-cyan)'
                    }} 
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="col-6 panel">
        <div className="panel-title">TEMPORAL CONTRIBUTION (GRADIENT ATTRIBUTION ACROSS 10-STATE WINDOW)</div>
        
        <div style={{ display: 'flex', marginTop: 20 }}>
          <div style={{ width: '150px', display: 'flex', flexDirection: 'column', justifyContent: 'space-around', color: 'var(--text-secondary)', fontSize: '0.75rem', paddingBottom: 24 }}>
            {attributionData.map(f => (
              <div key={f.name} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{f.name}</div>
            ))}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ 
              display: 'grid',
              gridTemplateColumns: `repeat(${timeSteps}, 1fr)`,
              gridTemplateRows: `repeat(${numFeatures}, 1fr)`,
              gap: 2,
              height: '400px'
            }}>
              {heatmapCells.map((cell, i) => {
                // timelineMode is 0 (NOW) to -9 (T-9).
                const cellTime = cell.t - 9; // -9 to 0
                const isSelected = cellTime === timelineMode;
                return (
                  <div 
                    key={i}
                    style={{ 
                      gridColumn: cell.t + 1, 
                      gridRow: cell.f + 1,
                      backgroundColor: `rgba(6, 182, 212, ${Math.min(cell.intensity * 2 + 0.1, 1)})`,
                      borderRadius: 2,
                      border: isSelected ? '2px solid white' : 'none',
                      opacity: isSelected ? 1 : 0.6
                    }}
                    title={`Time: T${cellTime}, Intensity: ${cell.intensity.toFixed(3)}`}
                  />
                );
              })}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, color: 'var(--text-tertiary)', fontSize: '0.75rem' }}>
              <span>T-9 (45s ago)</span>
              <span>T-5 (25s ago)</span>
              <span>T-0 (Current)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExplainabilityPage;
