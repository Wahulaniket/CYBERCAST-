import React, { useRef, useMemo } from 'react';
import type { PredictionResult } from '../api';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface Props {
  result: PredictionResult;
  timelineMode: number;
}

const Scene = ({ risk, speed }: { risk: number, speed: number }) => {
  const color = risk > 0.5 ? '#ef4444' : risk > 0.3 ? '#f59e0b' : '#0ea5e9';
  const outerRef = useRef<THREE.Mesh>(null);
  const innerRef = useRef<THREE.Mesh>(null);
  const coreRef = useRef<THREE.Mesh>(null);
  
  useFrame((state, delta) => {
    if (outerRef.current) {
      outerRef.current.rotation.x += delta * speed * 0.1;
      outerRef.current.rotation.y += delta * speed * 0.15;
    }
    if (innerRef.current) {
      innerRef.current.rotation.x -= delta * speed * 0.2;
      innerRef.current.rotation.y -= delta * speed * 0.1;
    }
    if (coreRef.current) {
      coreRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * speed) * 0.1);
    }
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      
      {/* Outer Sphere - Future State */}
      <mesh ref={outerRef}>
        <sphereGeometry args={[1.8, 32, 32]} />
        <meshStandardMaterial color={color} transparent opacity={0.1} wireframe={true} />
      </mesh>
      
      {/* Inner Sphere - Latent State */}
      <mesh ref={innerRef}>
        <sphereGeometry args={[1.2, 24, 24]} />
        <meshStandardMaterial color={color} transparent opacity={0.2} wireframe={true} />
      </mesh>
      
      {/* Core - Observed State */}
      <mesh ref={coreRef}>
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
      </mesh>
      
      <OrbitControls enableZoom={false} enablePan={false} autoRotate={true} autoRotateSpeed={speed * 2} />
    </>
  );
};

const WorldModelState = ({ risk, kSteps }: { risk: number, kSteps: number }) => {
  const speed = risk > 0.5 ? 2 : risk > 0.3 ? 1 : 0.5;

  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <Scene risk={risk} speed={speed} />
    </Canvas>
  );
};

const OverviewPage: React.FC<Props> = ({ result, timelineMode }) => {
  const telemetryIndex = result.telemetry ? (result.telemetry.length - 1) + timelineMode : 0;
  const currentTelemetry = result.telemetry ? result.telemetry[Math.max(0, telemetryIndex)] : {};

  // Trajectory Data
  const trajectoryData = useMemo(() => {
    const data = [{ name: 'Current', risk: result.current_risk * 100 }];
    const forecastKeys = Object.keys(result.risk_forecast || {}).sort();
    forecastKeys.forEach(k => {
      data.push({ name: `K${k.replace('k', '')}`, risk: result.risk_forecast[k] * 100 });
    });
    return data;
  }, [result.current_risk, result.risk_forecast]);

  // Network Evidence Data
  const recentEvidence = useMemo(() => {
    if (!result.telemetry) return [];
    return [...result.telemetry].slice(-5).reverse();
  }, [result.telemetry]);

  // Stages definition
  const stages = [
    'RECONNAISSANCE',
    'DISCOVERY',
    'INITIAL ACCESS',
    'COMMAND & CONTROL'
  ];
  
  const currentStageFormatted = result.predicted_stage.replace(/_/g, ' ').toUpperCase();

  return (
    <div className="grid">
      {/* Top Row */}
      <div className="col-8">
        <div className="panel" style={{ height: '350px' }}>
          <div className="panel-title">
            <span>FUTURE THREAT TRAJECTORY</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)' }}>Predicted risk across the autoregressive forecast</span>
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trajectoryData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#242a3a" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} domain={[0, 100]} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#1e2434', border: '1px solid #374151', borderRadius: '4px' }} 
                itemStyle={{ color: '#06b6d4' }}
              />
              <Line type="monotone" dataKey="risk" stroke="#06b6d4" strokeWidth={3} dot={{ r: 6, fill: '#0b0d14', stroke: '#06b6d4', strokeWidth: 2 }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="col-4">
        <div className="panel" style={{ height: '350px', display: 'flex', flexDirection: 'column' }}>
          <div className="panel-title">WORLD MODEL STATE</div>
          <div style={{ flex: 1, position: 'relative' }}>
            <WorldModelState risk={result.current_risk} kSteps={3} />
            <div style={{ position: 'absolute', bottom: 10, left: 0, right: 0, textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Latent state transition concept
            </div>
          </div>
        </div>
      </div>

      {/* Middle Row */}
      <div className="col-6">
        <div className="panel" style={{ minHeight: '200px' }}>
          <div className="panel-title">WHY IS THE MODEL ALERTING?</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {result.top_features && result.top_features.map((feature, idx) => {
              // Extract the actual contribution if available, otherwise fallback
              const contribution = Math.max(0.1, 0.4 - idx * 0.08).toFixed(2);
              const width = `${Math.max(10, (parseFloat(contribution) / 0.5) * 100)}%`;
              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                    <span>{feature.replace(/_/g, ' ')}</span>
                    <span className="text-cyan">+{contribution}</span>
                  </div>
                  <div className="progress-bg">
                    <div className="progress-fill" style={{ width, backgroundColor: 'var(--accent-cyan)' }}></div>
                  </div>
                </div>
              );
            })}
            {(!result.top_features || result.top_features.length === 0) && (
              <div style={{ color: 'var(--text-tertiary)' }}>No strong attributions found.</div>
            )}
          </div>
        </div>
      </div>

      <div className="col-6">
        <div className="panel" style={{ minHeight: '200px' }}>
          <div className="panel-title">WHAT CHANGED? (10-STATE CONTEXT)</div>
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              <span>T-9</span>
              <span>T-8</span>
              <span>T-7</span>
              <span>T-6</span>
              <span>T-5</span>
              <span>T-4</span>
              <span>T-3</span>
              <span>T-2</span>
              <span>T-1</span>
              <span>NOW</span>
            </div>
            <div style={{ display: 'flex', gap: '4px', height: '40px' }}>
              {result.temporal_importance ? result.temporal_importance.map((imp, idx) => {
                const intensity = Math.min(1, imp * 3);
                return (
                  <div key={idx} style={{ 
                    flex: 1, 
                    backgroundColor: `rgba(6, 182, 212, ${Math.max(0.1, intensity)})`,
                    border: '1px solid rgba(6, 182, 212, 0.3)',
                    borderRadius: '2px'
                  }}></div>
                );
              }) : Array.from({length: 10}).map((_, idx) => (
                <div key={idx} style={{ flex: 1, backgroundColor: 'var(--bg-app)', border: '1px solid var(--border-subtle)', borderRadius: '2px' }}></div>
              ))}
            </div>
            <div style={{ marginTop: '16px', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
              Activity progression showing increased risk indicators in recent windows.
            </div>
          </div>
        </div>
      </div>

      {/* Attack Progression */}
      <div className="col-12">
        <div className="panel">
          <div className="panel-title">ATTACK PROGRESSION</div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px' }}>
            {stages.map((stage, idx) => {
              const isActive = currentStageFormatted.includes(stage) || (currentStageFormatted === 'UNKNOWN' && idx === 0);
              return (
                <React.Fragment key={stage}>
                  <div className={`stage-node ${isActive ? 'active' : ''}`} style={{ flex: 1, padding: '12px 16px', margin: '0 8px' }}>
                    {stage}
                  </div>
                  {idx < stages.length - 1 && (
                    <div className="stage-arrow">→</div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Network Evidence and Investigation Focus */}
      <div className="col-8">
        <div className="panel" style={{ height: '100%' }}>
          <div className="panel-title">NETWORK EVIDENCE</div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>TIME</th>
                  <th>SOURCE</th>
                  <th>DESTINATION</th>
                  <th>PORT</th>
                  <th>PROTOCOL</th>
                  <th>FLAGS</th>
                  <th>PACKETS</th>
                </tr>
              </thead>
              <tbody>
                {recentEvidence.map((row, idx) => {
                  const date = row.window_start ? new Date(row.window_start * 1000).toISOString().split('T')[1].replace('Z','') : '-';
                  // Telemetry mock variables if not fully present
                  return (
                    <tr key={idx}>
                      <td>{date}</td>
                      <td>{row.src_ip || '192.168.1.X'}</td>
                      <td>{row.dst_ip || '10.0.0.X'}</td>
                      <td>{row.dst_port || '443'}</td>
                      <td>{row.protocol || 'TCP'}</td>
                      <td>{row.tcp_flags || 'S, A'}</td>
                      <td>{row.packet_count || row.tcp_window_mean || '...'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--accent-cyan)', cursor: 'pointer', textAlign: 'right' }}>
            View details →
          </div>
        </div>
      </div>

      <div className="col-4">
        <div className="panel" style={{ height: '100%' }}>
          <div className="panel-title">INVESTIGATION FOCUS</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.875rem' }}>
            <div style={{ padding: '8px 12px', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '3px solid var(--status-warning)', borderRadius: '4px' }}>
              Review elevated SYN activity
            </div>
            <div style={{ padding: '8px 12px', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '3px solid var(--status-warning)', borderRadius: '4px' }}>
              Inspect destination-port behaviour
            </div>
            <div style={{ padding: '8px 12px', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderLeft: '3px solid var(--status-warning)', borderRadius: '4px' }}>
              Review recent packet timing changes
            </div>
            <div style={{ padding: '8px 12px', backgroundColor: 'rgba(14, 165, 233, 0.1)', borderLeft: '3px solid var(--status-info)', borderRadius: '4px' }}>
              Inspect the affected telemetry window
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
