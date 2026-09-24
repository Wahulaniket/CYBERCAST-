import cProfile
from phase8b_full_extraction import extract_features
import os

pcap_dir = r"D:\working_projects\SIH\cyberCast2\data\CIC-ID-2017\PCAPs\pcaps"
cProfile.run('extract_features("Monday-WorkingHours.pcap", os.path.join(pcap_dir, "Monday-WorkingHours.pcap"), is_validation=True)', 'profile.stats')

import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
