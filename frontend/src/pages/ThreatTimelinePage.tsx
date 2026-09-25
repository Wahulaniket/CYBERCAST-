import React from 'react';
import type { PredictionResult } from '../api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface Props {
  result: PredictionResult;
}

const ThreatTimelinePage: React.FC<Props> = ({ result }) => {
  const isHighRisk = result.current_risk > 0.5;

  const forecastData = Object.entries(result.risk_forecast).map(([horizon, risk]) => ({
    horizon,
    risk: risk * 100
  }));

  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">FUTURE THREAT TRAJECTORY (AUTOREGRESSIVE NETWORK-STATE ROLLOUT)</div>
        <div style={{ height: 400, marginTop: 24 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastData}>
              <defs>
                <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={isHighRisk ? "#ef4444" : "#06b6d4"} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={isHighRisk ? "#ef4444" : "#06b6d4"} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
              <XAxis dataKey="horizon" stroke="var(--text-tertiary)" />
              <YAxis domain={[0, 100]} stroke="var(--text-tertiary)" unit="%" />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-subtle)', borderRadius: 8 }}
                itemStyle={{ color: 'var(--text-primary)' }}
                formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Risk']}
              />
              <Area 
                type="monotone" 
                dataKey="risk" 
                stroke={isHighRisk ? "#ef4444" : "#06b6d4"} 
                fillOpacity={1} 
                fill="url(#colorRisk)" 
                strokeWidth={3} 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ThreatTimelinePage;
