#!/bin/bash
set -euo pipefail
shopt -s nullglob
# Bots Registry (əə) — NeuronLabs
# Discovers, registers, audits, and executes bots

BOT_DIR="./bots"
REGISTRY_LOG="bots_registry-əə.log"
mkdir -p "$BOT_DIR"

echo "[`date +%FT%T`] Scanning for bots in $BOT_DIR" | tee -a "$REGISTRY_LOG"

for bot in "$BOT_DIR"/*; do
  [ -x "$bot" ] || continue
  echo "Registering bot: $(basename "$bot")" | tee -a "$REGISTRY_LOG"
  echo "  Path: $bot" | tee -a "$REGISTRY_LOG"
  echo "  SHA256: $(sha256sum "$bot" | awk '{print $1}')" | tee -a "$REGISTRY_LOG"
  "$bot" --audit 2>/dev/null | tee -a "$REGISTRY_LOG"
done

# References:
# - /reference/vault.md (modular bot registry, audit patterns)