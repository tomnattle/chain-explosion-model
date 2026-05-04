"""
nist_same_index_dual_metric_bridge_v1.py
----------------------------------------
Bridge two analysis lines on the same NIST data under fixed same-index pairing:
1) Binary CHSH (standard +/-1 outcomes)
2) Continuous normalized correlation CHSH (slot-derived continuous values)

This script is explicitly a bridge/audit tool.
"""

import argparse
import json
import os
from typing import Dict, Tuple

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


def bin_outcome_from_slot(slot_idx: np.ndarray) -> np.ndarray:
    # Pre-registered engineering mapping used in this repository:
    # slots 0..7 => +1, slots 8..15 => -1
    out = np.zeros(slot_idx.shape, dtype=np.int8)
    ok = slot_idx >= 0
    out[ok] = np.where(slot_idx[ok] <= 7, 1, -1)
    return out


def cont_value_from_slot(slot_idx: np.ndarray) -> np.ndarray:
    # Continuous surrogate from slot index on a 16-phase circle.
    # Range [-1,1], preserves slot geometry.
    out = np.zeros(slot_idx.shape, dtype=np.float64)
    ok = slot_idx >= 0
    phi = 2.0 * np.pi * (slot_idx[ok].astype(np.float64) / 16.0)
    out[ok] = np.cos(phi)
    return out


def corr_binary(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.mean(x * y))


def corr_cont_norm(x: np.ndarray, y: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    num = float(np.mean(x * y))
    dx = float(np.mean(x * x))
    dy = float(np.mean(y * y))
    den = float(np.sqrt(max(1e-12, dx * dy)))
    return num / den


def chsh(eab: float, eabp: float, eapb: float, eapbp: float) -> float:
    return float(eab + eabp + eapb - eapbp)


def theoretical_cos_map(a: float, ap: float, b: float, bp: float) -> Dict[str, float]:
    r = np.pi / 180.0
    return {
        "ab": float(-np.cos((a - b) * r)),
        "abp": float(-np.cos((a - bp) * r)),
        "apb": float(-np.cos((ap - b) * r)),
        "apbp": float(-np.cos((ap - bp) * r)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Same-index dual-metric bridge on NIST HDF5")
    ap.add_argument(
        "--hdf5",
        default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5",
    )
    ap.add_argument("--alice-clicks", default="alice/clicks")
    ap.add_argument("--bob-clicks", default="bob/clicks")
    ap.add_argument("--alice-settings", default="alice/settings")
    ap.add_argument("--bob-settings", default="bob/settings")
    ap.add_argument("--angle-a", type=float, default=0.0)
    ap.add_argument("--angle-ap", type=float, default=45.0)
    ap.add_argument("--angle-b", type=float, default=22.5)
    ap.add_argument("--angle-bp", type=float, default=67.5)
    ap.add_argument(
        "--out-json",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_dual_metric_bridge_v1.json",
    )
    ap.add_argument(
        "--out-png",
        default="battle_results/nist_clock_reference_audit_v1/results/same_index_dual_metric_bridge_v1.png",
    )
    args = ap.parse_args()

    with h5py.File(args.hdf5, "r") as h5:
        ca = h5[args.alice_clicks][()]
        cb = h5[args.bob_clicks][()]
        sa = h5[args.alice_settings][()]
        sb = h5[args.bob_settings][()]

    # same-index pair: both sides clicked at same grid index
    m = (ca > 0) & (cb > 0) & ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2))
    s_a = sa[m].astype(np.int8) - 1
    s_b = sb[m].astype(np.int8) - 1
    ia = slot_index_from_click_uint16(ca[m])
    ib = slot_index_from_click_uint16(cb[m])
    ok_slot = (ia >= 0) & (ib >= 0)

    s_a = s_a[ok_slot]
    s_b = s_b[ok_slot]
    ia = ia[ok_slot]
    ib = ib[ok_slot]

    out_a = bin_outcome_from_slot(ia).astype(np.int8)
    out_b = bin_outcome_from_slot(ib).astype(np.int8)
    x_a = cont_value_from_slot(ia)
    x_b = cont_value_from_slot(ib)

    def pick(a_set: int, b_set: int) -> np.ndarray:
        return (s_a == a_set) & (s_b == b_set)

    masks = {
        "ab": pick(0, 0),
        "abp": pick(0, 1),
        "apb": pick(1, 0),
        "apbp": pick(1, 1),
    }

    e_bin = {}
    e_con = {}
    counts = {}
    for k, mm in masks.items():
        e_bin[k] = corr_binary(out_a[mm], out_b[mm])
        e_con[k] = corr_cont_norm(x_a[mm], x_b[mm])
        counts[k] = int(np.sum(mm))

    s_bin = chsh(e_bin["ab"], e_bin["abp"], e_bin["apb"], e_bin["apbp"])
    s_con = chsh(e_con["ab"], e_con["abp"], e_con["apb"], e_con["apbp"])
    e_th = theoretical_cos_map(args.angle_a, args.angle_ap, args.angle_b, args.angle_bp)
    s_th = chsh(e_th["ab"], e_th["abp"], e_th["apb"], e_th["apbp"])

    out = {
        "version": "same-index-dual-metric-bridge-v1",
        "hdf5": os.path.abspath(args.hdf5),
        "pairing_mode": "same_index_only",
        "pair_count": int(out_a.size),
        "angles_deg": {
            "a": float(args.angle_a),
            "ap": float(args.angle_ap),
            "b": float(args.angle_b),
            "bp": float(args.angle_bp),
        },
        "counts_by_cell": counts,
        "E_binary": e_bin,
        "E_continuous_norm": e_con,
        "E_theory_neg_cos": e_th,
        "S_binary": float(s_bin),
        "S_continuous_norm": float(s_con),
        "S_theory_neg_cos": float(s_th),
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # plot: E comparison by setting pair
    labels = ["ab", "ab'", "a'b", "a'b'"]
    kkeys = ["ab", "abp", "apb", "apbp"]
    y_bin = [e_bin[k] for k in kkeys]
    y_con = [e_con[k] for k in kkeys]
    y_th = [e_th[k] for k in kkeys]

    x = np.arange(4)
    w = 0.25
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")
    ax.bar(x - w, y_bin, width=w, color="#58a6ff", label="binary E")
    ax.bar(x, y_con, width=w, color="#7ee787", label="continuous norm E")
    ax.bar(x + w, y_th, width=w, color="#ffa657", label="theory -cos E")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color="#8b949e")
    ax.set_ylim(-1.05, 1.05)
    ax.grid(True, axis="y", color="#30363d", alpha=0.25)
    ax.set_title("Same-index dual metric bridge", color="white")
    txt = "S_bin=%.6f | S_cont=%.6f | S_-cos=%.6f" % (s_bin, s_con, s_th)
    ax.text(0.02, 0.97, txt, transform=ax.transAxes, va="top", ha="left", color="#c9d1d9", fontsize=9)
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(args.out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)

    print("pair_count =", out_a.size)
    print("S_binary =", s_bin)
    print("S_continuous_norm =", s_con)
    print("S_theory_neg_cos =", s_th)
    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
