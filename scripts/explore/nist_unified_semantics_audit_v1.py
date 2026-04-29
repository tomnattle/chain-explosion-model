"""
nist_unified_semantics_audit_v1.py
----------------------------------
Unified audit runner for:
1) metric effect (binary / cont_raw / cont_norm)
2) pairing effect (same_index / external_clock_bin / event_anchor_nearest)
3) angle/sign convention scan (on empirical E)
4) counterfactual injections (shuffled-B, synthetic-cos)
"""

import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import h5py
import matplotlib.pyplot as plt
import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")


@dataclass
class Event:
    t: float
    setting: int
    out_bin: int
    x_cont: float


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


def bin_outcome_from_slot(slot_idx: int) -> int:
    return 1 if slot_idx <= 7 else -1


def cont_value_from_slot(slot_idx: int) -> float:
    phi = 2.0 * np.pi * (float(slot_idx) / 16.0)
    return float(np.cos(phi))


def load_side_events_from_hdf5(hdf5_path: str) -> Tuple[List[Event], List[Event]]:
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5["alice/clicks"][()]
        cb = h5["bob/clicks"][()]
        sa = h5["alice/settings"][()]
        sb = h5["bob/settings"][()]

    ia = slot_index_from_click_uint16(ca)
    ib = slot_index_from_click_uint16(cb)
    A: List[Event] = []
    B: List[Event] = []
    n = int(ca.shape[0])
    for i in range(n):
        if sa[i] in (1, 2) and ia[i] >= 0:
            s = int(sa[i] - 1)
            k = int(ia[i])
            A.append(Event(float(i), s, bin_outcome_from_slot(k), cont_value_from_slot(k)))
        if sb[i] in (1, 2) and ib[i] >= 0:
            s = int(sb[i] - 1)
            k = int(ib[i])
            B.append(Event(float(i), s, bin_outcome_from_slot(k), cont_value_from_slot(k)))
    A.sort(key=lambda x: x.t)
    B.sort(key=lambda x: x.t)
    return A, B


def pair_same_index(A: List[Event], B: List[Event]) -> List[Tuple[Event, Event]]:
    from collections import defaultdict

    amap: Dict[float, List[Event]] = defaultdict(list)
    bmap: Dict[float, List[Event]] = defaultdict(list)
    for e in A:
        amap[e.t].append(e)
    for e in B:
        bmap[e.t].append(e)
    out: List[Tuple[Event, Event]] = []
    for t, la in amap.items():
        lb = bmap.get(t, [])
        n = min(len(la), len(lb))
        for i in range(n):
            out.append((la[i], lb[i]))
    return out


def pair_event_anchor_nearest(A: List[Event], B: List[Event], window: float) -> List[Tuple[Event, Event]]:
    used = np.zeros(len(B), dtype=np.bool_)
    out: List[Tuple[Event, Event]] = []
    j = 0
    for a in A:
        while j < len(B) and B[j].t < a.t - window:
            j += 1
        best_k = -1
        best_dt = None
        k = j
        while k < len(B) and B[k].t <= a.t + window:
            if not used[k]:
                dt = abs(B[k].t - a.t)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_k = k
            k += 1
        if best_k >= 0:
            used[best_k] = True
            out.append((a, B[best_k]))
    return out


def pair_external_clock_bin(A: List[Event], B: List[Event], window: float) -> List[Tuple[Event, Event]]:
    if window <= 0:
        return pair_same_index(A, B)
    bins_a: Dict[int, List[Tuple[int, Event]]] = {}
    bins_b: Dict[int, List[Tuple[int, Event]]] = {}
    for i, e in enumerate(A):
        bi = int(np.floor(e.t / window))
        bins_a.setdefault(bi, []).append((i, e))
    for i, e in enumerate(B):
        bi = int(np.floor(e.t / window))
        bins_b.setdefault(bi, []).append((i, e))
    used_b: Dict[int, bool] = {}
    out: List[Tuple[Event, Event]] = []
    for bi, aa in bins_a.items():
        bb = bins_b.get(bi, [])
        if not bb:
            continue
        for _, a in aa:
            best_j = -1
            best_dt = None
            best_b = None
            for jb, b in bb:
                if used_b.get(jb, False):
                    continue
                dt = abs(b.t - a.t)
                if best_dt is None or dt < best_dt:
                    best_dt = dt
                    best_j = jb
                    best_b = b
            if best_j >= 0 and best_b is not None:
                used_b[best_j] = True
                out.append((a, best_b))
    return out


def cell_masks(pairs: List[Tuple[Event, Event]]) -> Dict[str, np.ndarray]:
    if not pairs:
        z = np.zeros(0, dtype=np.bool_)
        return {"ab": z, "abp": z, "apb": z, "apbp": z}
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    return {
        "ab": (sa == 0) & (sb == 0),
        "abp": (sa == 0) & (sb == 1),
        "apb": (sa == 1) & (sb == 0),
        "apbp": (sa == 1) & (sb == 1),
    }


def metric_values(pairs: List[Tuple[Event, Event]], metric: str) -> Dict[str, float]:
    if not pairs:
        return {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)
    ba = np.asarray([p[0].out_bin for p in pairs], dtype=np.float64)
    bb = np.asarray([p[1].out_bin for p in pairs], dtype=np.float64)
    masks = cell_masks(pairs)
    out = {}
    for k, m in masks.items():
        if not np.any(m):
            out[k] = 0.0
            continue
        if metric == "binary":
            out[k] = float(np.mean(ba[m] * bb[m]))
        elif metric == "cont_raw":
            out[k] = float(np.mean(xa[m] * xb[m]))
        else:
            num = float(np.mean(xa[m] * xb[m]))
            den = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
            out[k] = num / den
    return out


def s_from_e(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def chsh_coeff_vectors() -> List[np.ndarray]:
    out = []
    for mask in range(16):
        signs = []
        neg = 0
        for i in range(4):
            if (mask >> i) & 1:
                signs.append(-1.0)
                neg += 1
            else:
                signs.append(1.0)
        if neg % 2 == 1:
            out.append(np.asarray(signs, dtype=np.float64))
    return out


def max_abs_chsh_equiv(E: Dict[str, float]) -> float:
    v = np.asarray([E["ab"], E["abp"], E["apb"], E["apbp"]], dtype=np.float64)
    m = 0.0
    for c in chsh_coeff_vectors():
        m = max(m, abs(float(np.dot(c, v))))
    return float(m)


def shuffled_B(B: List[Event], seed: int) -> List[Event]:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(B))
    rng.shuffle(idx)
    out = []
    for i, j in enumerate(idx):
        b = B[i]
        src = B[int(j)]
        out.append(Event(b.t, b.setting, src.out_bin, src.x_cont))
    return out


def synthetic_cos_events(n_trials: int, seed: int) -> Tuple[List[Event], List[Event]]:
    rng = np.random.default_rng(seed)
    a, ap, b, bp = 0.0, np.pi / 4.0, np.pi / 8.0, -np.pi / 8.0
    lam = rng.uniform(0.0, 2.0 * np.pi, size=n_trials)
    set_a = rng.integers(0, 2, size=n_trials)
    set_b = rng.integers(0, 2, size=n_trials)
    th_a = np.where(set_a == 0, a, ap)
    th_b = np.where(set_b == 0, b, bp)
    xa = np.cos(lam - th_a)
    xb = -np.cos(lam - th_b)
    A = [Event(float(i), int(set_a[i]), 1 if xa[i] >= 0 else -1, float(xa[i])) for i in range(n_trials)]
    B = [Event(float(i), int(set_b[i]), 1 if xb[i] >= 0 else -1, float(xb[i])) for i in range(n_trials)]
    return A, B


def run_matrix(A: List[Event], B: List[Event], window: float) -> Dict[str, Dict[str, float]]:
    pairings = {
        "same_index": pair_same_index(A, B),
        "external_clock_bin": pair_external_clock_bin(A, B, window),
        "event_anchor_nearest": pair_event_anchor_nearest(A, B, window),
    }
    metrics = ["binary", "cont_raw", "cont_norm"]
    out: Dict[str, Dict[str, float]] = {}
    for p_name, pairs in pairings.items():
        row = {"pair_count": float(len(pairs))}
        for m in metrics:
            E = metric_values(pairs, m)
            row[f"S_{m}"] = s_from_e(E)
            row[f"Smax_{m}"] = max_abs_chsh_equiv(E)
        out[p_name] = row
    return out


def plot_matrix(real_m: Dict[str, Dict[str, float]], out_png: str) -> None:
    pairings = ["same_index", "external_clock_bin", "event_anchor_nearest"]
    metrics = ["binary", "cont_raw", "cont_norm"]
    vals = np.zeros((len(pairings), len(metrics)), dtype=np.float64)
    for i, p in enumerate(pairings):
        for j, m in enumerate(metrics):
            vals[i, j] = real_m[p][f"S_{m}"]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    im = ax.imshow(vals, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(metrics, color="#8b949e")
    ax.set_yticks(np.arange(len(pairings)))
    ax.set_yticklabels(pairings, color="#8b949e")
    ax.set_title("S by pairing x metric (real data)", color="white")
    for i in range(len(pairings)):
        for j in range(len(metrics)):
            ax.text(j, i, f"{vals[i,j]:.3f}", ha="center", va="center", color="white", fontsize=9)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors="#8b949e")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)


def plot_counterfactual(real_m: Dict[str, Dict[str, float]], shuf_m: Dict[str, Dict[str, float]], syn_m: Dict[str, Dict[str, float]], out_png: str) -> None:
    key = "S_binary"
    pairings = ["same_index", "external_clock_bin", "event_anchor_nearest"]
    xr = np.arange(len(pairings))
    rv = [real_m[p][key] for p in pairings]
    sv = [shuf_m[p][key] for p in pairings]
    yv = [syn_m[p][key] for p in pairings]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#8b949e")
    for sp in ax.spines.values():
        sp.set_color("#30363d")
    w = 0.25
    ax.bar(xr - w, rv, width=w, color="#58a6ff", label="real")
    ax.bar(xr, sv, width=w, color="#ff7b72", label="shuffled-B")
    ax.bar(xr + w, yv, width=w, color="#7ee787", label="synthetic-cos")
    ax.set_xticks(xr)
    ax.set_xticklabels(pairings, color="#8b949e")
    ax.set_ylabel("S_binary", color="#8b949e")
    ax.set_title("Counterfactual comparison", color="white")
    ax.grid(True, axis="y", alpha=0.25, color="#30363d")
    ax.legend(facecolor="#161b22", edgecolor="#30363d", framealpha=0.9, fontsize=9)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Unified semantics audit")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--window", type=float, default=15.0)
    ap.add_argument("--synthetic-n", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=20260429)
    ap.add_argument("--target-s", type=float, default=2.82)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v1.json")
    ap.add_argument("--out-heatmap", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_heatmap_v1.png")
    ap.add_argument("--out-counterfactual", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_counterfactual_v1.png")
    args = ap.parse_args()

    A, B = load_side_events_from_hdf5(args.hdf5)
    real_m = run_matrix(A, B, args.window)
    shuf_m = run_matrix(A, shuffled_B(B, args.seed), args.window)
    sA, sB = synthetic_cos_events(args.synthetic_n, args.seed + 1)
    syn_m = run_matrix(sA, sB, args.window)

    # angle/sign scan result on same_index, binary + cont_norm
    same_pairs = pair_same_index(A, B)
    E_bin = metric_values(same_pairs, "binary")
    E_con = metric_values(same_pairs, "cont_norm")
    smax_bin = max_abs_chsh_equiv(E_bin)
    smax_con = max_abs_chsh_equiv(E_con)

    out = {
        "version": "nist-unified-semantics-audit-v1",
        "hdf5": os.path.abspath(args.hdf5),
        "window": float(args.window),
        "target_s": float(args.target_s),
        "tol": float(args.tol),
        "real_matrix": real_m,
        "counterfactual_shuffledB_matrix": shuf_m,
        "counterfactual_synthetic_cos_matrix": syn_m,
        "same_index_angle_sign_scan": {
            "Smax_binary_equiv": smax_bin,
            "Smax_cont_norm_equiv": smax_con,
            "near_target_binary": bool(abs(smax_bin - args.target_s) <= args.tol),
            "near_target_cont_norm": bool(abs(smax_con - args.target_s) <= args.tol),
            "E_binary": E_bin,
            "E_cont_norm": E_con,
        },
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    plot_matrix(real_m, args.out_heatmap)
    plot_counterfactual(real_m, shuf_m, syn_m, args.out_counterfactual)

    print("real same_index S_binary =", real_m["same_index"]["S_binary"])
    print("real same_index S_cont_norm =", real_m["same_index"]["S_cont_norm"])
    print("same_index Smax binary equiv =", smax_bin)
    print("same_index Smax cont_norm equiv =", smax_con)
    print("saved:", args.out_json)
    print("saved:", args.out_heatmap)
    print("saved:", args.out_counterfactual)


if __name__ == "__main__":
    main()
