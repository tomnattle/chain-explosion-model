"""
nist_unified_semantics_audit_v3.py
----------------------------------
Adds U4/U5/U7 checks on top of v2:
U4: cont_norm_fixedden (fixed denominator from same-index baseline)
U5: same-index multi-event timestamp diagnostics
U7: one-hot filtering impact diagnostics
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


def load_arrays(hdf5_path: str):
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5["alice/clicks"][()]
        cb = h5["bob/clicks"][()]
        sa = h5["alice/settings"][()]
        sb = h5["bob/settings"][()]
    return ca, cb, sa, sb


def load_side_events_from_hdf5(hdf5_path: str) -> Tuple[List[Event], List[Event], Dict[str, float]]:
    ca, cb, sa, sb = load_arrays(hdf5_path)
    ia = slot_index_from_click_uint16(ca)
    ib = slot_index_from_click_uint16(cb)

    # U7 diagnostics: filtering impact
    pre_a = (ca > 0) & ((sa == 1) | (sa == 2))
    pre_b = (cb > 0) & ((sb == 1) | (sb == 2))
    post_a = pre_a & (ia >= 0)
    post_b = pre_b & (ib >= 0)

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

    diag = {
        "pre_filter_A_events": int(np.sum(pre_a)),
        "pre_filter_B_events": int(np.sum(pre_b)),
        "post_filter_A_events": int(np.sum(post_a)),
        "post_filter_B_events": int(np.sum(post_b)),
        "drop_ratio_A": float(1.0 - (np.sum(post_a) / max(1, np.sum(pre_a)))),
        "drop_ratio_B": float(1.0 - (np.sum(post_b) / max(1, np.sum(pre_b)))),
    }
    return A, B, diag


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


def same_index_multi_event_diag(A: List[Event], B: List[Event]) -> Dict[str, float]:
    from collections import defaultdict

    amap = defaultdict(int)
    bmap = defaultdict(int)
    for e in A:
        amap[e.t] += 1
    for e in B:
        bmap[e.t] += 1

    shared_t = set(amap.keys()) & set(bmap.keys())
    if not shared_t:
        return {
            "shared_t_count": 0,
            "multi_event_t_count": 0,
            "multi_event_t_rate": 0.0,
            "max_A_count_same_t": 0,
            "max_B_count_same_t": 0,
        }
    multi = 0
    max_a = 0
    max_b = 0
    for t in shared_t:
        ca = amap[t]
        cb = bmap[t]
        max_a = max(max_a, ca)
        max_b = max(max_b, cb)
        if ca > 1 or cb > 1:
            multi += 1
    return {
        "shared_t_count": int(len(shared_t)),
        "multi_event_t_count": int(multi),
        "multi_event_t_rate": float(multi / len(shared_t)),
        "max_A_count_same_t": int(max_a),
        "max_B_count_same_t": int(max_b),
    }


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


def E_from_pairs(pairs: List[Tuple[Event, Event]], metric: str, fixed_den: Dict[str, float] | None = None) -> Dict[str, float]:
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
        elif metric == "cont_norm":
            num = float(np.mean(xa[m] * xb[m]))
            den = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
            out[key] = num / den
        else:  # cont_norm_fixedden
            num = float(np.mean(xa[m] * xb[m]))
            den = float(max(1e-12, (fixed_den or {}).get(key, 1.0)))
            out[key] = num / den
    return out


def fixed_den_from_pairs(pairs: List[Tuple[Event, Event]]) -> Dict[str, float]:
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)
    out = {}
    for key, m in {
        "ab": (sa == 0) & (sb == 0),
        "abp": (sa == 0) & (sb == 1),
        "apb": (sa == 1) & (sb == 0),
        "apbp": (sa == 1) & (sb == 1),
    }.items():
        if not np.any(m):
            out[key] = 1.0
        else:
            out[key] = float(np.sqrt(max(1e-12, float(np.mean(xa[m] * xa[m])) * float(np.mean(xb[m] * xb[m])))))
    return out


def E_external_bucket_all(A: List[Event], B: List[Event], window: float, metric: str, fixed_den: Dict[str, float] | None = None) -> Tuple[Dict[str, float], int]:
    if window <= 0:
        p = pair_same_index(A, B)
        return E_from_pairs(p, metric, fixed_den=fixed_den), len(p)

    bins_a: Dict[int, List[Event]] = {}
    bins_b: Dict[int, List[Event]] = {}
    for e in A:
        bi = int(np.floor(e.t / window))
        bins_a.setdefault(bi, []).append(e)
    for e in B:
        bi = int(np.floor(e.t / window))
        bins_b.setdefault(bi, []).append(e)

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
        stats_a = {0: [], 1: []}
        stats_b = {0: [], 1: []}
        for e in aa:
            stats_a[e.setting].append(e)
        for e in bb:
            stats_b[e.setting].append(e)
        for sa0 in (0, 1):
            for sb0 in (0, 1):
                la = stats_a[sa0]
                lb = stats_b[sb0]
                if not la or not lb:
                    continue
                na = len(la)
                nb = len(lb)
                n_pairs = na * nb
                total_pairs += n_pairs
                k = key(sa0, sb0)
                if metric == "binary":
                    sum_num[k] += float(np.sum([e.out_bin for e in la])) * float(np.sum([e.out_bin for e in lb]))
                else:
                    sum_num[k] += float(np.sum([e.x_cont for e in la])) * float(np.sum([e.x_cont for e in lb]))
                    if metric == "cont_norm":
                        sum_x2[k] += float(np.sum([e.x_cont * e.x_cont for e in la])) * nb
                        sum_y2[k] += float(np.sum([e.x_cont * e.x_cont for e in lb])) * na
                cnt[k] += float(n_pairs)

    E = {}
    for k in ("ab", "abp", "apb", "apbp"):
        if cnt[k] <= 0:
            E[k] = 0.0
            continue
        num_mean = sum_num[k] / cnt[k]
        if metric == "binary" or metric == "cont_raw":
            E[k] = float(num_mean)
        elif metric == "cont_norm":
            ex2 = sum_x2[k] / cnt[k]
            ey2 = sum_y2[k] / cnt[k]
            E[k] = float(num_mean / np.sqrt(max(1e-12, ex2 * ey2)))
        else:
            den = float(max(1e-12, (fixed_den or {}).get(k, 1.0)))
            E[k] = float(num_mean / den)
    return E, int(total_pairs)


def S(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def run_modes(A: List[Event], B: List[Event], window: float, fixed_den: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    p_same = pair_same_index(A, B)
    p_evt = pair_event_anchor_nearest(A, B, window)
    p_ext_n = pair_external_clock_nearest_1to1(A, B, window)
    E_ext_b, c_ext = E_external_bucket_all(A, B, window, "binary", fixed_den=fixed_den)
    E_ext_r, _ = E_external_bucket_all(A, B, window, "cont_raw", fixed_den=fixed_den)
    E_ext_n, _ = E_external_bucket_all(A, B, window, "cont_norm", fixed_den=fixed_den)
    E_ext_f, _ = E_external_bucket_all(A, B, window, "cont_norm_fixedden", fixed_den=fixed_den)

    def row_from_pairs(pairs: List[Tuple[Event, Event]], role: str) -> Dict[str, float]:
        return {
            "role": role,
            "pair_count": len(pairs),
            "S_binary_chsh": S(E_from_pairs(pairs, "binary", fixed_den=fixed_den)),
            "S_cont_raw_corr": S(E_from_pairs(pairs, "cont_raw", fixed_den=fixed_den)),
            "S_cont_norm_corr": S(E_from_pairs(pairs, "cont_norm", fixed_den=fixed_den)),
            "S_cont_norm_fixedden_corr": S(E_from_pairs(pairs, "cont_norm_fixedden", fixed_den=fixed_den)),
        }

    return {
        "same_index": row_from_pairs(p_same, "baseline"),
        "external_clock_bucket_all": {
            "role": "primary_external_clock",
            "pair_count": c_ext,
            "S_binary_chsh": S(E_ext_b),
            "S_cont_raw_corr": S(E_ext_r),
            "S_cont_norm_corr": S(E_ext_n),
            "S_cont_norm_fixedden_corr": S(E_ext_f),
        },
        "external_clock_nearest_1to1": row_from_pairs(p_ext_n, "loophole_probe"),
        "event_anchor_nearest": row_from_pairs(p_evt, "loophole_probe"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="NIST unified semantics audit v3")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--window", type=float, default=15.0)
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v3.json")
    args = ap.parse_args()

    A, B, filter_diag = load_side_events_from_hdf5(args.hdf5)
    multi_diag = same_index_multi_event_diag(A, B)
    fixed_den = fixed_den_from_pairs(pair_same_index(A, B))
    modes = run_modes(A, B, args.window, fixed_den=fixed_den)

    out = {
        "version": "nist-unified-semantics-audit-v3",
        "hdf5": os.path.abspath(args.hdf5),
        "window": float(args.window),
        "fixed_den_source": "same_index per-cell second moments",
        "diagnostics_U5_same_index_multi_event": multi_diag,
        "diagnostics_U7_filtering": filter_diag,
        "modes": modes,
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("same_index S_binary_chsh =", modes["same_index"]["S_binary_chsh"])
    print("same_index S_cont_norm_corr =", modes["same_index"]["S_cont_norm_corr"])
    print("same_index S_cont_norm_fixedden_corr =", modes["same_index"]["S_cont_norm_fixedden_corr"])
    print("external_bucket_all S_binary_chsh =", modes["external_clock_bucket_all"]["S_binary_chsh"])
    print("drop_ratio_A =", filter_diag["drop_ratio_A"], "drop_ratio_B =", filter_diag["drop_ratio_B"])
    print("multi_event_t_rate =", multi_diag["multi_event_t_rate"])
    print("saved:", args.out_json)


if __name__ == "__main__":
    main()
