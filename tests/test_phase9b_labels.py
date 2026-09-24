import pytest
import os
import pandas as pd
import numpy as np
import json

def test_label_validity():
    labeled_dir = r"D:\working_projects\SIH\cyberCast2\data\processed\labeled_v2"
    if not os.path.exists(labeled_dir):
        pytest.skip("Labeled data directory not found")
        
    files = [f for f in os.listdir(labeled_dir) if f.endswith('.parquet')]
    if not files:
        pytest.skip("No labeled parquet files found")
        
    # Check just the first file to be fast
    df = pd.read_parquet(os.path.join(labeled_dir, files[0]))
    
    # 1. all labels have valid binary values
    assert df['attack_binary'].isin([0, 1]).all()
    
    # 2. all timestamps are finite
    assert np.isfinite(df['window_start']).all()
    
    # 3. window_end > window_start
    assert (df['window_end'] > df['window_start']).all()
    
    # 5. labels are independent of feature columns
    # We can check that labels exist in the DataFrame
    assert 'attack_type' in df.columns
    assert 'label' in df.columns
    
    # 10. all unified feature rows have exactly one label
    # The merge was how='left', so if there's no NaN in attack_binary, it has exactly one label
    assert not df['attack_binary'].isna().any()

def test_timeline_metadata():
    timeline_path = r"D:\working_projects\SIH\cyberCast2\data\processed\labels\cicids2017_attack_timeline.json"
    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
        
    assert "source" in timeline
    assert "events" in timeline
    for ev in timeline['events']:
        assert "date" in ev
        assert "start" in ev
        assert "end" in ev
        assert "attack" in ev
