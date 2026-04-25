"""
explore_ncc_singles_coincidence_bridge.py
-----------------------------------------
Bridge check for the "NCC denominator observability" question:

Given event CSV rows (side, t, setting, outcome), compute:
1) singles counts per side/setting
2) coincidence counts per setting pair under a declared pairing window
3) geometric normalization bridge:
     C_norm(a,b) = C(a,b) / sqrt(SA(a) * SB(b))
4) optional signed bridge (using +/- outcomes in paired events):
     C_signed_norm(a,b) = Sum(oA*oB) / sqrt(SA(a) * SB(b))

This script does NOT claim that C_norm is identical to CHSH E.
It only makes the denominator mapping explicit and reproducible.
"""

import argparse
import csv
import json
import math
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


Event = Tuple[float, int, int]  # (t, setting in {0,1}, outcome in {-1,+1})


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


def simulate_events(n: int = 120000, seed: int = 77) -> Tuple[List[Event], List[Event]]:
    rng = np.random.default_rng(seed)
    a = 0.0
    ap = np.pi / 4.0
    b = np.pi / 8.0
    bp = -np.pi / 8.0

    t0 = np.arange(n, dtype=np.float64)
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n)
    setA = rng.integers(0, 2, size=n)
    setB = rng.integers(0, 2, size=n)
    thA = np.where(setA == 0, a, ap)
    thB = np.where(setB == 0, b, bp)
    u = np.cos(lam - thA)
    v = np.cos(lam - thB)
    outA = np.where(u + 0.06 * rng.normal(size=n) >= 0.0, 1, -1)
    outB = np.where(v + 0.06 * rng.normal(size=n) >= 0.0, 1, -1)
    tA = t0 + 1.0 + 0.10 * rng.normal(size=n)
    tB = t0 + 1.0 + 0.10 * rng.normal(size=n)

    A = [(float(tA[i]), int(setA[i]), int(outA[i])) for i in range(n)]
    B = [(float(tB[i]), int(setB[i]), int(outB[i])) for i in range(n)]
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def pair_events(A: List[Event], B: List[Event], window: float):
    paired = []
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
            tb, sb, ob = B[best_k]
            paired.append((sa, sb, oa, ob, tb - ta))
    return paired


def singles_by_setting(events: List[Event]) -> Dict[int, int]:
    out = {0: 0, 1: 0}
    for _, s, _ in events:
        out[s] += 1
    return out


def analyze_window(A: List[Event], B: List[Event], window: float) -> Dict[str, object]:
    SA = singles_by_setting(A)
    SB = singles_by_setting(B)
    paired = pair_events(A, B, window=window)

    # per setting-pair statistics
    # cells[(sa,sb)] = {"coincidences": int, "signed_sum": int}
    cells = {(sa, sb): {"coincidences": 0, "signed_sum": 0} for sa in (0, 1) for sb in (0, 1)}

    dts = []
    for sa, sb, oa, ob, dt in paired:
        c = cells[(sa, sb)]
        c["coincidences"] += 1
        c["signed_sum"] += int(oa * ob)
        dts.append(float(dt))

    rows = []
    for sa in (0, 1):
        for sb in (0, 1):
            c = cells[(sa, sb)]["coincidences"]
            signed = cells[(sa, sb)]["signed_sum"]
            denom = math.sqrt(float(SA[sa]) * float(SB[sb]))
            c_norm = (float(c) / denom) if denom > 0 else None
            c_signed_norm = (float(signed) / denom) if denom > 0 else None
            rows.append(
                {
                    "setting_A": sa,
                    "setting_B": sb,
                    "singles_A": SA[sa],
                    "singles_B": SB[sb],
                    "coincidences": c,
                    "signed_sum_oa_ob": signed,
                    "C_norm": c_norm,
                    "C_signed_norm": c_signed_norm,
                }
            )

    return {
        "window": float(window),
        "pair_count": int(len(paired)),
        "dt_mean": float(np.mean(dts)) if dts else None,
        "dt_median": float(np.median(dts)) if dts else None,
        "singles_A": SA,
        "singles_B": SB,
        "cells": rows,
    }


def render_bridge_plot(report: Dict[str, object], out_png: str) -> None:
    strict = report["strict"]
    standard = report["standard"]
    s_cells = strict["cells"]
    w_cells = standard["cells"]
    labels = [f"{r['setting_A']}{r['setting_B']}" for r in s_cells]

    s_norm = [float(r["C_norm"] or 0.0) for r in s_cells]
    w_norm = [float(r["C_norm"] or 0.0) for r in w_cells]
    s_signed = [float(r["C_signed_norm"] or 0.0) for r in s_cells]
    w_signed = [float(r["C_signed_norm"] or 0.0) for r in w_cells]

    x = np.arange(len(labels), dtype=np.float64)
    bar_w = 0.20

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    fig.patch.set_facecolor("#0d1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#c9d1d9")
        for sp in ax.spines.values():
            sp.set_color("#30363d")
        ax.grid(True, axis="y", alpha=0.25, color="#30363d")

    ax1.bar(x - 1.5 * bar_w, s_norm, width=bar_w, color="#58a6ff", label="strict C_norm")
    ax1.bar(x - 0.5 * bar_w, w_norm, width=bar_w, color="#7ee787", label="standard C_norm")
    ax1.set_ylabel("C_norm", color="#c9d1d9")
    ax1.set_title("NCC denominator bridge: coincidences / sqrt(singles_A*singles_B)", color="white")
    ax1.legend(loc="upper right")

    ax2.bar(x + 0.5 * bar_w, s_signed, width=bar_w, color="#d2a8ff", label="strict C_signed_norm")
    ax2.bar(x + 1.5 * bar_w, w_signed, width=bar_w, color="#ffa657", label="standard C_signed_norm")
    ax2.set_ylabel("C_signed_norm", color="#c9d1d9")
    ax2.set_xlabel("setting pair (A,B)", color="#c9d1d9")
    ax2.legend(loc="upper right")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)

    note = report.get("note", "")
    fig.text(0.01, 0.01, str(note), color="#8b949e", fontsize=9)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    plt.savefig(out_png, dpi=160, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(
        description="Bridge NCC denominator to observable singles/coincidences."
    )
    ap.add_argument("--events-csv", default="", help="input events csv (side,t,setting,outcome)")
    ap.add_argument("--simulate", action="store_true", help="use simulated event stream instead of csv")
    ap.add_argument("--simulate-n", type=int, default=120000, help="simulated event count")
    ap.add_argument("--simulate-seed", type=int, default=77, help="simulated random seed")
    ap.add_argument("--window-strict", type=float, default=0.0, help="strict coincidence window")
    ap.add_argument("--window-standard", type=float, default=15.0, help="standard coincidence window")
    ap.add_argument("--out-json", default="", help="optional output json path")
    ap.add_argument("--out-png", default="", help="optional output figure path")
    args = ap.parse_args()

    if args.simulate:
        A, B = simulate_events(n=int(args.simulate_n), seed=int(args.simulate_seed))
        src = "simulated"
        csv_abs = ""
    else:
        if not args.events_csv:
            raise ValueError("pass --events-csv or use --simulate")
        if not os.path.isfile(args.events_csv):
            raise FileNotFoundError("events csv not found: %s" % args.events_csv)
        A, B = load_events_csv(args.events_csv)
        src = "events_csv"
        csv_abs = os.path.abspath(args.events_csv)

    strict_report = analyze_window(A, B, window=float(args.window_strict))
    standard_report = analyze_window(A, B, window=float(args.window_standard))

    report = {
        "source": src,
        "events_csv": csv_abs,
        "note": (
            "C_norm = coincidences / sqrt(singles_A * singles_B). "
            "This is an observability bridge for NCC denominator, not a CHSH identity."
        ),
        "strict": strict_report,
        "standard": standard_report,
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("wrote", args.out_json)
    if args.out_png:
        render_bridge_plot(report, args.out_png)
        print("saved", args.out_png)


if __name__ == "__main__":
    main()
