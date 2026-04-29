"""
nist_clock_reference_audit_v1.py
--------------------------------
Compare three pairing semantics on the same events CSV:
1) event_anchor_nearest
2) external_clock_bin
3) same_index_only
"""

import argparse
import csv
import json
import math
import os
from typing import Dict, List, Tuple

import numpy as np


Event = Tuple[float, int, int]


def load_events_csv(path: str) -> Tuple[List[Event], List[Event]]:
    A: List[Event] = []
    B: List[Event] = []
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            side = str(row["side"]).strip().upper()
            t = float(row["t"])
            s = int(row["setting"])
            o = int(row["outcome"])
            if s not in (0, 1):
                continue
            o = 1 if o >= 0 else -1
            if side == "A":
                A.append((t, s, o))
            elif side == "B":
                B.append((t, s, o))
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def compute_E_S(paired: List[Tuple[int, int, int, int]]) -> Dict[str, float]:
    if not paired:
        return {"Eab": 0.0, "Eabp": 0.0, "Eapb": 0.0, "Eapbp": 0.0, "S": float("nan")}

    arr = np.asarray(paired, dtype=np.int64)
    sa = arr[:, 0]
    sb = arr[:, 1]
    oa = arr[:, 2]
    ob = arr[:, 3]
    ab = oa * ob

    def m(mask: np.ndarray) -> float:
        if np.any(mask):
            return float(np.mean(ab[mask]))
        return 0.0

    Eab = m((sa == 0) & (sb == 0))
    Eabp = m((sa == 0) & (sb == 1))
    Eapb = m((sa == 1) & (sb == 0))
    Eapbp = m((sa == 1) & (sb == 1))
    S = float(Eab + Eabp + Eapb - Eapbp)
    return {"Eab": Eab, "Eabp": Eabp, "Eapb": Eapb, "Eapbp": Eapbp, "S": S}


def pair_event_anchor_nearest(A: List[Event], B: List[Event], window: float) -> List[Tuple[int, int, int, int]]:
    used_b = np.zeros(len(B), dtype=np.bool_)
    out: List[Tuple[int, int, int, int]] = []
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
            tb, sb, ob = B[best_k]
            out.append((sa, sb, oa, ob))
    return out


def pair_external_clock_bin(A: List[Event], B: List[Event], window: float) -> List[Tuple[int, int, int, int]]:
    if window <= 0:
        return pair_same_index_only(A, B)

    bins_a: Dict[int, List[Tuple[int, Event]]] = {}
    bins_b: Dict[int, List[Tuple[int, Event]]] = {}
    for i, e in enumerate(A):
        t = e[0]
        bi = int(math.floor(t / window))
        bins_a.setdefault(bi, []).append((i, e))
    for i, e in enumerate(B):
        t = e[0]
        bi = int(math.floor(t / window))
        bins_b.setdefault(bi, []).append((i, e))

    used_b: Dict[int, bool] = {}
    out: List[Tuple[int, int, int, int]] = []
    for bi, arr_a in bins_a.items():
        arr_b = bins_b.get(bi, [])
        if not arr_b:
            continue
        for _, (ta, sa, oa) in arr_a:
            best_j = -1
            best_dt = None
            for jb, (tb, sb, ob) in arr_b:
                if used_b.get(jb, False):
                    continue
                dt = abs(tb - ta)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_j = jb
                    best_sb = sb
                    best_ob = ob
            if best_j >= 0:
                used_b[best_j] = True
                out.append((sa, best_sb, oa, best_ob))
    return out


def pair_same_index_only(A: List[Event], B: List[Event]) -> List[Tuple[int, int, int, int]]:
    from collections import defaultdict

    a_map: Dict[float, List[Tuple[int, int]]] = defaultdict(list)
    b_map: Dict[float, List[Tuple[int, int]]] = defaultdict(list)
    for t, s, o in A:
        a_map[t].append((s, o))
    for t, s, o in B:
        b_map[t].append((s, o))

    out: List[Tuple[int, int, int, int]] = []
    for t, la in a_map.items():
        lb = b_map.get(t)
        if not lb:
            continue
        n = min(len(la), len(lb))
        for i in range(n):
            sa, oa = la[i]
            sb, ob = lb[i]
            out.append((sa, sb, oa, ob))
    return out


def run_one(A: List[Event], B: List[Event], scheme: str, window: float) -> Dict[str, float]:
    if scheme == "event_anchor_nearest":
        paired = pair_event_anchor_nearest(A, B, window)
    elif scheme == "external_clock_bin":
        paired = pair_external_clock_bin(A, B, window)
    elif scheme == "same_index_only":
        paired = pair_same_index_only(A, B)
    else:
        raise ValueError("unknown scheme: %s" % scheme)
    met = compute_E_S(paired)
    met["pair_count"] = int(len(paired))
    met["window"] = float(window)
    return met


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST clock-reference semantics audit v1")
    ap.add_argument("--events-csv", required=True, help="input events csv: side,t,setting,outcome")
    ap.add_argument("--windows", default="0,1,2,5,10,15", help="comma-separated window list")
    ap.add_argument(
        "--schemes",
        default="event_anchor_nearest,external_clock_bin,same_index_only",
        help="comma-separated schemes",
    )
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/clock_reference_audit.json",
        help="output json",
    )
    args = ap.parse_args()

    windows = [float(x.strip()) for x in args.windows.split(",") if x.strip()]
    schemes = [x.strip() for x in args.schemes.split(",") if x.strip()]

    A, B = load_events_csv(args.events_csv)
    out: Dict[str, object] = {
        "events_csv": os.path.abspath(args.events_csv),
        "windows": windows,
        "schemes": schemes,
        "results": {},
    }
    for s in schemes:
        rows = []
        for w in windows:
            rows.append(run_one(A, B, s, w))
        out["results"][s] = rows

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("saved:", args.out_json)


if __name__ == "__main__":
    main()
