#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
name=xpack-arm-none-eabi-gcc-14.2.1-1.1-linux-x64.tar.gz
expected=ed8c7d207a85d00da22b90cf80ab3b0b2c7600509afadf6b7149644e9d4790a6
mkdir -p .tools
if [ ! -x .tools/xpack-arm-none-eabi-gcc-14.2.1-1.1/bin/arm-none-eabi-g++ ]; then
    curl --fail --location --retry 3 "https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases/download/v14.2.1-1.1/$name" -o ".tools/$name"
    echo "$expected  .tools/$name" | sha256sum --check
    tar -xzf ".tools/$name" -C .tools
fi
.tools/xpack-arm-none-eabi-gcc-14.2.1-1.1/bin/arm-none-eabi-g++ --version | head -1
