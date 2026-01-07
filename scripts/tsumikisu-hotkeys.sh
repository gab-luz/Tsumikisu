#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
python3 "$SCRIPT_DIR/tsumikisu-launcher.py" hotkeys
