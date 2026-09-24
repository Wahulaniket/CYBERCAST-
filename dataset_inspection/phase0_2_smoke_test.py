import sys
import os

try:
    import dpkt
except ImportError:
    print("dpkt not installed")
    sys.exit(1)

def check_format(filepath):
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic in (b'\xa1\xb2\xc3\xd4', b'\xd4\xc3\xb2\xa1', b'\xa1\xb2\x3c\x4d', b'\x4d\x3c\xb2\xa1'):
            return "PCAP"
        elif magic == b'\x0a\x0d\x0d\x0a':
            return "PCAPNG"
        else:
            return f"UNKNOWN ({magic.hex()})"

def smoke_test(filepath):
    fmt = check_format(filepath)
    print(f"Format: {fmt}")
    
    success = 0
    failed = 0
    first_ts = None
    last_ts = None
    
    has_eth = False
    has_ipv4 = False
    has_ipv6 = False
    has_tcp = False
    has_udp = False
    has_icmp = False
    has_tcp_flags = False
    has_tcp_window = False

    try:
        with open(filepath, 'rb') as f:
            if fmt == "PCAP":
                reader = dpkt.pcap.Reader(f)
            elif fmt == "PCAPNG":
                if hasattr(dpkt, 'pcapng'):
                    reader = dpkt.pcapng.Reader(f)
                else:
                    print("Error: pcapng format detected but dpkt.pcapng is not available.")
                    return
            else:
                print("Unsupported format.")
                return
            
            print(f"Link type: {getattr(reader, 'datalink', 'unknown')}")

            for ts, buf in reader:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
                
                try:
                    # Parse ethernet
                    eth = dpkt.ethernet.Ethernet(buf)
                    has_eth = True
                    
                    if isinstance(eth.data, dpkt.ip.IP):
                        has_ipv4 = True
                        ip = eth.data
                    elif isinstance(eth.data, dpkt.ip6.IP6):
                        has_ipv6 = True
                        ip = eth.data
                    else:
                        ip = None
                        
                    if ip:
                        if isinstance(ip.data, dpkt.tcp.TCP):
                            has_tcp = True
                            tcp = ip.data
                            _ = tcp.flags
                            has_tcp_flags = True
                            _ = tcp.win
                            has_tcp_window = True
                        elif isinstance(ip.data, dpkt.udp.UDP):
                            has_udp = True
                        elif isinstance(ip.data, dpkt.icmp.ICMP):
                            has_icmp = True

                    success += 1
                    if success >= 5000:
                        break
                except Exception as e:
                    failed += 1
                    if failed >= 10:
                        print(f"Too many failures. Last error: {e}")
                        break

    except Exception as e:
        print(f"File reading error: {e}")

    print(f"Packets successfully parsed: {success}")
    print(f"Packets failed: {failed}")
    print(f"First timestamp: {first_ts}")
    print(f"Last timestamp: {last_ts}")
    
    print("\nFeature Checks:")
    print(f"Ethernet frame decoded: {has_eth}")
    print(f"IPv4 identified: {has_ipv4}")
    print(f"IPv6 identified: {has_ipv6}")
    print(f"TCP identified: {has_tcp}")
    print(f"UDP identified: {has_udp}")
    print(f"ICMP identified: {has_icmp}")
    print(f"TCP flags read: {has_tcp_flags}")
    print(f"TCP window read: {has_tcp_window}")


if __name__ == "__main__":
    test_file = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\PCAPs\pcaps\Friday-WorkingHours.pcap"
    smoke_test(test_file)
