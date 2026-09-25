import React, { useState, useMemo, useRef, useEffect } from 'react';
import type { PredictionResult } from '../api';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Line, Html, Bounds, useBounds } from '@react-three/drei';
import * as THREE from 'three';
// @ts-ignore
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force-3d';

interface Props {
  result: PredictionResult;
  timelineMode: number;
}

// Bounded log scale
const getBoundedScale = (value: number, minOut: number, maxOut: number, logScale = true) => {
  if (value <= 0) return minOut;
  const scaled = logScale ? Math.log(value + 1) : value;
  // Simple heuristic, assuming log max is around 10 for very high traffic
  return Math.min(Math.max(minOut + scaled * (maxOut - minOut) * 0.1, minOut), maxOut);
};

const NodeRenderer = ({ node, isSelected, showLabel, onClick, onPointerOver, onPointerOut }: any) => {
  const radius = getBoundedScale(node.activity, 2.5, 8);
  
  // Semantic Colors
  let color = node.type === 'source' ? '#3b82f6' : '#0ea5e9'; // normal activity cyan-blue
  let isImportant = false;
  
  if (node.isHighRisk) {
    color = '#ef4444'; // Red
    isImportant = true;
  } else if (node.isElevatedRisk) {
    color = '#f59e0b'; // Amber
    isImportant = true;
  }
  
  const highlightColor = '#ffffff';
  
  // Minimal animation for breathing effect
  const ref = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (ref.current && !isSelected) {
      ref.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * 2 + node.index) * 0.05);
    } else if (ref.current) {
      ref.current.scale.setScalar(1.2); // Highlighted scale
    }
  });

  const shouldShowLabel = showLabel || isSelected || isImportant;

  return (
    <group position={[node.x || 0, node.y || 0, node.z || 0]}>
      <Sphere 
        ref={ref}
        args={[radius, 16, 16]} 
        onClick={(e) => { e.stopPropagation(); onClick(node); }}
        onPointerOver={(e) => { e.stopPropagation(); onPointerOver(node); }}
        onPointerOut={(e) => { e.stopPropagation(); onPointerOut(); }}
      >
        <meshStandardMaterial 
          color={isSelected ? highlightColor : color} 
          emissive={isSelected ? highlightColor : color}
          emissiveIntensity={isSelected ? 0.6 : 0.2}
          roughness={0.4}
          metalness={0.6}
        />
      </Sphere>
      {shouldShowLabel && (
        <Html distanceFactor={50} center style={{ pointerEvents: 'none' }}>
          <div style={{ 
            background: 'var(--bg-panel)', 
            color: 'var(--text-primary)', 
            padding: '4px 8px', 
            borderRadius: 4, 
            fontSize: '0.75rem', 
            border: `1px solid ${color}`, 
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
            transform: `translate(0, -${radius * 2}px)`
          }}>
            <div style={{ fontWeight: 600 }}>{node.id}</div>
            {(isSelected || showLabel) && (
              <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: 2 }}>
                Packets: {node.activity}
              </div>
            )}
          </div>
        </Html>
      )}
    </group>
  );
};

const EdgeRenderer = ({ edge, isSelected }: any) => {
  if (!edge.source || typeof edge.source !== 'object' || edge.source.x == null || isNaN(edge.source.x) || edge.target.x == null || isNaN(edge.target.x)) return null;
  const width = getBoundedScale(edge.weight, 0.5, 3);
  
  const points = [
    new THREE.Vector3(edge.source.x || 0, edge.source.y || 0, edge.source.z || 0),
    new THREE.Vector3(edge.target.x || 0, edge.target.y || 0, edge.target.z || 0)
  ];

  return (
    <Line
      points={points}
      color={isSelected ? "#06b6d4" : "#242a3a"}
      lineWidth={width}
      transparent
      opacity={isSelected ? 0.8 : 0.4}
    />
  );
};

const SetupCamera = ({ autoFitTrigger }: { autoFitTrigger: number }) => {
  const bounds = useBounds();
  useEffect(() => {
    // Wait a frame for layout to settle, then fit
    setTimeout(() => {
      bounds.refresh().clip().fit();
    }, 50);
  }, [bounds, autoFitTrigger]);
  return null;
};

const OverviewPage: React.FC<Props> = ({ result, timelineMode }) => {
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [hoveredNode, setHoveredNode] = useState<any>(null);
  const [autoRotate, setAutoRotate] = useState(false);
  const [showLabels, setShowLabels] = useState(false);
  const [autoFitTrigger, setAutoFitTrigger] = useState(0);

  const telemetryIndex = result.telemetry ? (result.telemetry.length - 1) + timelineMode : 0;
  const currentTelemetry = result.telemetry ? result.telemetry[Math.max(0, telemetryIndex)] : {};

  const getFeature = (name: string, fallback: string = '-') => {
    if (currentTelemetry[name] !== undefined) return Number(currentTelemetry[name]).toFixed(2);
    const key = Object.keys(currentTelemetry).find(k => k.toLowerCase().includes(name.toLowerCase()));
    return key ? Number(currentTelemetry[key]).toFixed(2) : fallback;
  };

  // Run force simulation synchronously in useMemo to get static positions
  const { nodes, edges } = useMemo(() => {
    // Deep copy and add jitter to prevent NaN from physics blowup
    const gNodes = (result.network_graph?.nodes || []).map((n: any, i: number) => ({ 
      ...n,
      x: Math.random() * 10 - 5,
      y: Math.random() * 10 - 5,
      z: Math.random() * 10 - 5
    }));
    const gEdges = (result.network_graph?.edges || []).map((e: any) => ({ ...e }));

    // Inject risk heuristics (for demo: mark top nodes if high overall risk)
    if (result.current_risk > 0.5) {
      if (gNodes.length > 0) {
        gNodes.sort((a,b) => b.activity - a.activity);
        gNodes[0].isHighRisk = true;
      }
    } else if (result.current_risk > 0.3) {
      if (gNodes.length > 0) {
        gNodes.sort((a,b) => b.activity - a.activity);
        gNodes[0].isElevatedRisk = true;
      }
    }

    const sim = forceSimulation(gNodes)
      .numDimensions(3)
      .force('link', forceLink(gEdges).id((d: any) => d.id).distance(20))
      .force('charge', forceManyBody().strength(-150))
      .force('center', forceCenter(0, 0, 0))
      .stop();

    // Run synchronously
    sim.tick(150);

    return { nodes: gNodes, edges: gEdges };
  }, [result.network_graph, result.current_risk]);

  // Determine connected edges for selected node
  const connectedEdgeIndices = useMemo(() => {
    if (!selectedNode) return new Set();
    const set = new Set();
    edges.forEach((e: any, i: number) => {
      if (e.source.id === selectedNode.id || e.target.id === selectedNode.id) {
        set.add(i);
      }
    });
    return set;
  }, [selectedNode, edges]);

  return (
    <div className="grid">
      <div className="col-12" style={{ display: 'flex', gap: 16 }}>
        {/* 3D Network Topology Hero Panel */}
        <div className="panel" style={{ flex: '3', padding: 0, position: 'relative' }}>
          <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10, pointerEvents: 'none' }}>
            <div className="panel-title" style={{ margin: 0, fontSize: '1rem' }}>NETWORK THREAT TOPOLOGY</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Observed communication graph</div>
          </div>

          <div style={{ position: 'absolute', bottom: 20, left: 20, zIndex: 10, display: 'flex', gap: 8 }}>
            <button className="btn-toggle" onClick={() => setAutoFitTrigger(prev => prev + 1)}>RESET VIEW</button>
            <button className={`btn-toggle ${autoRotate ? 'active' : ''}`} onClick={() => setAutoRotate(!autoRotate)}>AUTO ROTATE</button>
            <button className={`btn-toggle ${showLabels ? 'active' : ''}`} onClick={() => setShowLabels(!showLabels)}>LABELS</button>
          </div>

          <div className="network-3d-container" onClick={() => setSelectedNode(null)}>
            <Canvas 
              camera={{ position: [0, 18, 35], fov: 50, near: 0.1, far: 2000 }}
              dpr={[1, 2]}
            >
              <color attach="background" args={['#0b0d14']} />
              <ambientLight intensity={0.4} />
              <directionalLight position={[10, 20, 15]} intensity={1} color="#ffffff" />
              {/* Subtle grid */}
              <gridHelper args={[200, 40, '#1e2434', '#161a25']} position={[0, -20, 0]} />

              <Bounds fit clip observe margin={1.2}>
                <SetupCamera autoFitTrigger={autoFitTrigger} />
                <group>
                  {edges.map((edge: any, i: number) => (
                    <EdgeRenderer 
                      key={i} 
                      edge={edge} 
                      isSelected={connectedEdgeIndices.has(i)}
                    />
                  ))}
                  {nodes.map((node: any) => {
                    const isSelected = selectedNode?.id === node.id;
                    const isHovered = hoveredNode?.id === node.id;
                    return (
                      <NodeRenderer 
                        key={node.id} 
                        node={node} 
                        isSelected={isSelected}
                        showLabel={showLabels || isHovered}
                        onClick={setSelectedNode} 
                        onPointerOver={setHoveredNode}
                        onPointerOut={() => setHoveredNode(null)}
                      />
                    );
                  })}
                </group>
              </Bounds>

              <OrbitControls 
                autoRotate={autoRotate} 
                autoRotateSpeed={0.8} 
                enableDamping 
                dampingFactor={0.05} 
                makeDefault
              />
            </Canvas>
          </div>
        </div>

        {/* Side Panels */}
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Node Inspector */}
          <div className="panel" style={{ flex: 1 }}>
            <div className="panel-title">NODE INSPECTOR</div>
            {selectedNode ? (
              <div>
                <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: 16 }}>
                  {selectedNode.id}
                </div>
                
                <div className="feature-group">
                  <div className="feature-group-title">Traffic Activity</div>
                  <div className="feature-row">
                    <span>Total Packets</span>
                    <span className="feature-val">{selectedNode.activity}</span>
                  </div>
                  <div className="feature-row">
                    <span>Endpoint Type</span>
                    <span className="feature-val" style={{ textTransform: 'capitalize' }}>{selectedNode.type}</span>
                  </div>
                </div>

                <div className="feature-group">
                  <div className="feature-group-title">Global State ({timelineMode === 0 ? 'NOW' : `T${timelineMode}`})</div>
                  <div className="feature-row">
                    <span>Flow Count</span>
                    <span className="feature-val">{getFeature('flow')}</span>
                  </div>
                  <div className="feature-row">
                    <span>Total Bytes</span>
                    <span className="feature-val">{getFeature('byte')}</span>
                  </div>
                  <div className="feature-row">
                    <span>SYN Ratio</span>
                    <span className="feature-val">{getFeature('syn')}</span>
                  </div>
                </div>
                
                <button className="btn-toggle" style={{ width: '100%', marginTop: 16 }} onClick={() => setSelectedNode(null)}>
                  CLEAR SELECTION
                </button>
              </div>
            ) : (
              <div style={{ color: 'var(--text-tertiary)', textAlign: 'center', marginTop: 40, fontSize: '0.875rem' }}>
                Select a node in the topology to inspect.
              </div>
            )}
          </div>

          {/* Current Network State Summary */}
          <div className="panel" style={{ flex: 1 }}>
            <div className="panel-title">GLOBAL SUMMARY ({timelineMode === 0 ? 'NOW' : `T${timelineMode}`})</div>
            
            <div className="feature-group" style={{ marginTop: 16 }}>
              <div className="feature-row">
                <span>Timestamp</span>
                <span className="feature-val">{currentTelemetry['window_start'] ? new Date(currentTelemetry['window_start'] * 1000).toISOString().split('T')[1].replace('Z','') : '-'}</span>
              </div>
              <div className="feature-row">
                <span>TCP Window</span>
                <span className="feature-val">{getFeature('tcp_window_mean')}</span>
              </div>
              <div className="feature-row">
                <span>IAT Mean</span>
                <span className="feature-val">{getFeature('iat')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
