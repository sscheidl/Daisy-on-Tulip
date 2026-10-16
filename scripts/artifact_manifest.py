#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
files = {}
for ext in ("bin", "elf", "map"):
    for p in sorted((root / "artifacts").glob("*." + ext)):
        files[p.name] = {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
manifest = {
    "version": "v0.1.0-alpha",
    "target": "Electro-Smith Seed3 Desktop Dev Kit",
    "app_type": "BOOT_NONE / internal flash 0x08000000",
    "compiler": subprocess.check_output(["arm-none-eabi-g++", "--version"], text=True).splitlines()[0],
    "dependencies": json.loads((root / "dependencies.lock.json").read_text()),
    "firmware_sources": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(list((root / "daisy/include").glob("*.h")) + list((root / "daisy/src").glob("*.cpp")) + [root / "daisy/Makefile", root / "config/protocol.json"])
    },
    "tulip_sources": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((root / "tulip/daisy_toy_piano").glob("*.py"))
    },
    "files": files,
    "hardware_verified": False
}
(root / "artifacts/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
