#!/usr/bin/env python3
"""USB install into /user/lib; mpremote resume never resets or flashes Tulip."""
import argparse
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument("--port", default="auto", help="mpremote port, e.g. /dev/ttyACM0 or COM4")
args = p.parse_args()
root = Path(__file__).resolve().parents[1]
base = ["mpremote", "connect", args.port, "resume", "fs"]
destination = ":/user/lib/daisy_toy_piano"
listing = subprocess.run(base + ["ls", ":/user/lib"], text=True, capture_output=True)
if listing.returncode:
    raise SystemExit("Tulip /user/lib not accessible over USB.\n" + listing.stderr)
if "daisy_toy_piano" not in listing.stdout:
    subprocess.run(base + ["mkdir", destination], check=True)
for path in sorted((root / "tulip/daisy_toy_piano").glob("*.py")):
    subprocess.run(base + ["cp", str(path), destination + "/" + path.name], check=True)
print("Installed. At Tulip REPL: import tulip; tulip.run('daisy_toy_piano')")
