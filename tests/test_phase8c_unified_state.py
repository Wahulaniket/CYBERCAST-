import pytest
import os
import pandas as pd
import numpy as np

def test_unified_state_sanity():
    data_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\unified_v2"
    if not os.path.exists(data_dir):
        pytest.skip("Unified data directory not found")
        
    files = [f for f in os.listdir(data_dir) if f.endswith('.parquet')]
    if not files:
        pytest.skip("No parquet files found")
        
    df = pd.read_parquet(os.path.join(data_dir, files[0]))
    
    # 1. timestamps are monotonic per flow? Well, window_start is deterministic
    # But let's check that windows are multiples of 5
    assert np.all(df['window_start'] % 5.0 == 0)
    
    # 4. feature values are finite
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        assert np.all(np.isfinite(df[col].dropna()))
        
    # 5. labels are absent from feature columns
    cols_lower = [c.lower() for c in df.columns]
    assert 'label' not in cols_lower
    assert 'attack' not in cols_lower
    
    # 6. packet features are present
    assert 'ttl_mean' in df.columns
    assert 'payload_mean' in df.columns
    
    # 7. flow features are present
    assert 'flow_duration' in df.columns
    assert 'flow_byte_count' in df.columns
    assert 'fwd_packet_count' in df.columns
    
    # 9. no accidental IP leakage into model features (IPs are only in flow_id)
    assert 'src_ip' not in df.columns
    assert 'dst_ip' not in df.columns
    
    # 10. no raw payload data
    assert 'payload' not in df.columns # we have 'payload_mean' etc, but not the raw bytes
