#!/usr/bin/env bash
# Build the GC9A01 firmware using an existing Arduino CLI environment.
# End users can use the supplied binaries without installing build tools.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
V=$(sed -n 's/^#define VERSAO *"\(.*\)"/\1/p' "$DIR/claudinho/config.h")
mkdir -p "$DIR/bin"
CHIP=esp32c3
FQBN="esp32:esp32:$CHIP:CDCOnBoot=cdc,PartitionScheme=min_spiffs"
echo "==> $CHIP $V"
# Keep build-machine paths out of firmware diagnostics.
PM="-fmacro-prefix-map=$HOME/=~/ -fmacro-prefix-map=$DIR/="
arduino-cli compile --clean --fqbn "$FQBN" --build-path "$DIR/build/$CHIP" --output-dir "$DIR/build/$CHIP" \
  --build-property "compiler.c.extra_flags=$PM" --build-property "compiler.cpp.extra_flags=$PM" \
  "$DIR/claudinho"
rm -f "$DIR"/bin/claudinho-$CHIP-*.bin
cp "$DIR/build/$CHIP/claudinho.ino.merged.bin" "$DIR/bin/claudinho-$CHIP-$V-completo.bin"
cp "$DIR/build/$CHIP/claudinho.ino.bin"        "$DIR/bin/claudinho-$CHIP-$V-ota.bin"
(cd "$DIR/bin" && sha256sum claudinho-$CHIP-$V-*.bin > SHA256SUMS-GC9A01.txt)
rm -rf "$DIR/build"
ls -la "$DIR/bin"
