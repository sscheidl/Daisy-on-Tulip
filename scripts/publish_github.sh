#!/usr/bin/env bash
# Run in an account allowed to create repositories. Does not touch existing repos.
set -euo pipefail
cd "$(dirname "$0")/.."
owner="$(gh api user --jq .login)"
if [ -n "$(git status --porcelain)" ]; then
    echo 'Commit the reviewed source before publishing.' >&2
    exit 1
fi
if git remote get-url origin >/dev/null 2>&1; then
    echo 'origin already exists; inspect it and publish manually.' >&2
    exit 1
fi
for backend in DIN USB_INTERNAL USB_EXTERNAL; do
    test -s "artifacts/daisy_toy_piano_$backend.bin"
done
python3 scripts/package.py
# The server refuses creation if this name already exists. No overwrite fallback.
gh repo create "$owner/Daisy-on-Tulip" --private --description 'Daisy on Tulip – Touchscreen Control for Daisy Seed3' --source . --remote origin --push
git push origin v0.1.0-alpha
gh release create v0.1.0-alpha --prerelease --title 'v0.1.0-alpha' --notes-file docs/RELEASE_NOTES.md artifacts/*.bin artifacts/*.elf artifacts/*.map artifacts/manifest.json artifacts/SHA256SUMS dist/daisy_toy_piano.zip
