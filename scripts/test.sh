#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
python3 scripts/generate_protocol.py --check
g++ -std=c++14 -g -fsanitize=address,undefined \
    -Ithird_party/DaisySP/Source -Ithird_party/DaisySP/Source/Utility \
    -c third_party/DaisySP/Source/Synthesis/oscillator.cpp -o build/oscillator.o
g++ -std=c++14 -g -fsanitize=address,undefined -Ithird_party/libDaisy/src \
    -c third_party/libDaisy/src/hid/midi_parser.cpp -o build/midi_parser.o
g++ -std=c++14 -Wall -Wextra -Werror -g -fsanitize=address,undefined \
    -Idaisy/include -isystem third_party/libDaisy/src -isystem third_party/DaisySP/Source -isystem third_party/DaisySP/Source/Utility \
    tests/core_test.cpp build/oscillator.o build/midi_parser.o \
    -o build/core_test
./build/core_test
PYTHONPATH="$PWD/tulip" python3 -m unittest discover -s tests -v
python3 -m compileall -q tulip scripts
