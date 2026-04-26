#!/usr/bin/env python3
"""
CHSH / coincidence-window denominator audit — verification entry point.

Referenced from papers_final Bell audit as `chsh_denominator_audit.py`.

This is a thin wrapper around `bell_honest_window_scan_v1.py`, which loads the
NIST complete-blind side stream and sweeps coincidence windows (including
strict w=0 and Round-1 standard w=15). Same event stream, different pairing
rules → denominator / pair-count audit for reported S values.

Run from repository root:
  python scripts/explore/chsh_denominator_audit.py

Requires:
  data/nist_completeblind_side_streams.csv
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_window_scan_main():
    here = Path(__file__).resolve().parent
    target = here / "bell_honest_window_scan_v1.py"
    spec = importlib.util.spec_from_file_location(
        "bell_honest_window_scan_v1", target
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {target}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main


def main() -> int:
    return int(_load_window_scan_main()())


if __name__ == "__main__":
    raise SystemExit(main())
