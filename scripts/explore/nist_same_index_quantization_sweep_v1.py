"""
nist_same_index_quantization_sweep_v1.py
----------------------------------------
Under fixed same-index pairing, sweep quantization levels from continuous to binary
and report how CHSH S changes.

This is used to test the claim "binarization causes the observed S-level".
"""

import argparse
import json
import os
from typing import Dict, List, Tuple

import h5py
import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


def slot_index_from_click_uint16(v: np.ndarray) -> np.ndarray:
    arr = v.astype(np.uint16)
    idx = np.full(arr.shape, -1, dtype=np.int16)
    nz = arr > 0
    bits = arr[nz].astype(np.uint32)
    k = np.floor(np.log2(bits)).astype(np.int16)
    valid = (1 << k) == bits
    out = np.full(bits.shape, -1, dtype=np.int16)
    out[valid] = k[valid]
    idx[nz] = out
    return idx


def load_same_index_arrays(hdf5_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5["alice/clicks"][()]
        cb = h5["bob/clicks"][()]
        sa = h5["alice/settings"][()]
        sb = h5["bob/settings"][()]

    m = (ca > 0) & (cb > 0) & ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2))
    s_a = sa[m].astype(np.int8) - 1
    s_b = sb[m].astype(np.int8) - 1
    ia = slot_index_from_click_uint16(ca[m])
    ib = slot_index_from_click_uint16(cb[m])
    ok = (ia >= 0) & (ib >= 0)
    s_a = s_a[ok]
    s_b = s_b[ok]
    ia = ia[ok]
    ib = ib[ok]

    # Continuous surrogate on 16-slot phase circle
    xa = np.cos(2.0 * np.pi * (ia.astype(np.float64) / 16.0))
    xb = np.cos(2.0 * np.pi * (ib.astype(np.float64) / 16.0))
    return s_a, s_b, xa, xb


def quantize_symmetric(x: np.ndarray, levels: int) -> np.ndarray:
    if levels <= 1:
        return np.zeros_like(x)
    if levels == 2:
        return np.where(x >= 0.0, 1.0, -1.0)
    # uniform bins in [-1, 1], mapped to bin centers
    edges = np.linspace(-1.0, 1.0, levels + 1)
    centers = (edges[:-1] + edges[1:]) * 0.5
    idx = np.digitize(x, edges[1:-1], right=False)
    return centers[idx]


def corr_raw(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.mean(x * y))


def corr_norm(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    num = float(np.mean(x * y))
    den = float(np.sqrt(max(1e-12, float(np.mean(x * x)) * float(np.mean(y * y)))))
    return num / den


def chsh_from_E(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def compute_E_by_cell(sa: np.ndarray, sb: np.ndarray, xa: np.ndarray, xb: np.ndarray, mode: str) -> Dict[str, float]:
    def m(a_set: int, b_set: int) -> np.ndarray:
        return (sa == a_set) & (sb == b_set)

    out: Dict[str, float] = {}
    for key, mask in {
        "ab": m(0, 0),
        "abp": m(0, 1),
        "apb": m(1, 0),
        "apbp": m(1, 1),
    }.items():
        x = xa[mask]
        y = xb[mask]
        out[key] = corr_norm(x, y) if mode == "norm" else corr_raw(x, y)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Same-index quantization sweep for CHSH")
    ap.add_argument(
        "--hdf5",
        default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
    )
    ap.add_argument("--levels", default="2,3,4,6,8,12,16,32", help="comma-separated quantization levels")
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v1.json",
    )
    ap.add_argument(
        "--out-png",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v1.png",
    )
    args = ap.parse_args()

    levels = [int(x.strip()) for x in args.levels.split(",") if x.strip()]
    sa, sb, xa, xb = load_same_index_arrays(args.hdf5)

    rows: List[Dict[str, float]] = []

    # reference: continuous (no quantization)
    E_raw_ref = compute_E_by_cell(sa, sb, xa, xb, mode="raw")
    E_norm_ref = compute_E_by_cell(sa, sb, xa, xb, mode="norm")
    rows.append(
        {
            "label": "continuous",
            "levels": 0,
            "S_raw": chsh_from_E(E_raw_ref),
            "S_norm": chsh_from_E(E_norm_ref),
        }
    )

    for lv in levels:
        qa = quantize_symmetric(xa, lv)
        qb = quantize_symmetric(xb, lv)
        E_raw = compute_E_by_cell(sa, sb, qa, qb, mode="raw")
        E_norm = compute_E_by_cell(sa, sb, qa, qb, mode="norm")
        rows.append(
            {
                "label": f"quant_{lv}",
                "levels": int(lv),
                "S_raw": chsh_from_E(E_raw),
                "S_norm": chsh_from_E(E_norm),
            }
        )

    out = {
        "version": "same-index-quantization-sweep-v1",
        "hdf5": os.path.abspath(args.hdf5),
        "pair_count": int(sa.size),
        "rows": rows,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    xs = np.arange(len(rows))
    y_raw = [r["S_raw"] for r in rows]
    y_norm = [r["S_norm"] for r in rows]
    labels = [r["label"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")
    ax.plot(xs, y_raw, marker="o", color="#58a6ff", linewidth=1.8, label="S_raw")
    ax.plot(xs, y_norm, marker="o", color="#7ee787", linewidth=1.8, label="S_norm")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=25, ha="right", color="#8b949e")
    ax.grid(True, alpha=0.25, color="#30363d")
    ax.set_title("Same-index CHSH vs quantization levels", color="white")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9)
    plt.tight_layout()
    os.makedirs(os.path.dirname(args.out_png), exist_ok=True)
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("pair_count =", sa.size)
    for r in rows:
        print(f"{r['label']}: S_raw={r['S_raw']:.6f} S_norm={r['S_norm']:.6f}")
    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
