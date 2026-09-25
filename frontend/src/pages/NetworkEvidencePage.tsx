import React from 'react';


interface Props {
  data: any[];
}

const NetworkEvidencePage: React.FC<Props> = ({ data }) => {
  // Use the last 20 records for the evidence table, simulating recent history
  const recentData = data.slice(-20).reverse();

  return (
    <div className="grid">
      <div className="col-12 panel">
        <div className="panel-title">NETWORK EVIDENCE</div>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
          Analyst evidence table of most recent state transitions.
        </p>
        
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Packets</th>
                <th>Bytes</th>
                <th>Avg IAT</th>
                <th>SYN Ratio</th>
                <th>ACK Ratio</th>
                <th>RST Ratio</th>
                <th>Dest Ports</th>
              </tr>
            </thead>
            <tbody>
              {recentData.map((row, i) => {
                const ts = row['window_start'] ? new Date(row['window_start'] * 1000).toISOString() : 'N/A';
                
                // Helper to safely get properties since columns depend on the dataset
                const getVal = (searchStr: string) => {
                  const key = Object.keys(row).find(k => k.toLowerCase().includes(searchStr));
                  return key && row[key] !== undefined ? Number(row[key]).toFixed(2) : '-';
                };

                return (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace' }}>{ts}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('packet')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('byte')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('iat mean')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('syn')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('ack')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('rst')}</td>
                    <td style={{ fontFamily: 'monospace' }}>{getVal('port')}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default NetworkEvidencePage;
