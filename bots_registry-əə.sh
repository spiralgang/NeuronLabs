#!/bin/bash
set -euo pipefail
shopt -s nullglob
# Bots Registry (əə) — NeuronLabs
# Discovers, registers, audits, and executes bots

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BOT_DIR="$SCRIPT_DIR/bots"
REGISTRY_LOG="$SCRIPT_DIR/bots_registry-əə.log"
mkdir -p "$BOT_DIR"

echo "[`date +%FT%T`] Scanning for bots in $BOT_DIR" | tee -a "$REGISTRY_LOG"

for bot in "$BOT_DIR"/*-bot "$BOT_DIR"/test_bot; do
  [ -f "$bot" ] && [ -x "$bot" ] || continue
  echo "Registering bot: $(basename "$bot")" | tee -a "$REGISTRY_LOG"
  echo "  Path: $bot" | tee -a "$REGISTRY_LOG"
  echo "  SHA256: $(sha256sum "$bot" | awk '{print $1}')" | tee -a "$REGISTRY_LOG"
  "$bot" --audit 2>/dev/null | tee -a "$REGISTRY_LOG"
done

# References:
# - /reference/vault.md (modular bot registry, audit patterns)