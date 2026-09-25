import React, { useRef } from 'react';
import type { PredictionResult } from '../api';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

interface Props {
  result: PredictionResult;
  kSteps: number;
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

const WorldModelPage: React.FC<Props> = ({ result, kSteps }) => {
  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">WORLD MODEL ARCHITECTURE</div>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '40px' }}>
          
          {/* Left side: Architecture */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', flex: 1 }}>
            
            <div className="arch-box">OBSERVED STATE</div>
            <div className="arch-arrow">↓</div>
            <div className="arch-box">TEMPORAL CONTEXT</div>
            <div className="arch-arrow">↓</div>
            <div className="arch-box highlight" style={{ width: '300px' }}>
              <h3 style={{ color: 'var(--accent-cyan)' }}>WORLD MODEL</h3>
            </div>
            <div className="arch-arrow">↓</div>
            <div className="arch-box">NEXT STATE</div>
            <div className="arch-arrow">↓</div>
            <div className="arch-box highlight text-critical">FUTURE ROLLOUT</div>
            
          </div>
          
          {/* Right side: 3D Visualization */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '400px' }}>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '16px' }}>WORLD MODEL STATE</div>
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <WorldModelState risk={result.current_risk} kSteps={kSteps} />
            </div>
            <div style={{ marginTop: '16px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Latent State Transition Visualization
            </div>
          </div>
          
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
