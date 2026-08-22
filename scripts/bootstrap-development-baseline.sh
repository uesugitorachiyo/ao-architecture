#!/bin/sh
set -eu

controller_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$controller_dir/bootstrap_development_baseline.py" "$@"
fi
exec python "$controller_dir/bootstrap_development_baseline.py" "$@"
