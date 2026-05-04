"""
nist_unified_semantics_audit_v4.py
----------------------------------
V4 hardening for challenge items:
- F1: external bucket edge sensitivity (offset scan)
- F2: strict same-index mode (drop multi-event timestamps)
- F3: bootstrap CI integrated for key binary CHSH outputs
- F4: fixed_den split (train/test style) to reduce leakage concern
- F5: anchor symmetry check (A-anchor vs B-anchor)
"""

import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import h5py
import numpy as np


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


def load_side_events_from_hdf5(hdf5_path: str) -> Tuple[List[Event], List[Event], Dict[str, float]]:
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5["alice/clicks"][()]
        cb = h5["bob/clicks"][()]
        sa = h5["alice/settings"][()]
        sb = h5["bob/settings"][()]
    ia = slot_index_from_click_uint16(ca)
    ib = slot_index_from_click_uint16(cb)

    pre_a = (ca > 0) & ((sa == 1) | (sa == 2))
    pre_b = (cb > 0) & ((sb == 1) | (sb == 2))
    post_a = pre_a & (ia >= 0)
    post_b = pre_b & (ib >= 0)
    diag = {
        "pre_filter_A_events": int(np.sum(pre_a)),
        "pre_filter_B_events": int(np.sum(pre_b)),
        "post_filter_A_events": int(np.sum(post_a)),
        "post_filter_B_events": int(np.sum(post_b)),
        "drop_ratio_A": float(1.0 - np.sum(post_a) / max(1, np.sum(pre_a))),
        "drop_ratio_B": float(1.0 - np.sum(post_b) / max(1, np.sum(pre_b))),
    }

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
    return A, B, diag


def build_time_maps(events: List[Event]) -> Dict[float, List[Event]]:
    from collections import defaultdict

    m = defaultdict(list)
    for e in events:
        m[e.t].append(e)
    return m


def pair_same_index(A: List[Event], B: List[Event], drop_multi_t: bool = False) -> List[Tuple[Event, Event]]:
    amap = build_time_maps(A)
    bmap = build_time_maps(B)
    out: List[Tuple[Event, Event]] = []
    for t, la in amap.items():
        lb = bmap.get(t, [])
        if not lb:
            continue
        if drop_multi_t and (len(la) > 1 or len(lb) > 1):
            continue
        n = min(len(la), len(lb))
        for i in range(n):
            out.append((la[i], lb[i]))
    return out


def same_index_multi_diag(A: List[Event], B: List[Event]) -> Dict[str, float]:
    amap = build_time_maps(A)
    bmap = build_time_maps(B)
    shared = set(amap.keys()) & set(bmap.keys())
    if not shared:
        return {"shared_t_count": 0, "multi_event_t_count": 0, "multi_event_t_rate": 0.0}
    multi = 0
    for t in shared:
        if len(amap[t]) > 1 or len(bmap[t]) > 1:
            multi += 1
    return {
        "shared_t_count": int(len(shared)),
        "multi_event_t_count": int(multi),
        "multi_event_t_rate": float(multi / len(shared)),
    }


def pair_event_anchor_nearest(A: List[Event], B: List[Event], window: float, anchor_side: str = "A") -> List[Tuple[Event, Event]]:
    if anchor_side == "B":
        inv = pair_event_anchor_nearest(B, A, window, anchor_side="A")
        return [(b, a) for (a, b) in inv]
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


def _cell_key(sa: int, sb: int) -> str:
    if sa == 0 and sb == 0:
        return "ab"
    if sa == 0 and sb == 1:
        return "abp"
    if sa == 1 and sb == 0:
        return "apb"
    return "apbp"


def E_from_pairs(pairs: List[Tuple[Event, Event]], metric: str, fixed_den: Dict[str, float] | None = None) -> Dict[str, float]:
    if not pairs:
        return {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    ba = np.asarray([p[0].out_bin for p in pairs], dtype=np.float64)
    bb = np.asarray([p[1].out_bin for p in pairs], dtype=np.float64)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)
    out = {}
    for k, m in {
        "ab": (sa == 0) & (sb == 0),
        "abp": (sa == 0) & (sb == 1),
        "apb": (sa == 1) & (sb == 0),
        "apbp": (sa == 1) & (sb == 1),
    }.items():
        if not np.any(m):
            out[k] = 0.0
            continue
        if metric == "binary":
            out[k] = float(np.mean(ba[m] * bb[m]))
        elif metric == "cont_raw":
            out[k] = float(np.mean(xa[m] * xb[m]))
        elif metric == "cont_norm":
            num = float(np.mean(xa[m] * xb[m]))
            den = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
            out[k] = num / den
        else:
            num = float(np.mean(xa[m] * xb[m]))
            den = float(max(1e-12, (fixed_den or {}).get(k, 1.0)))
            out[k] = num / den
    return out


def fixed_den_from_pairs(pairs: List[Tuple[Event, Event]]) -> Dict[str, float]:
    E = E_from_pairs(pairs, "cont_norm")
    # reconstruct per-cell den by direct compute for transparency
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)
    out = {}
    for k, m in {
        "ab": (sa == 0) & (sb == 0),
        "abp": (sa == 0) & (sb == 1),
        "apb": (sa == 1) & (sb == 0),
        "apbp": (sa == 1) & (sb == 1),
    }.items():
        if not np.any(m):
            out[k] = 1.0
        else:
            out[k] = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
    _ = E
    return out


def split_train_test_by_time(pairs: List[Tuple[Event, Event]]) -> Tuple[List[Tuple[Event, Event]], List[Tuple[Event, Event]]]:
    if not pairs:
        return [], []
    t = np.asarray([p[0].t for p in pairs], dtype=np.float64)
    med = float(np.median(t))
    train = [p for p in pairs if p[0].t <= med]
    test = [p for p in pairs if p[0].t > med]
    return train, test


def S(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def E_external_bucket_all(A: List[Event], B: List[Event], window: float, offset: float, metric: str, fixed_den: Dict[str, float] | None = None) -> Tuple[Dict[str, float], int]:
    if window <= 0:
        p = pair_same_index(A, B)
        return E_from_pairs(p, metric, fixed_den=fixed_den), len(p)

    bins_a: Dict[int, List[Event]] = {}
    bins_b: Dict[int, List[Event]] = {}
    for e in A:
        bi = int(np.floor((e.t - offset) / window))
        bins_a.setdefault(bi, []).append(e)
    for e in B:
        bi = int(np.floor((e.t - offset) / window))
        bins_b.setdefault(bi, []).append(e)

    sum_num = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sum_x2 = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sum_y2 = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    cnt = {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    total_pairs = 0

    for bi, aa in bins_a.items():
        bb = bins_b.get(bi, [])
        if not bb:
            continue
        a_by = {0: [], 1: []}
        b_by = {0: [], 1: []}
        for e in aa:
            a_by[e.setting].append(e)
        for e in bb:
            b_by[e.setting].append(e)
        for sa in (0, 1):
            for sb in (0, 1):
                la = a_by[sa]
                lb = b_by[sb]
                if not la or not lb:
                    continue
                n_pairs = len(la) * len(lb)
                total_pairs += n_pairs
                k = _cell_key(sa, sb)
                if metric == "binary":
                    sum_num[k] += float(np.sum([e.out_bin for e in la])) * float(np.sum([e.out_bin for e in lb]))
                else:
                    sum_num[k] += float(np.sum([e.x_cont for e in la])) * float(np.sum([e.x_cont for e in lb]))
                    if metric == "cont_norm":
                        sum_x2[k] += float(np.sum([e.x_cont * e.x_cont for e in la])) * len(lb)
                        sum_y2[k] += float(np.sum([e.x_cont * e.x_cont for e in lb])) * len(la)
                cnt[k] += float(n_pairs)

    E = {}
    for k in ("ab", "abp", "apb", "apbp"):
        if cnt[k] <= 0:
            E[k] = 0.0
            continue
        num = sum_num[k] / cnt[k]
        if metric in ("binary", "cont_raw"):
            E[k] = float(num)
        elif metric == "cont_norm":
            ex2 = sum_x2[k] / cnt[k]
            ey2 = sum_y2[k] / cnt[k]
            E[k] = float(num / np.sqrt(max(1e-12, ex2 * ey2)))
        else:
            E[k] = float(num / max(1e-12, (fixed_den or {}).get(k, 1.0)))
    return E, int(total_pairs)


def bootstrap_ci_pairs(pairs: List[Tuple[Event, Event]], metric: str, n_boot: int, seed: int) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    if not pairs:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan")}
    n = len(pairs)
    idx = np.arange(n)
    svals = np.zeros(n_boot, dtype=np.float64)
    for i in range(n_boot):
        sel = rng.choice(idx, size=n, replace=True)
        samp = [pairs[int(j)] for j in sel]
        svals[i] = S(E_from_pairs(samp, metric))
    return {"mean": float(np.mean(svals)), "lo": float(np.quantile(svals, 0.025)), "hi": float(np.quantile(svals, 0.975))}


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST unified semantics audit v4")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--window", type=float, default=15.0)
    ap.add_argument("--n-boot", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20260429)
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v4.json")
    args = ap.parse_args()

    A, B, filter_diag = load_side_events_from_hdf5(args.hdf5)
    multi_diag = same_index_multi_diag(A, B)

    p_same = pair_same_index(A, B, drop_multi_t=False)
    p_same_strict = pair_same_index(A, B, drop_multi_t=True)
    p_evt_a = pair_event_anchor_nearest(A, B, args.window, anchor_side="A")
    p_evt_b = pair_event_anchor_nearest(A, B, args.window, anchor_side="B")

    # fixed den split (U4 hardening)
    train, test = split_train_test_by_time(p_same)
    den_split = fixed_den_from_pairs(train)

    # offset sensitivity scan for external bucket all (U1 hardening)
    offset_rows = []
    for off in range(int(args.window)):
        Eb, cnt = E_external_bucket_all(A, B, args.window, float(off), "binary")
        En, _ = E_external_bucket_all(A, B, args.window, float(off), "cont_norm")
        Ef, _ = E_external_bucket_all(A, B, args.window, float(off), "cont_norm_fixedden", fixed_den=den_split)
        offset_rows.append(
            {
                "offset": int(off),
                "pair_count": cnt,
                "S_binary_chsh": S(Eb),
                "S_cont_norm_corr": S(En),
                "S_cont_norm_fixedden_corr": S(Ef),
            }
        )

    # primary offset=0
    r0 = next(r for r in offset_rows if r["offset"] == 0)

    # CIs (U3 hardening) for key pair-based modes
    ci = {
        "same_index_binary_chsh": bootstrap_ci_pairs(p_same, "binary", args.n_boot, args.seed + 1),
        "same_index_strict_binary_chsh": bootstrap_ci_pairs(p_same_strict, "binary", args.n_boot, args.seed + 2),
        "event_anchor_A_binary_chsh": bootstrap_ci_pairs(p_evt_a, "binary", args.n_boot, args.seed + 3),
        "event_anchor_B_binary_chsh": bootstrap_ci_pairs(p_evt_b, "binary", args.n_boot, args.seed + 4),
    }

    out = {
        "version": "nist-unified-semantics-audit-v4",
        "hdf5": os.path.abspath(args.hdf5),
        "window": float(args.window),
        "n_boot": int(args.n_boot),
        "fixes": {
            "F1_bucket_edge_offset_scan": True,
            "F2_same_index_strict_mode": True,
            "F3_bootstrap_ci_integrated": True,
            "F4_fixed_den_split": True,
            "F5_anchor_symmetry_check": True,
        },
        "diagnostics_U5_multi_event": multi_diag,
        "diagnostics_U7_filtering": filter_diag,
        "same_index": {
            "pair_count": len(p_same),
            "S_binary_chsh": S(E_from_pairs(p_same, "binary")),
            "S_cont_norm_corr": S(E_from_pairs(p_same, "cont_norm")),
        },
        "same_index_strict": {
            "pair_count": len(p_same_strict),
            "S_binary_chsh": S(E_from_pairs(p_same_strict, "binary")),
            "S_cont_norm_corr": S(E_from_pairs(p_same_strict, "cont_norm")),
        },
        "event_anchor_symmetry": {
            "A_anchor_pair_count": len(p_evt_a),
            "B_anchor_pair_count": len(p_evt_b),
            "A_anchor_S_binary_chsh": S(E_from_pairs(p_evt_a, "binary")),
            "B_anchor_S_binary_chsh": S(E_from_pairs(p_evt_b, "binary")),
            "delta_abs": abs(S(E_from_pairs(p_evt_a, "binary")) - S(E_from_pairs(p_evt_b, "binary"))),
        },
        "external_bucket_offset_scan": {
            "offset0_snapshot": r0,
            "S_binary_min": float(np.min([r["S_binary_chsh"] for r in offset_rows])),
            "S_binary_max": float(np.max([r["S_binary_chsh"] for r in offset_rows])),
            "S_binary_range": float(np.max([r["S_binary_chsh"] for r in offset_rows]) - np.min([r["S_binary_chsh"] for r in offset_rows])),
            "rows": offset_rows,
        },
        "fixed_den_split_info": {
            "train_pairs": len(train),
            "test_pairs": len(test),
            "note": "cont_norm_fixedden uses denominator learned on train half only.",
            "offset0_S_cont_norm_fixedden_corr": r0["S_cont_norm_fixedden_corr"],
        },
        "bootstrap_ci": ci,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("saved:", args.out_json)
    print("same_index S_binary =", out["same_index"]["S_binary_chsh"])
    print("same_index_strict S_binary =", out["same_index_strict"]["S_binary_chsh"])
    print("external offset range S_binary =", out["external_bucket_offset_scan"]["S_binary_range"])
    print("event anchor delta(A vs B) =", out["event_anchor_symmetry"]["delta_abs"])


if __name__ == "__main__":
    main()
