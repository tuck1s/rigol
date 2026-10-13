# rigol

Command-line tool for capturing screenshots and waveform data from a Rigol DS1054Z oscilloscope, using the [ds1054z](https://github.com/pklaus/ds1054z) library.

## Usage

```sh
# Capture a screenshot: saves as prefix_000.png, prefix_001.png, ...
./scope.py prefix

# Capture waveform data for all displayed channels as CSV
./scope.py prefix --csv

# Specify the scope's IP address (default: 192.168.0.25)
./scope.py prefix --ip 192.168.1.50
```

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install ds1054z
```

## Example

![Example capture](img/capture_000.png)
