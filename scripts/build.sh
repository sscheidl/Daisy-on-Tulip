#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -d .tools/xpack-arm-none-eabi-gcc-14.2.1-1.1/bin ]; then
    export PATH="$PWD/.tools/xpack-arm-none-eabi-gcc-14.2.1-1.1/bin:$PATH"
fi
command -v arm-none-eabi-g++ >/dev/null || { echo 'Run scripts/install_toolchain.sh or provide arm-none-eabi-g++ in PATH.' >&2; exit 1; }
python3 scripts/generate_protocol.py --check
python3 scripts/bootstrap.py
jobs="${JOBS:-4}"
mkdir -p artifacts
make -C third_party/libDaisy -j"$jobs" > artifacts/build-libDaisy.log 2>&1 || { tail -50 artifacts/build-libDaisy.log; exit 1; }
make -C third_party/DaisySP -j"$jobs" > artifacts/build-DaisySP.log 2>&1 || { tail -50 artifacts/build-DaisySP.log; exit 1; }
for backend in DIN USB_INTERNAL USB_EXTERNAL; do
    # Clean guarantees backend flags and any changed headers are rebuilt.
    make -C daisy clean >/dev/null
    make -C daisy -j"$jobs" MIDI_BACKEND="$backend" > "artifacts/build-$backend.log" 2>&1 || { tail -50 "artifacts/build-$backend.log"; exit 1; }
    for extension in bin elf map; do
        cp "daisy/build/daisy_toy_piano_$backend.$extension" artifacts/
    done
    arm-none-eabi-size "artifacts/daisy_toy_piano_$backend.elf"
done
(cd artifacts && sha256sum *.bin *.elf *.map > SHA256SUMS)
python3 scripts/artifact_manifest.py
