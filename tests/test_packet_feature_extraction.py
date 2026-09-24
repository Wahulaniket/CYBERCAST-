import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset_inspection')))
from packet_extractor import process_packet, extract_features_from_window, FlowState

def test_ttl():
    state = FlowState()
    state.ttls = [64, 64, 60]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['ttl_mean'] == (64+64+60)/3
    assert f['ttl_min'] == 60
    assert f['ttl_max'] == 64

def test_tcp_window():
    state = FlowState()
    state.tcp_windows = [1000, 2000, 3000]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['tcp_window_mean'] == 2000.0

def test_fragmentation():
    state = FlowState()
    state.packet_count = 10
    state.fragments = 2
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['fragment_count'] == 2
    assert f['fragment_ratio'] == 0.2

def test_payload_statistics():
    state = FlowState()
    state.payload_sizes = [0, 100, 200]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['payload_mean'] == 100.0
    assert f['payload_min'] == 0
    assert f['payload_max'] == 200
    assert f['payload_median'] == 100.0
    assert f['payload_nonzero_ratio'] == 2/3

def test_port_statistics():
    state = FlowState()
    state.dst_ports = [80, 80, 443]
    state.src_ports = [1000, 1001, 1002]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['unique_destination_ports'] == 2
    assert f['unique_source_ports'] == 3

def test_sequential_port_ratio():
    state = FlowState()
    state.dst_ports = [80, 81, 82, 100]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    # Transitions: 80->81 (seq), 81->82 (seq), 82->100 (non)
    # 2 sequential out of 3 transitions
    assert abs(f['sequential_port_ratio'] - 2/3) < 1e-6

def test_port_entropy():
    state = FlowState()
    state.dst_ports = [80, 80]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['destination_port_entropy'] == 0.0

def test_retransmission_detection():
    state = FlowState()
    state.tcp_packet_count = 5
    state.retransmissions = 2
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['tcp_retransmission_count'] == 2
    assert f['tcp_retransmission_ratio'] == 0.4

def test_packet_iat():
    state = FlowState()
    state.timestamps = [1.0, 1.5, 2.5]
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    # IATs: 0.5, 1.0
    assert f['packet_iat_mean'] == 0.75
    assert f['packet_iat_min'] == 0.5
    assert f['packet_iat_max'] == 1.0

def test_tcp_flags():
    state = FlowState()
    state.tcp_packet_count = 10
    state.syn_count = 2
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert f['syn_count'] == 2
    assert f['syn_ratio'] == 0.2

def test_no_label_leakage():
    state = FlowState()
    f = extract_features_from_window(('A', 'B', 1, 2, 'TCP'), 0, state)
    assert 'label' not in [k.lower() for k in f.keys()]
    assert 'attack' not in [k.lower() for k in f.keys()]
