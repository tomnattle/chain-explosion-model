"""
nist_unified_semantics_audit_v2.py
----------------------------------
V2 fixes (from audit challenges):
1) Add official-like external clock pure bucket mode (no nearest matching).
2) Keep nearest modes as explicit loophole probes.
3) Split output between binary CHSH and continuous-correlation families.
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
            A.append(Event(float(i), s, 1 if k <= 7 else -1, float(np.cos(2.0 * np.pi * (k / 16.0)))))
        if sb[i] in (1, 2) and ib[i] >= 0:
            s = int(sb[i] - 1)
            k = int(ib[i])
            B.append(Event(float(i), s, 1 if k <= 7 else -1, float(np.cos(2.0 * np.pi * (k / 16.0)))))
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


def pair_external_clock_nearest_1to1(A: List[Event], B: List[Event], window: float) -> List[Tuple[Event, Event]]:
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


def E_from_pairs(pairs: List[Tuple[Event, Event]], metric: str) -> Dict[str, float]:
    if not pairs:
        return {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    ba = np.asarray([p[0].out_bin for p in pairs], dtype=np.float64)
    bb = np.asarray([p[1].out_bin for p in pairs], dtype=np.float64)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)

    def cell(a: int, b: int) -> np.ndarray:
        return (sa == a) & (sb == b)

    out = {}
    for key, m in {"ab": cell(0, 0), "abp": cell(0, 1), "apb": cell(1, 0), "apbp": cell(1, 1)}.items():
        if not np.any(m):
            out[key] = 0.0
            continue
        if metric == "binary":
            out[key] = float(np.mean(ba[m] * bb[m]))
        elif metric == "cont_raw":
            out[key] = float(np.mean(xa[m] * xb[m]))
        else:
            num = float(np.mean(xa[m] * xb[m]))
            den = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
            out[key] = num / den
    return out


def E_external_bucket_all(A: List[Event], B: List[Event], window: float, metric: str) -> Tuple[Dict[str, float], int]:
    # Pure bucket all-pairs counting (no nearest matching).
    if window <= 0:
        p = pair_same_index(A, B)
        return E_from_pairs(p, metric), len(p)

    bins_a: Dict[int, List[Event]] = {}
    bins_b: Dict[int, List[Event]] = {}
    for e in A:
        bi = int(np.floor(e.t / window))
        bins_a.setdefault(bi, []).append(e)
    for e in B:
        bi = int(np.floor(e.t / window))
        bins_b.setdefault(bi, []).append(e)

    # For each cell, accumulate pairwise sums and effective pair counts.
    sum_num = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sum_x2 = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sum_y2 = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    cnt = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    total_pairs = 0

    def key(a: int, b: int) -> str:
        if a == 0 and b == 0:
            return "ab"
        if a == 0 and b == 1:
            return "abp"
        if a == 1 and b == 0:
            return "apb"
        return "apbp"

    for bi, aa in bins_a.items():
        bb = bins_b.get(bi, [])
        if not bb:
            continue

        stats_a = {(0): [], (1): []}
        stats_b = {(0): [], (1): []}
        for e in aa:
            stats_a[e.setting].append(e)
        for e in bb:
            stats_b[e.setting].append(e)

        for sa in (0, 1):
            for sb in (0, 1):
                la = stats_a[sa]
                lb = stats_b[sb]
                if not la or not lb:
                    continue
                na = len(la)
                nb = len(lb)
                n_pairs = na * nb
                total_pairs += n_pairs
                k = key(sa, sb)

                if metric == "binary":
                    sum_a = float(np.sum([e.out_bin for e in la]))
                    sum_b = float(np.sum([e.out_bin for e in lb]))
                    sum_num[k] += sum_a * sum_b
                elif metric == "cont_raw":
                    sum_a = float(np.sum([e.x_cont for e in la]))
                    sum_b = float(np.sum([e.x_cont for e in lb]))
                    sum_num[k] += sum_a * sum_b
                else:
                    sum_a = float(np.sum([e.x_cont for e in la]))
                    sum_b = float(np.sum([e.x_cont for e in lb]))
                    sum_num[k] += sum_a * sum_b
                    sum_x2[k] += float(np.sum([e.x_cont * e.x_cont for e in la])) * nb
                    sum_y2[k] += float(np.sum([e.x_cont * e.x_cont for e in lb])) * na

                cnt[k] += float(n_pairs)

    E = {}
    for k in ("ab", "abp", "apb", "apbp"):
        if cnt[k] <= 0:
            E[k] = 0.0
            continue
        num_mean = sum_num[k] / cnt[k]
        if metric != "cont_norm":
            E[k] = float(num_mean)
        else:
            ex2 = sum_x2[k] / cnt[k]
            ey2 = sum_y2[k] / cnt[k]
            den = float(np.sqrt(max(1e-12, ex2 * ey2)))
            E[k] = float(num_mean / den)
    return E, int(total_pairs)


def S(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


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


def run_one(A: List[Event], B: List[Event], window: float) -> Dict[str, Dict[str, float]]:
    modes = {}
    p_same = pair_same_index(A, B)
    p_evt = pair_event_anchor_nearest(A, B, window)
    p_ext_n = pair_external_clock_nearest_1to1(A, B, window)

    # binary CHSH family
    modes["same_index"] = {
        "role": "baseline",
        "pair_count": len(p_same),
        "S_binary_chsh": S(E_from_pairs(p_same, "binary")),
        "S_cont_raw_corr": S(E_from_pairs(p_same, "cont_raw")),
        "S_cont_norm_corr": S(E_from_pairs(p_same, "cont_norm")),
    }
    E_ext_b, ext_cnt_b = E_external_bucket_all(A, B, window, "binary")
    E_ext_r, _ = E_external_bucket_all(A, B, window, "cont_raw")
    E_ext_n, _ = E_external_bucket_all(A, B, window, "cont_norm")
    modes["external_clock_bucket_all"] = {
        "role": "primary_external_clock",
        "pair_count": ext_cnt_b,
        "S_binary_chsh": S(E_ext_b),
        "S_cont_raw_corr": S(E_ext_r),
        "S_cont_norm_corr": S(E_ext_n),
    }
    modes["external_clock_nearest_1to1"] = {
        "role": "loophole_probe",
        "pair_count": len(p_ext_n),
        "S_binary_chsh": S(E_from_pairs(p_ext_n, "binary")),
        "S_cont_raw_corr": S(E_from_pairs(p_ext_n, "cont_raw")),
        "S_cont_norm_corr": S(E_from_pairs(p_ext_n, "cont_norm")),
    }
    modes["event_anchor_nearest"] = {
        "role": "loophole_probe",
        "pair_count": len(p_evt),
        "S_binary_chsh": S(E_from_pairs(p_evt, "binary")),
        "S_cont_raw_corr": S(E_from_pairs(p_evt, "cont_raw")),
        "S_cont_norm_corr": S(E_from_pairs(p_evt, "cont_norm")),
    }
    return modes


def plot_heatmap(modes: Dict[str, Dict[str, float]], out_png: str) -> None:
    order = ["same_index", "external_clock_bucket_all", "external_clock_nearest_1to1", "event_anchor_nearest"]
    metrics = ["S_binary_chsh", "S_cont_raw_corr", "S_cont_norm_corr"]
    vals = np.asarray([[modes[k][m] for m in metrics] for k in order], dtype=np.float64)
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    im = ax.imshow(vals, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(metrics, color="#8b949e")
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels(order, color="#8b949e")
    ax.set_title("V2 semantics matrix", color="white")
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            ax.text(j, i, f"{vals[i,j]:.3f}", ha="center", va="center", color="white", fontsize=9)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors="#8b949e")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST unified semantics audit v2")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--window", type=float, default=15.0)
    ap.add_argument("--seed", type=int, default=20260429)
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v2.json")
    ap.add_argument("--out-png", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_heatmap_v2.png")
    args = ap.parse_args()

    A, B = load_side_events_from_hdf5(args.hdf5)
    real = run_one(A, B, args.window)
    shuf = run_one(A, shuffled_B(B, args.seed), args.window)

    out = {
        "version": "nist-unified-semantics-audit-v2",
        "hdf5": os.path.abspath(args.hdf5),
        "window": float(args.window),
        "notes": {
            "binary_chsh": "Only this family is Bell-CHSH object.",
            "continuous_corr": "Diagnostic correlation family; not CHSH object.",
            "external_clock_bucket_all": "Primary external-clock semantics without nearest matching.",
            "nearest_modes": "Marked as loophole_probe.",
        },
        "real_modes": real,
        "counterfactual_shuffledB_modes": shuf,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    plot_heatmap(real, args.out_png)

    print("same_index S_binary_chsh =", real["same_index"]["S_binary_chsh"])
    print("external_bucket_all S_binary_chsh =", real["external_clock_bucket_all"]["S_binary_chsh"])
    print("external_nearest_1to1 S_binary_chsh =", real["external_clock_nearest_1to1"]["S_binary_chsh"])
    print("event_anchor S_binary_chsh =", real["event_anchor_nearest"]["S_binary_chsh"])
    print("saved:", args.out_json)
    print("saved:", args.out_png)


if __name__ == "__main__":
    main()
