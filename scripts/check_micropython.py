#!/usr/bin/env python3
"""Syntax/bytecode check against the MicroPython commit referenced by Tulip."""
import argparse
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, default=root / "third_party/micropython")
args = p.parse_args()
spec = json.loads((root / "dependencies.lock.json").read_text())["reference_MicroPython"]
source = args.source.resolve()
if not source.exists():
    source.mkdir(parents=True)
    subprocess.run(["git", "init", str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "fetch", "--depth", "1", spec["url"], spec["commit"]], check=True)
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", "FETCH_HEAD"], check=True)
actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
if actual != spec["commit"]:
    raise SystemExit("Unexpected MicroPython commit: " + actual)
subprocess.run(["make", "-C", str(source / "mpy-cross"), "-j4"], check=True)
compiler = source / "mpy-cross/build/mpy-cross"
subprocess.run([str(compiler), "--version"], check=True)
target = root / "build/mpy"
target.mkdir(parents=True, exist_ok=True)
for path in sorted((root / "tulip/daisy_toy_piano").glob("*.py")):
    subprocess.run([str(compiler), "-o", str(target / (path.stem + ".mpy")), str(path)], check=True)
    print("PASS mpy-cross:", path.name)
