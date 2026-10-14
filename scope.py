#!/usr/bin/env python3
import argparse
import csv
import glob
import os
import sys
from ds1054z import DS1054Z

DEFAULT_SCOPE_IP = '192.168.0.12'

parser = argparse.ArgumentParser(description='Capture a screenshot or waveform data from a Rigol DS1054Z oscilloscope.')
parser.add_argument('prefix', help='Filename prefix for the saved capture (a _nnn suffix is appended automatically)')
parser.add_argument('--ip', default=DEFAULT_SCOPE_IP, help='IP address of the scope (default: %(default)s)')
parser.add_argument('--csv', action='store_true', help='Capture waveform data for all displayed traces as a CSV file instead of a screenshot')
args = parser.parse_args()

ext = 'csv' if args.csv else 'png'
existing = glob.glob(f'{args.prefix}_[0-9][0-9][0-9].{ext}')
used = set()
for path in existing:
    suffix = os.path.basename(path)[len(args.prefix) + 1:-(len(ext) + 1)]
    if suffix.isdigit():
        used.add(int(suffix))

n = 0
while n in used:
    n += 1

filename = f'{args.prefix}_{n:03d}.{ext}'

try:
    s = DS1054Z(args.ip)  # queries *IDN? on connect, so this doubles as a liveness check
except Exception as e:
    sys.exit(f'Could not communicate with scope at {args.ip}: {e}')

if args.csv:
    channels = s.displayed_channels
    if not channels:
        sys.exit('No channels are currently displayed on the scope')
    samples_by_channel = {channel: s.get_waveform_samples(channel) for channel in channels}
    time_values = s.waveform_time_values
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time (s)'] + channels)
        writer.writerows([t] + [samples_by_channel[c][i] for c in channels] for i, t in enumerate(time_values))
else:
    open(filename, 'wb').write(s.display_data)

print('Written to',filename)
