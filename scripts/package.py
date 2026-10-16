#!/usr/bin/env python3
"""Create portable source/app/release archives without credentials or .git."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "artifacts/manifest.json").read_text())
for section in ("files", "firmware_sources", "tulip_sources"):
    for name, entry in manifest[section].items():
        path = root / "artifacts" / name if section == "files" else root / name
        expected = entry["sha256"] if isinstance(entry, dict) else entry
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit("Artifact/source changed since build manifest; rebuild first: " + name)
out = root / "dist"
out.mkdir(exist_ok=True)
bundle = out / "Daisy-on-Tulip-v0.1.0-alpha.bundle"
subprocess.run(["git", "-C", str(root), "bundle", "create", str(bundle), "--all"], check=True)
with zipfile.ZipFile(out / "daisy_toy_piano.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted((root / "tulip/daisy_toy_piano").glob("*.py")):
        z.write(p, "daisy_toy_piano/" + p.name)
    for name in ("README.md", "docs/TULIP_INSTALL.md", "LICENSE"):
        z.write(root / name, name)
tracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
with zipfile.ZipFile(out / "Daisy-on-Tulip-v0.1.0-alpha.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in filter(None, tracked):
        z.write(root / name, "Daisy-on-Tulip/" + name)
    for p in sorted((root / "artifacts").iterdir()):
        if p.is_file() and (p.suffix in (".bin", ".elf", ".map", ".log") or p.name == "SHA256SUMS"):
            z.write(p, "Daisy-on-Tulip/artifacts/" + p.name)
    z.write(out / "daisy_toy_piano.zip", "Daisy-on-Tulip/dist/daisy_toy_piano.zip")
    z.write(bundle, "Daisy-on-Tulip/dist/" + bundle.name)
print(out / "Daisy-on-Tulip-v0.1.0-alpha.zip")
