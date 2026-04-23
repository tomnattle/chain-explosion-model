"""
NIST side-stream phase diagram over:
  pairing window x outcome gauge-mapping

Gauge mappings are setting-conditional sign flips that preserve CHSH algebraic form,
used here as a robustness probe of pipeline conventions.
"""

import argparse
import csv
import math
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


Row = Tuple[float, int, int]  # t, setting, outcome(+/-1)


def pair_events(a_rows: List[Row], b_rows: List[Row], window: float) -> List[Tuple[Row, Row]]:
    i = 0
    j = 0
    pairs: List[Tuple[Row, Row]] = []
    while i < len(a_rows) and j < len(b_rows):
        ta = a_rows[i][0]
        tb = b_rows[j][0]
        dt = tb - ta
        if abs(dt) <= window:
            pairs.append((a_rows[i], b_rows[j]))
            i += 1
            j += 1
        elif tb < ta - window:
            j += 1
        else:
            i += 1
    return pairs


def chsh_s(pairs: List[Tuple[Row, Row]], gauge_fn: Callable[[str, int, int], int]) -> float:
    cells: Dict[Tuple[int, int], List[int]] = {(0, 0): [], (0, 1): [], (1, 0): [], (1, 1): []}
    for a, b in pairs:
        sa, oa = a[1], a[2]
        sb, ob = b[1], b[2]
        oa2 = gauge_fn("A", sa, oa)
        ob2 = gauge_fn("B", sb, ob)
        cells[(sa, sb)].append(oa2 * ob2)
    e = {}
    for key, vals in cells.items():
        if not vals:
            return float("nan")
        e[key] = float(np.mean(vals))
    return e[(0, 0)] + e[(0, 1)] + e[(1, 0)] - e[(1, 1)]


def get_gauges() -> Dict[str, Callable[[str, int, int], int]]:
    def identity(side: str, setting: int, out: int) -> int:
        return out

    def flip_a1(side: str, setting: int, out: int) -> int:
        return -out if (side == "A" and setting == 1) else out

    def flip_b1(side: str, setting: int, out: int) -> int:
        return -out if (side == "B" and setting == 1) else out

    def flip_a1_b1(side: str, setting: int, out: int) -> int:
        if (side == "A" and setting == 1) or (side == "B" and setting == 1):
            return -out
        return out

    def flip_all_a(side: str, setting: int, out: int) -> int:
        return -out if side == "A" else out

    def flip_all_b(side: str, setting: int, out: int) -> int:
        return -out if side == "B" else out

    return {
        "identity": identity,
        "flip_A_setting1": flip_a1,
        "flip_B_setting1": flip_b1,
        "flip_A1_B1": flip_a1_b1,
        "flip_all_A": flip_all_a,
        "flip_all_B": flip_all_b,
    }


def load_side_stream(path: Path) -> Tuple[List[Row], List[Row]]:
    a_rows: List[Row] = []
    b_rows: List[Row] = []
    with path.open("r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            side = row["side"].strip().upper()
            t = float(row["t"])
            setting = int(row["setting"])
            out = 1 if int(row["outcome"]) >= 0 else -1
            r = (t, setting, out)
            if side == "A":
                a_rows.append(r)
            elif side == "B":
                b_rows.append(r)
    a_rows.sort(key=lambda x: x[0])
    b_rows.sort(key=lambda x: x[0])
    return a_rows, b_rows


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST window x gauge mapping phase diagram")
    ap.add_argument("--csv", default="data/nist_completeblind_side_streams.csv")
    ap.add_argument("--windows", default="0,1,2,5,10,15")
    ap.add_argument("--out-png", default="artifacts/public_validation_pack/fig6_nist_window_mapping_phase_diagram.png")
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_WINDOW_MAPPING_PHASE_DIAGRAM.md")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"missing csv: {csv_path}")

    windows = [float(x.strip()) for x in args.windows.split(",") if x.strip()]
    gauges = get_gauges()
    gauge_names = list(gauges.keys())

    a_rows, b_rows = load_side_stream(csv_path)

    s_mat = np.zeros((len(gauge_names), len(windows)), dtype=np.float64)
    n_pairs = np.zeros(len(windows), dtype=np.int64)

    for wi, w in enumerate(windows):
        pairs = pair_events(a_rows, b_rows, w)
        n_pairs[wi] = len(pairs)
        for gi, gname in enumerate(gauge_names):
            s_mat[gi, wi] = chsh_s(pairs, gauges[gname])

    # Heatmap
    out_png = Path(args.out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=170)
    im = ax.imshow(s_mat, aspect="auto", cmap="coolwarm", vmin=np.nanmin(s_mat), vmax=np.nanmax(s_mat))
    ax.set_xticks(np.arange(len(windows)))
    ax.set_xticklabels([str(w) for w in windows])
    ax.set_yticks(np.arange(len(gauge_names)))
    ax.set_yticklabels(gauge_names)
    ax.set_xlabel("pairing window")
    ax.set_ylabel("outcome gauge mapping")
    ax.set_title("NIST side-stream phase diagram: S(window, gauge)")
    for i in range(len(gauge_names)):
        for j in range(len(windows)):
            ax.text(j, i, f"{s_mat[i, j]:.3f}", ha="center", va="center", color="black", fontsize=7.5)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("CHSH S")
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST window × gauge-mapping 相图\n\n")
        f.write(f"- 数据: `{csv_path.as_posix()}`\n")
        f.write(f"- windows: `{windows}`\n")
        f.write(f"- gauge mappings: `{', '.join(gauge_names)}`\n")
        f.write(f"- 图像: `{out_png.as_posix()}`\n\n")
        f.write("## 配对规模\n\n")
        for w, n in zip(windows, n_pairs):
            f.write(f"- window={w}: paired events={int(n)}\n")
        f.write("\n## S 值矩阵\n\n")
        f.write("| gauge \\\\ window | " + " | ".join(str(w) for w in windows) + " |\n")
        f.write("|---|" + "|".join(["---:"] * len(windows)) + "|\n")
        for gi, gname in enumerate(gauge_names):
            vals = " | ".join(f"{s_mat[gi, wi]:.6f}" for wi in range(len(windows)))
            f.write(f"| {gname} | {vals} |\n")
        f.write("\n")
        f.write("## 读取建议\n\n")
        f.write("- 观察同一行随 window 的变化，判断配对窗口敏感性。\n")
        f.write("- 观察同一列随 gauge 的变化，判断编码约定敏感性。\n")
        f.write("- 若两向都敏感，说明当前结论仍依赖分析管线细节。\n")

    print("wrote", out_png)
    print("wrote", out_md)


if __name__ == "__main__":
    main()
