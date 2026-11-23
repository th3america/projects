#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "SEEDFIRE needs Python 3.10+. Install python3, then run again." >&2
  exit 1
fi
if [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  exec python3 seedfire.py gui "$@"
fi
printf '%s\n' 'No GUI display detected. Read-only inventory:'
exec python3 seedfire.py scan "$@"
