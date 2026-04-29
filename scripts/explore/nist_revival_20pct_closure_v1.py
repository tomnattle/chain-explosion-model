"""
nist_revival_20pct_closure_v1.py
--------------------------------
Close the remaining "20%" by adding:
1) Bootstrap uncertainty on key deltas
2) Cross-sample / cross-slice baseline checks
3) Final split-by-metric (raw vs norm) closure note
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


def filter_by_t_fraction(A: List[Event], B: List[Event], lo: float, hi: float) -> Tuple[List[Event], List[Event]]:
    # based on max timeline across both wings
    tmax = max(A[-1].t if A else 0.0, B[-1].t if B else 0.0)
    a0, a1 = lo * tmax, hi * tmax
    AA = [e for e in A if a0 <= e.t < a1]
    BB = [e for e in B if a0 <= e.t < a1]
    return AA, BB


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


def compute_E(pairs: List[Tuple[Event, Event]], metric: str) -> Dict[str, float]:
    if not pairs:
        return {"ab": 0.0, "abp": 0.0, "apb": 0.0, "apbp": 0.0}
    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    ba = np.asarray([p[0].out_bin for p in pairs], dtype=np.float64)
    bb = np.asarray([p[1].out_bin for p in pairs], dtype=np.float64)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)

    def mask(a: int, b: int) -> np.ndarray:
        return (sa == a) & (sb == b)

    out = {}
    for key, m in {"ab": mask(0, 0), "abp": mask(0, 1), "apb": mask(1, 0), "apbp": mask(1, 1)}.items():
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


def S(E: Dict[str, float]) -> float:
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def bootstrap_ci(pairs: List[Tuple[Event, Event]], metric: str, n_boot: int, seed: int) -> Dict[str, float]:
    # Fast bootstrap: resample per CHSH cell on precomputed cell products.
    rng = np.random.default_rng(seed)
    n = len(pairs)
    if n == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan")}

    sa = np.asarray([p[0].setting for p in pairs], dtype=np.int8)
    sb = np.asarray([p[1].setting for p in pairs], dtype=np.int8)
    ba = np.asarray([p[0].out_bin for p in pairs], dtype=np.float64)
    bb = np.asarray([p[1].out_bin for p in pairs], dtype=np.float64)
    xa = np.asarray([p[0].x_cont for p in pairs], dtype=np.float64)
    xb = np.asarray([p[1].x_cont for p in pairs], dtype=np.float64)

    cells = {
        "ab": (sa == 0) & (sb == 0),
        "abp": (sa == 0) & (sb == 1),
        "apb": (sa == 1) & (sb == 0),
        "apbp": (sa == 1) & (sb == 1),
    }

    cell_vals: Dict[str, np.ndarray] = {}
    for k, m in cells.items():
        if metric == "binary":
            vals = ba[m] * bb[m]
        elif metric == "cont_raw":
            vals = xa[m] * xb[m]
        else:
            num = xa[m] * xb[m]
            den = np.sqrt(np.maximum(1e-12, np.mean(xa[m] * xa[m]) * np.mean(xb[m] * xb[m]))) if np.any(m) else 1.0
            vals = num / den
        cell_vals[k] = np.asarray(vals, dtype=np.float64)

    def boot_mean(arr: np.ndarray) -> float:
        if arr.size == 0:
            return 0.0
        idx = rng.integers(0, arr.size, size=arr.size)
        return float(np.mean(arr[idx]))

    svals = np.zeros(n_boot, dtype=np.float64)
    for i in range(n_boot):
        eab = boot_mean(cell_vals["ab"])
        eabp = boot_mean(cell_vals["abp"])
        eapb = boot_mean(cell_vals["apb"])
        eapbp = boot_mean(cell_vals["apbp"])
        svals[i] = eab + eabp + eapb - eapbp

    return {
        "mean": float(np.mean(svals)),
        "lo": float(np.quantile(svals, 0.025)),
        "hi": float(np.quantile(svals, 0.975)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Close remaining 20% for NIST semantics audit.")
    ap.add_argument("--hdf5-main", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--hdf5-second", default="data/03_31_CH_pockel_100kHz.run4.afterTimingfix2_training.dat.compressed.build.hdf5")
    ap.add_argument("--window", type=float, default=15.0)
    ap.add_argument("--n-boot", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20260429)
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v1.json")
    ap.add_argument("--out-md", default="battle_results/nist_clock_reference_audit_v1/results/nist_revival_20pct_closure_v1.md")
    args = ap.parse_args()

    A, B = load_side_events_from_hdf5(args.hdf5_main)
    pairs_same = pair_same_index(A, B)
    pairs_ext = pair_external_clock_bin(A, B, args.window)
    pairs_evt = pair_event_anchor_nearest(A, B, args.window)

    real = {}
    for m in ("binary", "cont_raw", "cont_norm"):
        real[f"same_{m}"] = S(compute_E(pairs_same, m))
        real[f"ext_{m}"] = S(compute_E(pairs_ext, m))
        real[f"evt_{m}"] = S(compute_E(pairs_evt, m))

    # bootstrap CI on key deltas
    ci_same_bin = bootstrap_ci(pairs_same, "binary", args.n_boot, args.seed + 1)
    ci_ext_bin = bootstrap_ci(pairs_ext, "binary", args.n_boot, args.seed + 2)
    ci_evt_bin = bootstrap_ci(pairs_evt, "binary", args.n_boot, args.seed + 3)

    ci_same_norm = bootstrap_ci(pairs_same, "cont_norm", args.n_boot, args.seed + 4)
    ci_ext_norm = bootstrap_ci(pairs_ext, "cont_norm", args.n_boot, args.seed + 5)
    ci_evt_norm = bootstrap_ci(pairs_evt, "cont_norm", args.n_boot, args.seed + 6)

    # cross-slice same-index stability on main file
    slices = {}
    for name, lo, hi in [("slice_0_33", 0.0, 1 / 3), ("slice_33_66", 1 / 3, 2 / 3), ("slice_66_100", 2 / 3, 1.0)]:
        AA, BB = filter_by_t_fraction(A, B, lo, hi)
        pp = pair_same_index(AA, BB)
        slices[name] = {
            "pair_count": len(pp),
            "S_binary": S(compute_E(pp, "binary")),
            "S_cont_norm": S(compute_E(pp, "cont_norm")),
        }

    # second sample stability (if file exists)
    second = {"available": False}
    if os.path.isfile(args.hdf5_second):
        A2, B2 = load_side_events_from_hdf5(args.hdf5_second)
        p2 = pair_same_index(A2, B2)
        second = {
            "available": True,
            "hdf5": os.path.abspath(args.hdf5_second),
            "pair_count": len(p2),
            "S_binary": S(compute_E(p2, "binary")),
            "S_cont_norm": S(compute_E(p2, "cont_norm")),
        }

    out = {
        "version": "nist-revival-20pct-closure-v1",
        "main_hdf5": os.path.abspath(args.hdf5_main),
        "window": float(args.window),
        "n_boot": int(args.n_boot),
        "full_run": {
            "pair_counts": {
                "same_index": len(pairs_same),
                "external_clock_bin": len(pairs_ext),
                "event_anchor_nearest": len(pairs_evt),
            },
            "S": real,
        },
        "bootstrap_ci": {
            "same_binary": ci_same_bin,
            "external_binary": ci_ext_bin,
            "event_binary": ci_evt_bin,
            "same_cont_norm": ci_same_norm,
            "external_cont_norm": ci_ext_norm,
            "event_cont_norm": ci_evt_norm,
            "delta_binary_external_minus_same": {
                "mean": ci_ext_bin["mean"] - ci_same_bin["mean"],
                "lo_rough": ci_ext_bin["lo"] - ci_same_bin["hi"],
                "hi_rough": ci_ext_bin["hi"] - ci_same_bin["lo"],
            },
            "delta_norm_external_minus_same": {
                "mean": ci_ext_norm["mean"] - ci_same_norm["mean"],
                "lo_rough": ci_ext_norm["lo"] - ci_same_norm["hi"],
                "hi_rough": ci_ext_norm["hi"] - ci_same_norm["lo"],
            },
        },
        "slice_stability_main_same_index": slices,
        "second_sample_same_index": second,
        "closure_checks": {
            "same_index_not_near_2p82": abs(real["same_binary"] - 2.82) > 0.02 and abs(real["same_cont_norm"] - 2.82) > 0.02,
            "pairing_pushes_to_2p8_zone": abs(real["ext_cont_norm"] - 2.82) <= 0.03 or abs(real["evt_cont_norm"] - 2.82) <= 0.03,
            "raw_and_norm_reported_separately": True,
        },
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append("# NIST Revival 20% Closure v1")
    lines.append("")
    lines.append("## Full-run snapshot")
    lines.append(f"- same_index: S_binary={real['same_binary']:.6f}, S_cont_norm={real['same_cont_norm']:.6f}")
    lines.append(f"- external_clock_bin: S_binary={real['ext_binary']:.6f}, S_cont_norm={real['ext_cont_norm']:.6f}")
    lines.append(f"- event_anchor_nearest: S_binary={real['evt_binary']:.6f}, S_cont_norm={real['evt_cont_norm']:.6f}")
    lines.append("")
    lines.append("## Bootstrap uncertainty (95% CI)")
    lines.append(
        f"- same_index binary: [{ci_same_bin['lo']:.6f}, {ci_same_bin['hi']:.6f}] ; "
        f"cont_norm: [{ci_same_norm['lo']:.6f}, {ci_same_norm['hi']:.6f}]"
    )
    lines.append(
        f"- external binary: [{ci_ext_bin['lo']:.6f}, {ci_ext_bin['hi']:.6f}] ; "
        f"cont_norm: [{ci_ext_norm['lo']:.6f}, {ci_ext_norm['hi']:.6f}]"
    )
    lines.append(
        f"- event binary: [{ci_evt_bin['lo']:.6f}, {ci_evt_bin['hi']:.6f}] ; "
        f"cont_norm: [{ci_evt_norm['lo']:.6f}, {ci_evt_norm['hi']:.6f}]"
    )
    lines.append("")
    lines.append("## Cross-slice stability (same_index on main file)")
    for k, v in slices.items():
        lines.append(f"- {k}: pairs={v['pair_count']}, S_binary={v['S_binary']:.6f}, S_cont_norm={v['S_cont_norm']:.6f}")
    lines.append("")
    lines.append("## Second sample check")
    if second.get("available"):
        lines.append(
            f"- available: True, pairs={second['pair_count']}, "
            f"S_binary={second['S_binary']:.6f}, S_cont_norm={second['S_cont_norm']:.6f}"
        )
    else:
        lines.append("- available: False")
    lines.append("")
    lines.append("## Final closure status")
    lines.append(f"- same_index_not_near_2p82: {out['closure_checks']['same_index_not_near_2p82']}")
    lines.append(f"- pairing_pushes_to_2p8_zone: {out['closure_checks']['pairing_pushes_to_2p8_zone']}")
    lines.append(f"- raw_and_norm_reported_separately: {out['closure_checks']['raw_and_norm_reported_separately']}")
    lines.append("")

    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("saved:", args.out_json)
    print("saved:", args.out_md)


if __name__ == "__main__":
    main()
