"""
bootstrap_chsh_ci.py
--------------------
Bootstrap CI for binary CHSH S on paired-event samples.

Usage example:
  python scripts/explore/bootstrap_chsh_ci.py \
    --events-csv data/nist_completeblind_side_streams.csv \
    --window 15.0 \
    --n-boot 2000 \
    --seed 42 \
    --out-json artifacts/reports/chsh_bootstrap_ci_standard15.json
"""

import argparse
import csv
import json
import math
import os
from typing import List, Tuple

import numpy as np


Event = Tuple[float, int, int]  # (t, setting, outcome)
Pair = Tuple[int, int, int, int]  # (sa, sb, oa, ob)


def load_events_csv(path: str) -> Tuple[List[Event], List[Event]]:
    A: List[Event] = []
    B: List[Event] = []
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        need = {"side", "t", "setting", "outcome"}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError("CSV missing required columns: side,t,setting,outcome")
        for row in rd:
            side = str(row["side"]).strip().upper()
            if side not in ("A", "B"):
                continue
            t = float(row["t"])
            s = int(row["setting"])
            if s not in (0, 1):
                continue
            o = 1 if int(row["outcome"]) >= 0 else -1
            if side == "A":
                A.append((t, s, o))
            else:
                B.append((t, s, o))
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def pair_events(A: List[Event], B: List[Event], window: float) -> List[Pair]:
    paired: List[Pair] = []
    used_b = np.zeros(len(B), dtype=np.bool_)
    j = 0
    for ta, sa, oa in A:
        while j < len(B) and B[j][0] < ta - window:
            j += 1
        best_k = -1
        best_dt = None
        k = j
        while k < len(B) and B[k][0] <= ta + window:
            if not used_b[k]:
                dt = abs(B[k][0] - ta)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_k = k
            k += 1
        if best_k >= 0:
            used_b[best_k] = True
            _, sb, ob = B[best_k]
            paired.append((sa, sb, oa, ob))
    return paired


def chsh_from_pairs(arr: np.ndarray) -> float:
    sa = arr[:, 0]
    sb = arr[:, 1]
    oa = arr[:, 2]
    ob = arr[:, 3]
    prod = oa * ob

    def m(mask):
        if np.any(mask):
            return float(np.mean(prod[mask]))
        return 0.0

    Eab = m((sa == 0) & (sb == 0))
    Eabp = m((sa == 0) & (sb == 1))
    Eapb = m((sa == 1) & (sb == 0))
    Eapbp = m((sa == 1) & (sb == 1))
    return float(Eab + Eabp + Eapb - Eapbp)


def bootstrap_ci(pairs: List[Pair], n_boot: int, seed: int):
    arr = np.asarray(pairs, dtype=np.int16)
    n = arr.shape[0]
    if n == 0:
        raise ValueError("no pairs, cannot bootstrap")
    rng = np.random.default_rng(seed)
    s_vals = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n, endpoint=False)
        s_vals[i] = chsh_from_pairs(arr[idx])
    ci_low = float(np.percentile(s_vals, 2.5))
    ci_high = float(np.percentile(s_vals, 97.5))
    return s_vals, ci_low, ci_high


def main():
    ap = argparse.ArgumentParser(description="Bootstrap CI for binary CHSH S.")
    ap.add_argument("--events-csv", required=True)
    ap.add_argument("--window", type=float, required=True)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()

    A, B = load_events_csv(args.events_csv)
    pairs = pair_events(A, B, window=float(args.window))
    s_hat = chsh_from_pairs(np.asarray(pairs, dtype=np.int16))
    s_vals, ci_low, ci_high = bootstrap_ci(pairs, n_boot=int(args.n_boot), seed=int(args.seed))
    tsirelson = 2.0 * math.sqrt(2.0)

    result = {
        "events_csv": os.path.abspath(args.events_csv),
        "window": float(args.window),
        "pair_count": int(len(pairs)),
        "n_boot": int(args.n_boot),
        "seed": int(args.seed),
        "S_hat": float(s_hat),
        "CI_95": [ci_low, ci_high],
        "tsirelson": tsirelson,
        "ci_contains_tsirelson": bool(ci_low <= tsirelson <= ci_high),
        "p_bootstrap_S_gt_tsirelson": float(np.mean(s_vals > tsirelson)),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("wrote", args.out_json)


if __name__ == "__main__":
    main()
