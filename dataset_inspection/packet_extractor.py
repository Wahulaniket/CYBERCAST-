import socket
import math
from collections import Counter

class FlowState:
    __slots__ = ['ttls', 'tcp_windows', 'fragments', 'payload_sizes', 'src_ports', 'dst_ports', 'timestamps', 'tcp_seqs', 'retransmissions', 'packet_count', 'tcp_packet_count', 'udp_packet_count', 'icmp_packet_count', 'syn_count', 'ack_count', 'fin_count', 'rst_count', 'psh_count', 'urg_count', 'fwd_packet_count', 'bwd_packet_count', 'fwd_byte_count', 'bwd_byte_count']
    
    def __init__(self):
        self.ttls = []
        self.tcp_windows = []
        self.fragments = 0
        self.payload_sizes = []
        self.src_ports = []
        self.dst_ports = []
        self.timestamps = []
        
        self.tcp_seqs = {} 
        self.retransmissions = 0
        
        self.packet_count = 0
        self.tcp_packet_count = 0
        self.udp_packet_count = 0
        self.icmp_packet_count = 0
        
        self.syn_count = 0
        self.ack_count = 0
        self.fin_count = 0
        self.rst_count = 0
        self.psh_count = 0
        self.urg_count = 0
        
        self.fwd_packet_count = 0
        self.bwd_packet_count = 0
        self.fwd_byte_count = 0
        self.bwd_byte_count = 0

def entropy(labels):
    if not labels:
        return 0.0
    counts = Counter(labels)
    n = len(labels)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def mean(data):
    return sum(data) / len(data) if data else 0.0

def variance(data, m=None):
    if len(data) < 2: return 0.0
    if m is None: m = mean(data)
    return sum((x - m) ** 2 for x in data) / len(data)

def std(data, m=None):
    return math.sqrt(variance(data, m))

def extract_features_from_window(flow_key, window_index, state, window_size=5.0):
    f = {}
    f['flow_id'] = f"{flow_key[0]}:{flow_key[2]}-{flow_key[1]}:{flow_key[3]}-{flow_key[4]}"
    f['window_start'] = window_index * window_size
    f['protocol'] = flow_key[4]
    f['src_port'] = flow_key[2]
    f['dst_port'] = flow_key[3]
    
    f['flow_duration'] = float(state.timestamps[-1] - state.timestamps[0]) if len(state.timestamps) > 1 else 0.0
    f['flow_byte_count'] = state.fwd_byte_count + state.bwd_byte_count
    f['fwd_packet_count'] = state.fwd_packet_count
    f['bwd_packet_count'] = state.bwd_packet_count
    f['fwd_byte_count'] = state.fwd_byte_count
    f['bwd_byte_count'] = state.bwd_byte_count
    f['bidirectional_flow_ratio'] = float(state.fwd_packet_count / state.packet_count) if state.packet_count > 0 else 1.0

    if state.ttls:
        f['ttl_mean'] = float(mean(state.ttls))
        f['ttl_variance'] = float(variance(state.ttls, f['ttl_mean']))
        f['ttl_min'] = int(min(state.ttls))
        f['ttl_max'] = int(max(state.ttls))
    else:
        f['ttl_mean'], f['ttl_variance'], f['ttl_min'], f['ttl_max'] = 0.0, 0.0, 0, 0

    if state.tcp_windows:
        f['tcp_window_mean'] = float(mean(state.tcp_windows))
        f['tcp_window_std'] = float(std(state.tcp_windows, f['tcp_window_mean']))
        f['tcp_window_min'] = int(min(state.tcp_windows))
        f['tcp_window_max'] = int(max(state.tcp_windows))
    else:
        f['tcp_window_mean'], f['tcp_window_std'], f['tcp_window_min'], f['tcp_window_max'] = 0.0, 0.0, 0, 0

    f['fragment_count'] = state.fragments
    f['fragment_ratio'] = float(state.fragments / state.packet_count) if state.packet_count > 0 else 0.0

    if state.payload_sizes:
        n = len(state.payload_sizes)
        f['payload_mean'] = float(mean(state.payload_sizes))
        f['payload_std'] = float(std(state.payload_sizes, f['payload_mean']))
        f['payload_min'] = int(min(state.payload_sizes))
        f['payload_max'] = int(max(state.payload_sizes))
        s = sorted(state.payload_sizes)
        f['payload_median'] = float(s[n//2] if n % 2 != 0 else (s[n//2 - 1] + s[n//2]) / 2.0)
        non_zeros = sum(1 for p in state.payload_sizes if p > 0)
        f['payload_nonzero_ratio'] = float(non_zeros / n)
    else:
        f['payload_mean'], f['payload_std'], f['payload_min'], f['payload_max'], f['payload_median'], f['payload_nonzero_ratio'] = 0.0, 0.0, 0, 0, 0.0, 0.0

    s_dst_ports = set(state.dst_ports)
    s_src_ports = set(state.src_ports)
    f['unique_destination_ports'] = len(s_dst_ports)
    f['unique_source_ports'] = len(s_src_ports)
    
    seq_trans = 0
    valid_trans = 0
    if len(state.dst_ports) > 1:
        for i in range(1, len(state.dst_ports)):
            valid_trans += 1
            if abs(state.dst_ports[i] - state.dst_ports[i-1]) == 1:
                seq_trans += 1
    
    f['sequential_port_ratio'] = float(seq_trans / valid_trans) if valid_trans > 0 else 0.0
    f['nonsequential_port_ratio'] = 1.0 - f['sequential_port_ratio'] if valid_trans > 0 else 0.0
    f['destination_port_entropy'] = float(entropy(state.dst_ports))
    f['port_scan_rate'] = float(f['unique_destination_ports'] / window_size)

    f['tcp_retransmission_count'] = state.retransmissions
    f['tcp_retransmission_ratio'] = float(state.retransmissions / state.tcp_packet_count) if state.tcp_packet_count > 0 else 0.0

    iats = []
    if len(state.timestamps) > 1:
        for i in range(1, len(state.timestamps)):
            iats.append(state.timestamps[i] - state.timestamps[i-1])
            
    if iats:
        f['packet_iat_mean'] = float(mean(iats))
        f['packet_iat_variance'] = float(variance(iats, f['packet_iat_mean']))
        f['packet_iat_std'] = float(math.sqrt(f['packet_iat_variance']))
        f['packet_iat_max'] = float(max(iats))
        f['packet_iat_min'] = float(min(iats))
    else:
        f['packet_iat_mean'], f['packet_iat_variance'], f['packet_iat_std'], f['packet_iat_max'], f['packet_iat_min'] = 0.0, 0.0, 0.0, 0.0, 0.0

    f['packet_count'] = state.packet_count
    f['tcp_packet_count'] = state.tcp_packet_count
    f['udp_packet_count'] = state.udp_packet_count
    f['icmp_packet_count'] = state.icmp_packet_count

    f['syn_count'] = state.syn_count
    f['ack_count'] = state.ack_count
    f['fin_count'] = state.fin_count
    f['rst_count'] = state.rst_count
    f['psh_count'] = state.psh_count
    f['urg_count'] = state.urg_count
    
    total_tcp = state.tcp_packet_count if state.tcp_packet_count > 0 else 1
    f['syn_ratio'] = float(state.syn_count / total_tcp)
    f['ack_ratio'] = float(state.ack_count / total_tcp)
    f['fin_ratio'] = float(state.fin_count / total_tcp)
    f['rst_ratio'] = float(state.rst_count / total_tcp)
    f['psh_ratio'] = float(state.psh_count / total_tcp)
    f['urg_ratio'] = float(state.urg_count / total_tcp)

    return f

import dpkt
def process_packet(ts, buf, windows, window_size=5.0):
    window_idx = int(ts / window_size)
    if window_idx not in windows:
        windows[window_idx] = {}
        
    try:
        eth = dpkt.ethernet.Ethernet(buf)
    except Exception:
        return window_idx
        
    ip = eth.data
    
    is_ipv4 = isinstance(ip, dpkt.ip.IP)
    is_ipv6 = isinstance(ip, dpkt.ip6.IP6)
    
    if not (is_ipv4 or is_ipv6):
        return window_idx

    if is_ipv4:
        src_ip = socket.inet_ntoa(ip.src)
        dst_ip = socket.inet_ntoa(ip.dst)
        ttl = ip.ttl
        
        frag = False
        if hasattr(ip, 'offset'):
            if (ip.offset & dpkt.ip.IP_MF) != 0 or (ip.offset & dpkt.ip.IP_OFFMASK) != 0:
                frag = True
    else:
        src_ip = socket.inet_ntop(socket.AF_INET6, ip.src)
        dst_ip = socket.inet_ntop(socket.AF_INET6, ip.dst)
        ttl = ip.hlim
        frag = ip.nxt == 44

    trans = ip.data
    protocol = "OTHER"
    src_port = 0
    dst_port = 0
    payload_len = 0
    
    is_tcp = isinstance(trans, dpkt.tcp.TCP)
    is_udp = isinstance(trans, dpkt.udp.UDP)
    is_icmp = isinstance(trans, dpkt.icmp.ICMP) or (getattr(dpkt, 'icmp6', None) and isinstance(trans, getattr(dpkt.icmp6, 'ICMP6', type(None))))

    if is_tcp:
        protocol = "TCP"
        src_port = trans.sport
        dst_port = trans.dport
        payload_len = len(trans.data)
    elif is_udp:
        protocol = "UDP"
        src_port = trans.sport
        dst_port = trans.dport
        payload_len = len(trans.data)
    elif is_icmp:
        protocol = "ICMP"
        payload_len = len(trans.data)
    else:
        if hasattr(ip, 'data'):
            payload_len = len(ip.data)

    if src_ip > dst_ip:
        flow_key = (dst_ip, src_ip, dst_port, src_port, protocol)
        dir_fwd = False
    else:
        flow_key = (src_ip, dst_ip, src_port, dst_port, protocol)
        dir_fwd = True
        
    if flow_key not in windows[window_idx]:
        windows[window_idx][flow_key] = FlowState()
        
    state = windows[window_idx][flow_key]
    
    state.packet_count += 1
    state.timestamps.append(ts)
    state.ttls.append(ttl)
    if frag:
        state.fragments += 1
    state.payload_sizes.append(payload_len)
    
    state.src_ports.append(src_port)
    state.dst_ports.append(dst_port)

    # flow features logic
    pkt_len = len(buf)
    if dir_fwd:
        state.fwd_packet_count += 1
        state.fwd_byte_count += pkt_len
    else:
        state.bwd_packet_count += 1
        state.bwd_byte_count += pkt_len

    if is_tcp:
        state.tcp_packet_count += 1
        state.tcp_windows.append(trans.win)
        
        flags = trans.flags
        if flags & dpkt.tcp.TH_SYN: state.syn_count += 1
        if flags & dpkt.tcp.TH_ACK: state.ack_count += 1
        if flags & dpkt.tcp.TH_FIN: state.fin_count += 1
        if flags & dpkt.tcp.TH_RST: state.rst_count += 1
        if flags & dpkt.tcp.TH_PUSH: state.psh_count += 1
        if flags & dpkt.tcp.TH_URG: state.urg_count += 1
        
        seq = trans.seq
        if seq in state.tcp_seqs:
            if payload_len > 0 and state.tcp_seqs[seq] == payload_len:
                state.retransmissions += 1
        if payload_len > 0:
            state.tcp_seqs[seq] = payload_len

    elif is_udp:
        state.udp_packet_count += 1
    elif is_icmp:
        state.icmp_packet_count += 1

    return window_idx
