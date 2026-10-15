#!/usr/bin/env python3
import argparse
import csv
import math
import sys
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot the time-domain trace and FFT spectrum of a waveform CSV captured by scope.py --csv.')
parser.add_argument('csvfile', help='CSV file with a Time (s) column followed by one column per channel')
parser.add_argument('--save', metavar='PNG', help='Save the plot to this file instead of opening a window')
args = parser.parse_args()

FREQ_UNITS = [(1e9, 'GHz'), (1e6, 'MHz'), (1e3, 'kHz'), (1, 'Hz')]


def freq_unit(f):
    return next((u for u in FREQ_UNITS if f >= u[0]), FREQ_UNITS[-1])


def fmt_freq(f, resolution=None):
    scale, unit = freq_unit(f)
    if resolution is None:
        return f'{f / scale:.4g} {unit}'
    # Show only as many decimals as the frequency resolution (bin spacing) justifies
    decimals = max(0, math.ceil(-math.log10(resolution / scale)))
    return f'{f / scale:.{decimals}f} {unit}'


with open(args.csvfile, newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    data = np.array([[float(v) for v in row] for row in reader])

if data.shape[0] < 2 or data.shape[1] < 2:
    sys.exit(f'{args.csvfile} does not contain any waveform data')

t = data[:, 0]
channels = header[1:]
dt = (t[-1] - t[0]) / (len(t) - 1)
window = np.hanning(len(t))
freqs = np.fft.rfftfreq(len(t), dt)
axis_scale, axis_unit = freq_unit(freqs[-1])

fig, (ax_t, ax_f) = plt.subplots(2, 1, figsize=(10, 8))
for i, name in enumerate(channels, start=1):
    v = data[:, i]
    ax_t.plot(t * 1e6, v, label=name)
    ac = (v - v.mean()) * window
    # Scale so a sine of amplitude A shows as A (Hann coherent gain is 0.5)
    mag = np.abs(np.fft.rfft(ac)) * 2 / window.sum()
    db = 20 * np.log10(np.maximum(mag, 1e-12))
    ax_f.plot(freqs / axis_scale, db, label=name)

    # Peaks are local maxima, so one broad peak is not reported as several adjacent bins
    is_peak = (db[1:-1] > db[:-2]) & (db[1:-1] >= db[2:])
    peak_bins = np.flatnonzero(is_peak) + 1
    top = peak_bins[np.argsort(db[peak_bins])[::-1][:3]]
    print(f'{name}:')
    for rank, k in enumerate(top, start=1):
        print(f'  Peak {rank}: {fmt_freq(freqs[k], freqs[1])}  {db[k]:.1f} dBV')
    # The median is robust against the peaks, unlike the mean
    print(f'  Noise floor (median): {np.median(db[1:]):.1f} dBV')

ax_t.set_xlabel('Time (µs)')
ax_t.set_ylabel('Voltage (V)')
ax_t.set_title(f'{args.csvfile}: {len(t)} samples, {fmt_freq(1 / dt)[:-2]}S/s, {(t[-1] - t[0]) * 1e6:g} µs')
ax_f.set_xlabel(f'Frequency ({axis_unit})')
ax_f.set_ylabel('Magnitude (dBV)')
ax_f.set_title(f'Spectrum (Hann window, DC removed, bin spacing {fmt_freq(freqs[1])})')
for ax in (ax_t, ax_f):
    ax.grid(True, alpha=0.3)
    ax.legend()
fig.tight_layout()

if args.save:
    fig.savefig(args.save, dpi=120)
    print(args.save)
else:
    plt.show()
