#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VALID_CONTEXTS = {"XXX", "XYY", "YXY", "YYX"}


@dataclass
class Shot:
    basis: str
    outcome: str


def _normalize_basis(raw: str) -> str:
    s = raw.strip().upper().replace(" ", "")
    s = s.replace(",", "")
    if len(s) != 3:
        raise ValueError(f"Invalid basis length: {raw}")
    return s


def _normalize_outcome(raw: str) -> str:
    s = raw.strip().replace(" ", "")
    if len(s) != 3:
        raise ValueError(f"Invalid outcome length: {raw}")
    for ch in s:
        if ch not in {"0", "1", "+", "-", "L"}:
            raise ValueError(f"Unsupported outcome char '{ch}' in {raw}")
    return s


def _char_to_spin(ch: str) -> int | None:
    if ch in {"0", "+"}:
        return +1
    if ch in {"1", "-"}:
        return -1
    # L means loss/no-click
    return None


def context_product(outcome: str) -> int | None:
    vals = [_char_to_spin(c) for c in outcome]
    if any(v is None for v in vals):
        return None
    out = 1
    for v in vals:
        out *= int(v)
    return out


def load_shots_csv(path: str | Path) -> list[Shot]:
    p = Path(path)
    rows: list[Shot] = []
    with p.open("r", encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        for r in rd:
            basis = _normalize_basis(r["measurement_basis"])
            outcome = _normalize_outcome(r["outcome"])
            rows.append(Shot(basis=basis, outcome=outcome))
    return rows


def load_shots_json(path: str | Path) -> list[Shot]:
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    rows: list[Shot] = []
    if isinstance(obj, dict) and "shots" in obj:
        data = obj["shots"]
    elif isinstance(obj, list):
        data = obj
    else:
        raise ValueError("JSON must be list or {'shots': [...]}")
    for it in data:
        basis = _normalize_basis(it["measurement_basis"])
        outcome = _normalize_outcome(it["outcome"])
        rows.append(Shot(basis=basis, outcome=outcome))
    return rows


def expand_counts_to_shots(counts: dict[str, dict[str, int]]) -> list[Shot]:
    """
    counts format:
      {
        "XXX": {"000": 120, "111": 118, ...},
        "XYY": {...},
        ...
      }
    """
    rows: list[Shot] = []
    for basis, table in counts.items():
        b = _normalize_basis(basis)
        for outcome, n in table.items():
            o = _normalize_outcome(outcome)
            for _ in range(int(n)):
                rows.append(Shot(basis=b, outcome=o))
    return rows


def load_any(path: str | Path) -> list[Shot]:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return load_shots_csv(p)
    if p.suffix.lower() == ".json":
        obj = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(obj, dict) and "counts" in obj:
            return expand_counts_to_shots(obj["counts"])
        return load_shots_json(p)
    raise ValueError(f"Unsupported file extension: {p.suffix}")


def compute_fr_from_shots(shots: Iterable[Shot]) -> dict:
    """
    F = E(XXX)-E(XYY)-E(YXY)-E(YYX)
    R = valid_triplet_shots / total_shots_in_audit_contexts
    A valid triplet is a shot without any 'L' (loss) symbol.
    """
    by_ctx: dict[str, list[int]] = {k: [] for k in VALID_CONTEXTS}
    valid = 0
    total = 0
    ignored_non_audit = 0
    for s in shots:
        if s.basis not in VALID_CONTEXTS:
            ignored_non_audit += 1
            continue
        total += 1
        p = context_product(s.outcome)
        if p is None:
            continue
        valid += 1
        by_ctx[s.basis].append(int(p))

    def e(ctx: str) -> float:
        arr = by_ctx[ctx]
        if not arr:
            return 0.0
        return float(sum(arr) / len(arr))

    exxx = e("XXX")
    exyy = e("XYY")
    eyxy = e("YXY")
    eyyx = e("YYX")
    f = exxx - exyy - eyxy - eyyx
    r = float(valid / total) if total else 0.0
    return {
        "contexts": {
            "XXX": {"n_valid": len(by_ctx["XXX"]), "E": exxx},
            "XYY": {"n_valid": len(by_ctx["XYY"]), "E": exyy},
            "YXY": {"n_valid": len(by_ctx["YXY"]), "E": eyxy},
            "YYX": {"n_valid": len(by_ctx["YYX"]), "E": eyyx},
        },
        "F": float(f),
        "R": float(r),
        "D": float(f * r),
        "n_total_audit_contexts": int(total),
        "n_valid_triplets": int(valid),
        "n_ignored_non_audit_contexts": int(ignored_non_audit),
    }

