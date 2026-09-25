import React from 'react';

const ModelPerformancePage: React.FC = () => {
  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">MODEL EVALUATION METRICS (HELD-OUT FRIDAY TEST EVALUATION)</div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px', marginTop: 16 }}>
          <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
            <div style={{ padding: 12, backgroundColor: 'rgba(6, 182, 212, 0.1)', color: 'var(--accent-cyan)', fontWeight: 600, borderBottom: '1px solid var(--border-subtle)' }}>
              World Model v2
            </div>
            <div style={{ padding: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div><span style={{ color: 'var(--text-secondary)' }}>PR-AUC:</span> <strong style={{ color: 'var(--text-primary)' }}>0.6873</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>ROC-AUC:</span> <strong style={{ color: 'var(--text-primary)' }}>0.7475</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>F1 Score:</span> <strong style={{ color: 'var(--text-primary)' }}>0.3181</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Precision:</span> <strong style={{ color: 'var(--text-primary)' }}>0.9261</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Recall:</span> <strong style={{ color: 'var(--text-primary)' }}>0.1920</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>FPR:</span> <strong style={{ color: 'var(--text-primary)' }}>0.0092</strong></div>
            </div>
          </div>
          
          <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
            <div style={{ padding: 12, backgroundColor: 'rgba(148, 163, 184, 0.1)', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-subtle)' }}>
              Logistic Regression Baseline
            </div>
            <div style={{ padding: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div><span style={{ color: 'var(--text-secondary)' }}>PR-AUC:</span> <strong style={{ color: 'var(--text-primary)' }}>0.5857</strong></div>
              <div><span style={{ color: 'var(--text-secondary)' }}>F1 Score:</span> <strong style={{ color: 'var(--text-primary)' }}>0.2569</strong></div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '24px', marginTop: 24 }}>
          <div style={{ flex: 1, padding: 16, backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--status-healthy)', borderRadius: 8 }}>
            <div style={{ color: 'var(--status-healthy)', fontSize: '0.875rem' }}>PR-AUC Δ</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--status-healthy)' }}>+0.1015</div>
          </div>
          <div style={{ flex: 1, padding: 16, backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--status-healthy)', borderRadius: 8 }}>
            <div style={{ color: 'var(--status-healthy)', fontSize: '0.875rem' }}>F1 Δ</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--status-healthy)' }}>+0.0612</div>
          </div>
        </div>
      </div>
      
      <div className="col-12 panel">
        <div className="panel-title">ATTACK CATEGORY PERFORMANCE (HELD-OUT ATTACK CATEGORIES)</div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
          Performance varies significantly by attack category. Do not assume universal unseen attack detection.
        </p>
        
        <div style={{ display: 'flex', gap: '24px' }}>
          <div style={{ flex: 1, padding: 16, backgroundColor: 'var(--bg-app)', border: '1px solid var(--accent-cyan)', borderRadius: 8 }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>DDoS F1</div>
            <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>0.9054</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 8 }}>Strong detection</div>
          </div>
          
          <div style={{ flex: 1, padding: 16, backgroundColor: 'var(--bg-app)', border: '1px solid var(--status-warning)', borderRadius: 8 }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Botnet F1</div>
            <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--status-warning)' }}>0.1814</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 8 }}>Weak detection</div>
          </div>
          
          <div style={{ flex: 1, padding: 16, backgroundColor: 'var(--bg-app)', border: '1px solid var(--status-warning)', borderRadius: 8 }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>PortScan F1</div>
            <div style={{ fontSize: '2rem', fontWeight: 600, color: 'var(--status-warning)' }}>0.1602</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 8 }}>Weak detection</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelPerformancePage;
