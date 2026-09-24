import sys
import os
import time
import psutil
import csv
import dpkt

pcap_dir = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\PCAPs\pcaps"
files = [
    "Monday-WorkingHours.pcap",
    "Tuesday-WorkingHours.pcap",
    "Wednesday-workingHours.pcap",
    "Thursday-WorkingHours.pcap",
    "Friday-WorkingHours.pcap"
]

reports_dir = r"D:\working_projects\SIH\cyberCast2\reports\dataset_inspection"
os.makedirs(reports_dir, exist_ok=True)
csv_path = os.path.join(reports_dir, "PCAP_STATISTICS.csv")

# Feature tracking (just need to know if we observe them at all)
features = {
    'TTL': False,
    'TCP Window': False,
    'IP Fragmentation': False,
    'Payload Length': False,
    'Source Port': False,
    'Destination Port': False,
    'Packet Timestamp': False,
    'TCP Sequence': False,
    'TCP ACK': False
}

results = []

for filename in files:
    filepath = os.path.join(pcap_dir, filename)
    print(f"Processing {filename}...")
    
    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss
    peak_mem = start_mem
    
    stats = {
        'filename': filename,
        'packet_count': 0,
        'first_timestamp': None,
        'last_timestamp': None,
        'duration': 0,
        'ipv4_count': 0,
        'ipv6_count': 0,
        'other_network_count': 0,
        'tcp_count': 0,
        'udp_count': 0,
        'icmp_count': 0,
        'other_transport_count': 0,
        'syn_count': 0,
        'ack_count': 0,
        'fin_count': 0,
        'rst_count': 0,
        'psh_count': 0,
        'urg_count': 0,
        'tcp_window_observed': 0,
        'tcp_sequence_observed': 0,
        'tcp_acknowledgement_observed': 0,
        'error': None,
        'parse_status': 'PASS',
        'peak_ram_mb': 0,
        'processing_time_s': 0
    }

    try:
        with open(filepath, 'rb') as f:
            reader = dpkt.pcapng.Reader(f)
            
            for i, (ts, buf) in enumerate(reader):
                if i % 100000 == 0:
                    current_mem = process.memory_info().rss
                    if current_mem > peak_mem:
                        peak_mem = current_mem
                
                if stats['first_timestamp'] is None:
                    stats['first_timestamp'] = ts
                stats['last_timestamp'] = ts
                features['Packet Timestamp'] = True
                
                try:
                    eth = dpkt.ethernet.Ethernet(buf)
                    
                    ip = eth.data
                    if isinstance(ip, dpkt.ip.IP):
                        stats['ipv4_count'] += 1
                        features['TTL'] = True
                        features['IP Fragmentation'] = True
                        features['Payload Length'] = True
                    elif isinstance(ip, dpkt.ip6.IP6):
                        stats['ipv6_count'] += 1
                        features['TTL'] = True
                        features['Payload Length'] = True
                    else:
                        stats['other_network_count'] += 1
                        stats['packet_count'] += 1
                        continue

                    trans = ip.data
                    if isinstance(trans, dpkt.tcp.TCP):
                        stats['tcp_count'] += 1
                        features['Source Port'] = True
                        features['Destination Port'] = True
                        features['TCP Sequence'] = True
                        features['TCP ACK'] = True
                        features['TCP Window'] = True
                        
                        flags = trans.flags
                        if flags & dpkt.tcp.TH_SYN: stats['syn_count'] += 1
                        if flags & dpkt.tcp.TH_ACK: stats['ack_count'] += 1
                        if flags & dpkt.tcp.TH_FIN: stats['fin_count'] += 1
                        if flags & dpkt.tcp.TH_RST: stats['rst_count'] += 1
                        if flags & dpkt.tcp.TH_PUSH: stats['psh_count'] += 1
                        if flags & dpkt.tcp.TH_URG: stats['urg_count'] += 1
                        
                        stats['tcp_window_observed'] += 1
                        stats['tcp_sequence_observed'] += 1
                        stats['tcp_acknowledgement_observed'] += 1

                    elif isinstance(trans, dpkt.udp.UDP):
                        stats['udp_count'] += 1
                        features['Source Port'] = True
                        features['Destination Port'] = True
                    elif isinstance(trans, dpkt.icmp.ICMP) or getattr(dpkt, 'icmp6', None) and isinstance(trans, getattr(dpkt.icmp6, 'ICMP6', type(None))):
                        stats['icmp_count'] += 1
                    else:
                        stats['other_transport_count'] += 1
                        
                    stats['packet_count'] += 1
                        
                except Exception as e:
                    stats['parse_status'] = 'FAIL'
                    stats['error'] = f"Packet {i} Error: {str(e)}"
                    print(f"Error parsing packet in {filename}: {e}")
                    break

    except Exception as e:
        stats['parse_status'] = 'FAIL'
        stats['error'] = f"File Error: {str(e)}"
        print(f"Error parsing {filename}: {e}")

    end_time = time.time()
    
    current_mem = process.memory_info().rss
    if current_mem > peak_mem:
        peak_mem = current_mem
        
    stats['peak_ram_mb'] = peak_mem / (1024 * 1024)
    stats['processing_time_s'] = end_time - start_time
    if stats['last_timestamp'] is not None and stats['first_timestamp'] is not None:
        stats['duration'] = stats['last_timestamp'] - stats['first_timestamp']
        
    results.append(stats)
    print(f"Finished {filename}: {stats['packet_count']} packets, status: {stats['parse_status']}, time: {stats['processing_time_s']:.2f}s, Peak RAM: {stats['peak_ram_mb']:.2f}MB")

# Write CSV
with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

# Feature output
features_path = os.path.join(reports_dir, "feature_availability.txt")
with open(features_path, 'w') as f:
    for k, v in features.items():
        f.write(f"{k}: {v}\n")

print("ALL DONE")
