import { useState, useEffect, useRef } from 'react';
import { 
  Activity, BarChart3, Network, LineChart, 
  AlertTriangle, Server, HardDrive, List, Play, Pause, RotateCcw
} from 'lucide-react';
import { fetchHealth, fetchDemoData, runAnalysis } from './api';
import type { HealthResponse, PredictionResult } from './api';
import OverviewPage from './pages/OverviewPage';
import WorldModelPage from './pages/WorldModelPage';
import SystemHealthPage from './pages/SystemHealthPage';
import ModelPerformancePage from './pages/ModelPerformancePage';
import ThreatTimelinePage from './pages/ThreatTimelinePage';
import ExplainabilityPage from './pages/ExplainabilityPage';
import NetworkEvidencePage from './pages/NetworkEvidencePage';

function App() {
  const [activeTab, setActiveTab] = useState('OVERVIEW');
  const [kSteps, setKSteps] = useState<number>(3);
  const [device, setDevice] = useState<'cpu' | 'gpu' | 'auto'>('auto');
  
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(true);
  const [demoData, setDemoData] = useState<any[] | null>(null);
  
  // Playback State
  const [playbackIndex, setPlaybackIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [timelineMode, setTimelineMode] = useState<number>(0); // 0 = NOW, -1 = T-1, etc.
  
  // Inference State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [inferenceCache, setInferenceCache] = useState<Record<string, PredictionResult>>({});

  const timerRef = useRef<number | null>(null);

  // Initial Load
  const checkHealth = () => {
    setIsCheckingHealth(true);
    fetchHealth().then(res => {
      setHealth(res);
      setIsCheckingHealth(false);
    }).catch(() => {
      setHealth({ status: 'offline', offline: true });
      setIsCheckingHealth(false);
    });
  };

  useEffect(() => {
    checkHealth();
    fetchDemoData().then(data => {
      if (data && data.length > 0) {
        setDemoData(data);
        
        // Find the first valid contiguous 10-step sequence (5s gaps)
        let foundIdx = -1;
        for (let i = 9; i < data.length; i++) {
          let isValid = true;
          for (let j = i - 9; j < i; j++) {
            const diff = data[j+1].window_start - data[j].window_start;
            if (Math.abs(diff - 5) > 0.1) {
              isValid = false;
              break;
            }
          }
          if (isValid) {
            foundIdx = i;
            break;
          }
        }
        
        setPlaybackIndex(foundIdx !== -1 ? foundIdx : Math.min(9, data.length - 1));
      } else {
        setDemoData([]);
      }
    }).catch(() => setDemoData(null));
  }, []);

  // Playback Loop
  useEffect(() => {
    if (isPlaying && demoData) {
      timerRef.current = window.setInterval(() => {
        setPlaybackIndex(prev => {
          if (prev >= demoData.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          
          // Check if next frame is contiguous
          const isContiguous = Math.abs(demoData[prev + 1].window_start - demoData[prev].window_start - 5) <= 0.1;
          
          if (isContiguous) {
            return prev + 1;
          } else {
            // Gap detected! Scan for the next valid 10-step sequence
            for (let i = prev + 10; i < demoData.length; i++) {
              let isValid = true;
              for (let j = i - 9; j < i; j++) {
                if (Math.abs(demoData[j+1].window_start - demoData[j].window_start - 5) > 0.1) {
                  isValid = false;
                  break;
                }
              }
              if (isValid) return i;
            }
            setIsPlaying(false);
            return prev; // No more valid sequences
          }
        });
      }, 1000 / playbackSpeed);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, playbackSpeed, demoData]);

  // Run Inference when playback index or K changes
  useEffect(() => {
    if (!demoData || demoData.length === 0) return;
    
    // Always use the latest 10 windows up to playbackIndex
    const startIdx = Math.max(0, playbackIndex - 9);
    const windowData = demoData.slice(startIdx, playbackIndex + 1);
    
    if (windowData.length === 0) return;

    const cacheKey = `${playbackIndex}_${kSteps}`;
    if (inferenceCache[cacheKey]) {
      setResult(inferenceCache[cacheKey]);
      setLoading(false);
      setError(null);
      return;
    }

    let isMounted = true;
    
    const triggerInference = async () => {
      if (!isPlaying) setLoading(true); // Don't show loading spinner constantly during fast playback
      try {
        const res = await runAnalysis(windowData, kSteps);
        if (isMounted) {
          setResult(res);
          setInferenceCache(prev => ({ ...prev, [cacheKey]: res }));
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Unable to connect to CyberCast inference service.');
          setIsPlaying(false); // Stop on error
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    triggerInference();
    
    return () => { isMounted = false; };
  }, [playbackIndex, kSteps, demoData, isPlaying]);

  const navItems = [
    { id: 'OVERVIEW', label: 'Overview', icon: <BarChart3 size={16} /> },
    { id: 'THREAT_TIMELINE', label: 'Threat Timeline', icon: <Activity size={16} /> },
    { id: 'EXPLAINABILITY', label: 'Explainability', icon: <List size={16} /> },
    { id: 'NETWORK_EVIDENCE', label: 'Network Evidence', icon: <HardDrive size={16} /> },
    { id: 'WORLD_MODEL', label: 'World Model', icon: <Network size={16} /> },
    { id: 'MODEL_PERFORMANCE', label: 'Model Performance', icon: <LineChart size={16} /> },
    { id: 'SYSTEM_HEALTH', label: 'System Health', icon: <Server size={16} /> },
  ];

  // Derive dynamic KPIs
  const isHighRisk = result ? result.current_risk > 0.5 : false;
  const isElevated = result ? result.current_risk > 0.3 : false;
  const riskColorClass = isHighRisk ? 'text-critical' : isElevated ? 'text-warning' : 'text-info';
  const formatStage = (stage: string) => stage.replace(/_/g, ' ').toUpperCase();
  const currentStage = result ? formatStage(result.predicted_stage) : 'UNKNOWN';

  // Dynamic values
  const currentRiskFormatted = result ? (result.current_risk * 100).toFixed(1) : '--';
  const networkNodes = result?.network_graph?.nodes?.length || 0;
  
  return (
    <div className="app-layout">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-title">CYBERCAST</div>
          <div className="brand-subtitle">Predictive Cyber Defence</div>
        </div>
        
        <div className="sidebar-system-info">
          <div>WORLD MODEL v2</div>
          <div className="system-status">
            {isCheckingHealth ? (
              <>
                <div className="dot" style={{ color: 'var(--text-tertiary)' }}></div>
                <span style={{ color: 'var(--text-tertiary)' }}>CONNECTING</span>
              </>
            ) : (
              <>
                <div className={`dot ${!health || health.status !== 'operational' ? 'text-critical' : 'text-healthy'}`}></div>
                {!health || health.status !== 'operational' ? 'SYSTEM OFFLINE' : 'SYSTEM ONLINE'}
              </>
            )}
          </div>
        </div>
        
        <div className="sidebar-nav">
          {navItems.map(item => (
            <div 
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              {item.icon}
              {item.label}
            </div>
          ))}
        </div>
        
        <div className="sidebar-footer">
          <div>SIH 26153</div>
          <div style={{ marginTop: '4px' }}>OFFLINE AI ENGINE</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-area" style={{ position: 'relative' }}>
        <div className="topbar">
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', fontSize: '0.875rem', fontWeight: 600 }}>
            <span>CYBERCAST</span>
            <span style={{ color: 'var(--text-secondary)' }}>/</span>
            <span>WORLD MODEL v2</span>
          </div>
          <div className="topbar-badges">
            <div className="badge">OFFLINE MODE</div>
            <div className="badge badge-outline">DEMO REPLAY</div>
            <div className="badge" style={{ borderColor: 'var(--status-healthy)', color: 'var(--status-healthy)' }}>MODEL VALID</div>
          </div>
        </div>

        <div className="page-container" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="page-header" style={{ marginBottom: 16 }}>
            <div className="page-title">
              <h1>Security Operations Center</h1>
              <p>Predictive network threat monitoring and attacker progression forecasting</p>
            </div>
            
            <div className="controls-group">
              <span className="control-label">Forecast horizon</span>
              <div className="btn-group">
                {[1, 3, 5, 10].map(k => (
                  <button 
                    key={k} 
                    className={`btn-toggle ${kSteps === k ? 'active' : ''}`}
                    onClick={() => setKSteps(k)}
                  >
                    K{k}
                  </button>
                ))}
              </div>
              
              <div style={{ width: '1px', height: '20px', backgroundColor: 'var(--border-subtle)', margin: '0 8px' }}></div>
              
              <div className="btn-group">
                {['cpu', 'gpu', 'auto'].map(d => (
                  <button 
                    key={d} 
                    className={`btn-toggle ${device === d ? 'active' : ''}`}
                    onClick={() => setDevice(d as any)}
                  >
                    {d.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Dynamic KPI Header Row - Visible across all tabs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
            <div className="panel" style={{ padding: '16px' }}>
              <div className="panel-title" style={{ marginBottom: 8 }}>FUTURE THREAT RISK</div>
              <div className={`kpi-value ${riskColorClass}`}>{currentRiskFormatted}%</div>
              <div className="kpi-sub">Horizon: {kSteps} steps</div>
            </div>
            <div className="panel" style={{ padding: '16px' }}>
              <div className="panel-title" style={{ marginBottom: 8 }}>ATTACK STAGE</div>
              <div className={`kpi-value ${isHighRisk ? 'text-critical' : 'text-warning'}`} style={{ fontSize: '1.25rem', lineHeight: '1.2' }}>
                {currentStage}
              </div>
              <div className="kpi-sub">ATT&CK-aligned derived stage</div>
            </div>
            <div className="panel" style={{ padding: '16px' }}>
              <div className="panel-title" style={{ marginBottom: 8 }}>OPERATIONAL STATUS</div>
              <div className={`kpi-value ${riskColorClass}`} style={{ fontSize: '1.25rem', lineHeight: '1.2' }}>
                {result ? (result.current_risk > 0.6 ? 'CRITICAL' : result.current_risk > 0.4 ? 'HIGH' : result.current_risk > 0.2 ? 'ELEVATED' : 'LOW') : 'UNKNOWN'}
              </div>
              <div className="kpi-sub">Derived risk level</div>
            </div>
            <div className="panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column' }}>
              <div className="panel-title" style={{ marginBottom: 8 }}>TELEMETRY REPLAY</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flex: 1 }}>
                <button className="btn-toggle" onClick={() => setIsPlaying(!isPlaying)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 32, height: 32, padding: 0 }}>
                  {isPlaying ? <Pause size={14} /> : <Play size={14} />}
                </button>
                <button className="btn-toggle" onClick={() => { setPlaybackIndex(Math.min(9, (demoData?.length || 10) - 1)); setIsPlaying(false); }} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 32, height: 32, padding: 0 }}>
                  <RotateCcw size={14} />
                </button>
                <select 
                  className="btn-toggle" 
                  value={playbackSpeed} 
                  onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                  style={{ height: 32, padding: '0 8px', WebkitAppearance: 'none' }}
                >
                  <option value={0.5}>0.5x</option>
                  <option value={1}>1.0x</option>
                  <option value={2}>2.0x</option>
                  <option value={5}>5.0x</option>
                </select>
                <div style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-tertiary)', fontFamily: 'monospace' }}>
                  Idx: {playbackIndex} / {demoData ? demoData.length - 1 : 0}
                </div>
              </div>
            </div>
          </div>

          {/* Timeline Control */}
          <div className="panel" style={{ padding: '12px 16px', marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', fontWeight: 600 }}>10-STEP TEMPORAL CONTEXT</span>
            <div style={{ display: 'flex', gap: 4 }}>
              {Array.from({ length: 10 }).map((_, i) => {
                const step = i - 9; // -9 to 0
                return (
                  <button 
                    key={step} 
                    className={`btn-toggle ${timelineMode === step ? 'active' : ''}`}
                    onClick={() => setTimelineMode(step)}
                    style={{ fontSize: '0.7rem', padding: '4px 8px' }}
                  >
                    {step === 0 ? 'NOW' : `T${step}`}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Content Body */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {isCheckingHealth ? (
              <div className="state-container">
                <div className="spinner"></div>
                <div>Connecting to local backend...</div>
              </div>
            ) : !health || health.status !== 'operational' ? (
              <div className="state-container">
                <AlertTriangle size={48} color="var(--status-critical)" style={{ marginBottom: 16 }} />
                <h2 className="text-critical">BACKEND OFFLINE</h2>
                <p style={{ marginTop: 8 }}>Unable to connect to the local CyberCast inference service.</p>
                <button className="btn-primary" style={{ marginTop: 24 }} onClick={checkHealth}>
                  RETRY CONNECTION
                </button>
              </div>
            ) : error ? (
              <div className="state-container">
                <AlertTriangle size={48} color="var(--status-critical)" style={{ marginBottom: 16 }} />
                <h2 className="text-critical">VALIDATION ERROR</h2>
                <p style={{ marginTop: 8 }}>{error}</p>
                <button className="btn-primary" style={{ marginTop: 24 }} onClick={() => setIsPlaying(true)}>
                  Resume Playback
                </button>
              </div>
            ) : loading && !result ? (
              <div className="state-container">
                <div className="spinner"></div>
                <div>Running inference on sequence context...</div>
              </div>
            ) : !demoData || demoData.length === 0 ? (
              <div className="state-container">
                <HardDrive size={48} color="var(--text-tertiary)" style={{ marginBottom: 16 }} />
                <h2>No telemetry available</h2>
                <p style={{ marginTop: 8 }}>The dataset is empty or cannot be read.</p>
              </div>
            ) : result ? (
              <>
                {activeTab === 'OVERVIEW' && <OverviewPage result={result} timelineMode={timelineMode} />}
                {activeTab === 'THREAT_TIMELINE' && <ThreatTimelinePage result={result} />}
                {activeTab === 'EXPLAINABILITY' && <ExplainabilityPage result={result} timelineMode={timelineMode} />}
                {activeTab === 'NETWORK_EVIDENCE' && <NetworkEvidencePage data={result.telemetry || []} />}
                {activeTab === 'WORLD_MODEL' && <WorldModelPage result={result} kSteps={kSteps} />}
                {activeTab === 'MODEL_PERFORMANCE' && <ModelPerformancePage />}
                {activeTab === 'SYSTEM_HEALTH' && <SystemHealthPage health={health} result={result} />}
              </>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
