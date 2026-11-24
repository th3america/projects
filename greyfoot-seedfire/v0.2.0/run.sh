#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 seedfire/bootstrap.py scan
printf '\nNext: python3 seedfire/bootstrap.py plan --model qwen3:8b\n'
