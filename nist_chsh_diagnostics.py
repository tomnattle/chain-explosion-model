"""
nist_chsh_diagnostics.py
------------------------
对事件 CSV 做标准化检验：边际分布、setting 平衡、粗粒度 no-signalling 提示量。
不改动数据；输出 JSON 供 round2 归档。
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter

import numpy as np


def load_rows(path, fields):
    rows = {"A": [], "B": []}
    with open(path, "r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        need = {fields["side"], fields["time"], fields["setting"], fields["outcome"]}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError("missing columns: %s" % sorted(need))
        for row in rd:
            side = str(row[fields["side"]]).strip().upper()
            if side not in ("A", "B"):
                continue
            t = float(row[fields["time"]])
            s = int(row[fields["setting"]])
            o = 1 if int(row[fields["outcome"]]) >= 0 else -1
            if s not in (0, 1):
                continue
            rows[side].append((t, s, o))
    return rows


def marginal_stats(tuples, label):
    if not tuples:
        return {label + "_n": 0}
    s = np.array([x[1] for x in tuples], dtype=np.int32)
    o = np.array([x[2] for x in tuples], dtype=np.int32)
    t = np.array([x[0] for x in tuples], dtype=np.float64)
    return {
        label + "_n": int(len(tuples)),
        label + "_P_setting0": float(np.mean(s == 0)),
        label + "_P_outcome_plus": float(np.mean(o == 1)),
        label + "_t_min": float(np.min(t)),
        label + "_t_max": float(np.max(t)),
    }


def paired_cells_from_lists(A, B, window):
    """Reuse pairing from alignment script."""
    from explore_chsh_experiment_alignment import pair_events

    paired, dt = pair_events(A, B, window=float(window))
    cells = Counter()
    for sa, sb, oa, ob in paired:
        cells[(int(sa), int(sb), int(oa), int(ob))] += 1
    return {
        "window": float(window),
        "pair_count": len(paired),
        "dt_mean": float(np.mean(dt)) if len(dt) else None,
        "dt_median": float(np.median(dt)) if len(dt) else None,
        "cell_counts_sample": {str(k): int(v) for k, v in cells.most_common(12)},
    }


def main():
    ap = argparse.ArgumentParser(description="CHSH-oriented CSV diagnostics for NIST pipeline")
    ap.add_argument("--events-csv", required=True)
    ap.add_argument("--out-json", default="")
    ap.add_argument("--window-strict", type=float, default=0.0)
    ap.add_argument("--window-standard", type=float, default=15.0)
    args = ap.parse_args()

    fields = {"side": "side", "time": "t", "setting": "setting", "outcome": "outcome"}
    raw = load_rows(args.events_csv, fields)
    A, B = raw["A"], raw["B"]
    A.sort(key=lambda x: x[0])
    B.sort(key=lambda x: x[0])

    report = {
        "events_csv": os.path.abspath(args.events_csv),
        "marginals": {
            "A": marginal_stats(A, "A"),
            "B": marginal_stats(B, "B"),
        },
        "paired": {
            "strict": paired_cells_from_lists(A, B, args.window_strict),
            "standard": paired_cells_from_lists(A, B, args.window_standard),
        },
        "note": "Rough balance only; formal tests need preregistered hypotheses.",
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("wrote", args.out_json, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
