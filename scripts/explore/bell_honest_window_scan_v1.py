#!/usr/bin/env python3
"""
Bell Honest Window Scan — v1

PURPOSE
-------
Audit whether the standard coincidence window (15.0 in Round 1, 10.0 in Round 2)
was cherry-picked to maximize S.

Scans window values from 0 to 20 in steps of 0.5, computes S at each,
and reports whether the chosen windows happen to be near-maxima.

ANTI-CHEAT
----------
- No existing files are modified.
- The window range and step are fixed BEFORE running (logged in PREREG).
- All window results are saved unconditionally — no suppression.
- If S peaks at exactly window=15 or window=10, that is reported honestly.
- If S peaks elsewhere, that is also reported honestly.
- The script does NOT decide whether cherry-picking occurred —
  it only provides the data needed to make that judgment.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "bell_window_scan_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EVENTS_CSV = ROOT / "data" / "nist_completeblind_side_streams.csv"

# ── Preregistered scan parameters (fixed before running) ──────────────────
WINDOW_MIN  = 0.0
WINDOW_MAX  = 20.0
WINDOW_STEP = 0.5

# Windows used in actual rounds (to check against scan)
ROUND1_STANDARD_WINDOW = 15.0
ROUND2_STANDARD_WINDOW = 10.0
STRICT_WINDOW = 0.0   # same in both rounds

PREREG = {
    "scan": "bell_honest_window_scan_v1",
    "window_min": WINDOW_MIN,
    "window_max": WINDOW_MAX,
    "window_step": WINDOW_STEP,
    "windows_under_audit": {
        "round1_standard": ROUND1_STANDARD_WINDOW,
        "round2_standard": ROUND2_STANDARD_WINDOW,
        "strict_both_rounds": STRICT_WINDOW,
    },
    "anti_cheat": (
        "All parameters above are logged before data is read. "
        "No window can be added or removed after seeing results."
    ),
}

(OUT_DIR / "PREREG_V1.json").write_text(
    json.dumps(PREREG, indent=2), encoding="utf-8"
)


def load_events() -> tuple[list, list]:
    A, B = [], []
    with open(EVENTS_CSV, encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            side = str(row["side"]).strip().upper()
            t = float(row["t"])
            s = int(row["setting"])
            o = int(row["outcome"])
            o_bin = 1 if o >= 0 else -1
            if side == "A":
                A.append((t, s, o_bin))
            elif side == "B":
                B.append((t, s, o_bin))
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])
    return A, B


def pair_events(A: list, B: list, window: float) -> list:
    import numpy as np
    paired = []
    used_b = [False] * len(B)
    j = 0
    for ta, sa, oa in A:
        while j < len(B) and B[j][0] < ta - window:
            j += 1
        best_k, best_dt = -1, None
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
            paired.append((sa, B[best_k][1], oa, B[best_k][2]))
    return paired


def compute_S(paired: list) -> tuple[float, int, dict]:
    import numpy as np
    if not paired:
        return float("nan"), 0, {}
    arr = np.array(paired, dtype=np.int64)
    ab = arr[:, 2] * arr[:, 3]
    def m(mask):
        return float(np.mean(ab[mask])) if np.any(mask) else float("nan")
    Eab   = m((arr[:,0]==0) & (arr[:,1]==0))
    Eabp  = m((arr[:,0]==0) & (arr[:,1]==1))
    Eapb  = m((arr[:,0]==1) & (arr[:,1]==0))
    Eapbp = m((arr[:,0]==1) & (arr[:,1]==1))
    S = Eab + Eabp + Eapb - Eapbp
    return S, len(paired), {"Eab": Eab, "Eabp": Eabp, "Eapb": Eapb, "Eapbp": Eapbp}


def main() -> int:
    import numpy as np

    if not EVENTS_CSV.exists():
        print(f"ERROR: NIST CSV not found: {EVENTS_CSV}", file=sys.stderr)
        return 1

    print("Loading NIST events ...", file=sys.stderr)
    A, B = load_events()
    print(f"  Alice: {len(A)} events, Bob: {len(B)} events", file=sys.stderr)

    # Build window list
    windows = []
    w = WINDOW_MIN
    while w <= WINDOW_MAX + 1e-9:
        windows.append(round(w, 10))
        w += WINDOW_STEP

    print(f"Scanning {len(windows)} windows from {WINDOW_MIN} to {WINDOW_MAX} ...",
          file=sys.stderr)

    records = []
    for w in windows:
        paired = pair_events(A, B, w)
        S, n, Es = compute_S(paired)
        record = {
            "window": w,
            "pair_count": n,
            "S": round(S, 8) if not (S != S) else None,
            **{k: round(v, 8) if not (v != v) else None for k, v in Es.items()},
            "is_round1_standard": abs(w - ROUND1_STANDARD_WINDOW) < 1e-9,
            "is_round2_standard": abs(w - ROUND2_STANDARD_WINDOW) < 1e-9,
            "is_strict": abs(w - STRICT_WINDOW) < 1e-9,
        }
        records.append(record)
        if record["is_round1_standard"] or record["is_round2_standard"] or record["is_strict"]:
            print(f"  window={w:.1f} -> S={S:.6f}, pairs={n}  <- AUDITED WINDOW",
                  file=sys.stderr)
        elif int(w) == w:  # print integers only for progress
            print(f"  window={w:.1f} -> S={S:.6f}, pairs={n}", file=sys.stderr)

    # ── Analysis ───────────────────────────────────────────────────────────
    valid_records = [r for r in records if r["S"] is not None]
    S_values = [r["S"] for r in valid_records]
    all_windows = [r["window"] for r in valid_records]

    S_max = max(S_values)
    S_min = min(S_values)
    S_at_r1 = next((r["S"] for r in records if r["is_round1_standard"]), None)
    S_at_r2 = next((r["S"] for r in records if r["is_round2_standard"]), None)
    S_at_strict = next((r["S"] for r in records if r["is_strict"]), None)

    # Window(s) where S is maximized
    max_windows = [r["window"] for r in valid_records if abs(r["S"] - S_max) < 1e-8]

    # Rank of the audited windows in the S distribution
    S_sorted = sorted(S_values, reverse=True)
    rank_r1 = S_sorted.index(S_at_r1) + 1 if S_at_r1 is not None else None
    rank_r2 = S_sorted.index(S_at_r2) + 1 if S_at_r2 is not None else None

    analysis = {
        "S_at_strict_window_0": S_at_strict,
        "S_at_round1_standard_window_15": S_at_r1,
        "S_at_round2_standard_window_10": S_at_r2,
        "S_max_across_all_windows": S_max,
        "S_max_at_windows": max_windows,
        "S_min_across_all_windows": S_min,
        "total_windows_scanned": len(windows),
        "rank_of_round1_window_by_S": rank_r1,
        "rank_of_round2_window_by_S": rank_r2,
        "rank_interpretation": (
            f"Round1 window (w=15) ranks #{rank_r1} out of {len(valid_records)} windows by S value. "
            f"Round2 window (w=10) ranks #{rank_r2} out of {len(valid_records)} windows by S value. "
            f"S_max occurs at windows={max_windows}."
        ),
        "cherry_pick_verdict": (
            "CANNOT DETERMINE automatically. See rank above: "
            "if the chosen windows rank near the top, cherry-picking is plausible. "
            "If they rank in the middle or bottom, cherry-picking is unlikely."
        ),
    }

    payload = {
        "prereg": PREREG,
        "analysis": analysis,
        "records": records,
    }

    json_path = OUT_DIR / "WINDOW_SCAN_V1.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # CSV
    csv_lines = ["window,pair_count,S,Eab,Eabp,Eapb,Eapbp,is_audited_window"]
    for r in records:
        audited = "YES" if r["is_round1_standard"] or r["is_round2_standard"] or r["is_strict"] else ""
        csv_lines.append(
            f"{r['window']},{r['pair_count']},{r['S']},{r.get('Eab','')},{r.get('Eabp','')},{r.get('Eapb','')},{r.get('Eapbp','')},{audited}"
        )
    (OUT_DIR / "WINDOW_SCAN_V1.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    # Plot
    try:
        import os
        os.environ.setdefault("MPLBACKEND", "Agg")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(all_windows, S_values, color="#4c72b0", lw=1.4, label="S vs window")
        ax.axhline(2.0,       color="#999999", ls="--", lw=1.0, label="LHV bound = 2")
        ax.axhline(2.0*2**0.5, color="#dd8452", ls="--", lw=1.0, label="Tsirelson = 2√2 ≈ 2.828")
        if S_at_r1 is not None:
            ax.axvline(ROUND1_STANDARD_WINDOW, color="#55a868", ls=":", lw=1.2,
                       label=f"Round1 window={ROUND1_STANDARD_WINDOW} (S={S_at_r1:.4f})")
        if S_at_r2 is not None:
            ax.axvline(ROUND2_STANDARD_WINDOW, color="#c44e52", ls=":", lw=1.2,
                       label=f"Round2 window={ROUND2_STANDARD_WINDOW} (S={S_at_r2:.4f})")
        ax.set_xlabel("Coincidence window (index units)")
        ax.set_ylabel("CHSH S value")
        ax.set_title("Bell Honest Window Scan v1\nS vs coincidence window — all values shown")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT_DIR / "WINDOW_SCAN_V1.png", dpi=160)
        plt.close(fig)
        print(f"Plot saved.", file=sys.stderr)
    except Exception as e:
        print(f"Plot failed: {e}", file=sys.stderr)

    # Markdown
    md = [
        "# Bell Honest Window Scan v1",
        "",
        "**Audit question:** Were the standard windows (15.0 and 10.0) cherry-picked to maximize S?",
        "",
        "## Key Results",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| S at strict window (0) | {S_at_strict:.6f} |",
        f"| S at Round1 standard window (15) | {S_at_r1:.6f} |",
        f"| S at Round2 standard window (10) | {S_at_r2:.6f} |",
        f"| S_max across all {len(windows)} windows | {S_max:.6f} |",
        f"| Window(s) where S is max | {max_windows} |",
        f"| Rank of Round1 window by S | #{rank_r1} of {len(valid_records)} |",
        f"| Rank of Round2 window by S | #{rank_r2} of {len(valid_records)} |",
        "",
        "## Interpretation",
        "",
        analysis["rank_interpretation"],
        "",
        f"> {analysis['cherry_pick_verdict']}",
        "",
        "## Note on S trend",
        "",
        "If S increases monotonically with window size, then ANY large window will give high S.",
        "In that case, choosing window=15 gives a high S not because it was cherry-picked",
        "at the peak, but because larger windows systematically include more pairs with",
        "higher apparent correlation. This is the coincidence loophole — and it is",
        "exactly what the Bell paper reports as its core finding.",
    ]

    (OUT_DIR / "WINDOW_SCAN_V1.md").write_text("\n".join(md), encoding="utf-8")

    # Console
    print(f"\n=== Bell Window Scan v1 ===")
    print(f"  S at strict (w=0):  {S_at_strict:.6f}")
    print(f"  S at R1 std (w=15): {S_at_r1:.6f}  [rank #{rank_r1}/{len(valid_records)}]")
    print(f"  S at R2 std (w=10): {S_at_r2:.6f}  [rank #{rank_r2}/{len(valid_records)}]")
    print(f"  S_max: {S_max:.6f} at windows={max_windows}")
    print(f"\nArtifacts: {OUT_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
