import time
import dpkt

test_file = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\PCAPs\pcaps\Friday-WorkingHours.pcap"

start = time.time()
count = 0
with open(test_file, 'rb') as f:
    reader = dpkt.pcapng.Reader(f)
    for ts, buf in reader:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            count += 1
        except:
            pass
        if count >= 100000:
            break

end = time.time()
print(f"Time for 100k packets: {end - start:.2f}s")
print(f"Packets per second: {100000 / (end - start):.0f}")
