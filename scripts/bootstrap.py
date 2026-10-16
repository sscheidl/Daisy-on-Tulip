#!/usr/bin/env python3
"""Fetch exact official library commits; never reset an existing checkout."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "dependencies.lock.json").read_text())
for name in ("libDaisy", "DaisySP"):
    spec = lock[name]
    target = ROOT / "third_party" / name
    if not target.exists():
        target.parent.mkdir(exist_ok=True)
        subprocess.run(["git", "clone", "--no-checkout", spec["url"], str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "checkout", "--detach", spec["commit"]], check=True)
    actual = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
    if actual != spec["commit"]:
        raise SystemExit(f"{name}: unexpected commit {actual}; use a separate clean checkout")
    if subprocess.check_output(["git", "-C", str(target), "status", "--porcelain", "--untracked-files=no", "--ignore-submodules"], text=True).strip():
        raise SystemExit(f"{name}: modified tracked files; refusing to build")
    subprocess.run(["git", "-C", str(target), "submodule", "update", "--init", "--recursive"], check=True)
    print(name, actual)
