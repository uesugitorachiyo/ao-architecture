#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from scripts.rust_binary_provenance import RustProvenanceError, read_rust_binary_metadata
except ModuleNotFoundError:
    from rust_binary_provenance import RustProvenanceError, read_rust_binary_metadata


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: read_rust_binary_metadata.py BINARY", file=sys.stderr)
        return 2
    try:
        metadata = read_rust_binary_metadata(Path(sys.argv[1]))
    except (OSError, RustProvenanceError) as exc:
        print(f"read_rust_binary_metadata.py: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
