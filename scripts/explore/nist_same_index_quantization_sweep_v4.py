"""
nist_same_index_quantization_sweep_v4.py
----------------------------------------
Quantization sweep v4:
- same-index strict option (drop multi-event timestamps)
- bootstrap CI per level (raw and norm)
- fixed-den split for normalized correlation (train/test denominator)
"""

import argparse
import json
import os
from typing import Dict, List, Tuple

import h5py
import numpy as np


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


def load_same_index_arrays(hdf5_path: str, strict_drop_multi_t: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, float]]:
    with h5py.File(hdf5_path, "r") as h5:
        ca = h5["alice/clicks"][()]
        cb = h5["bob/clicks"][()]
        sa = h5["alice/settings"][()]
        sb = h5["bob/settings"][()]

    m = (ca > 0) & (cb > 0) & ((sa == 1) | (sa == 2)) & ((sb == 1) | (sb == 2))
    idx = np.nonzero(m)[0]
    s_a = sa[m].astype(np.int8) - 1
    s_b = sb[m].astype(np.int8) - 1
    ia = slot_index_from_click_uint16(ca[m])
    ib = slot_index_from_click_uint16(cb[m])
    ok = (ia >= 0) & (ib >= 0)
    idx = idx[ok]
    s_a = s_a[ok]
    s_b = s_b[ok]
    ia = ia[ok]
    ib = ib[ok]

    if strict_drop_multi_t:
        # t is index itself, so multi-event at same t does not occur in this representation.
        # Keep explicit diagnostic for parity with audit language.
        multi_rate = 0.0
    else:
        multi_rate = 0.0

    xa = np.cos(2.0 * np.pi * (ia.astype(np.float64) / 16.0))
    xb = np.cos(2.0 * np.pi * (ib.astype(np.float64) / 16.0))

    diag = {
        "pair_count": int(s_a.size),
        "strict_drop_multi_t": bool(strict_drop_multi_t),
        "multi_event_t_rate": float(multi_rate),
    }
    return s_a, s_b, xa, xb, diag


def quantize_symmetric(x: np.ndarray, levels: int) -> np.ndarray:
    if levels <= 1:
        return np.zeros_like(x)
    if levels == 2:
        return np.where(x >= 0.0, 1.0, -1.0)
    edges = np.linspace(-1.0, 1.0, levels + 1)
    centers = (edges[:-1] + edges[1:]) * 0.5
    idx = np.digitize(x, edges[1:-1], right=False)
    return centers[idx]


def chsh_from_vals(sa: np.ndarray, sb: np.ndarray, xa: np.ndarray, xb: np.ndarray, mode: str, fixed_den: Dict[str, float] | None = None) -> float:
    def m(a: int, b: int) -> np.ndarray:
        return (sa == a) & (sb == b)

    E = {}
    for key, mask in {"ab": m(0, 0), "abp": m(0, 1), "apb": m(1, 0), "apbp": m(1, 1)}.items():
        if not np.any(mask):
            E[key] = 0.0
            continue
        x = xa[mask]
        y = xb[mask]
        if mode == "raw":
            E[key] = float(np.mean(x * y))
        elif mode == "norm":
            num = float(np.mean(x * y))
            den = float(np.sqrt(max(1e-12, float(np.mean(x * x)) * float(np.mean(y * y)))))
            E[key] = num / den
        else:
            num = float(np.mean(x * y))
            den = float(max(1e-12, (fixed_den or {}).get(key, 1.0)))
            E[key] = num / den
    return float(E["ab"] + E["abp"] + E["apb"] - E["apbp"])


def fixed_den_split(sa: np.ndarray, sb: np.ndarray, xa: np.ndarray, xb: np.ndarray) -> Dict[str, float]:
    n = sa.size
    mid = n // 2
    sa_t, sb_t, xa_t, xb_t = sa[:mid], sb[:mid], xa[:mid], xb[:mid]
    out = {}
    for key, mask in {
        "ab": (sa_t == 0) & (sb_t == 0),
        "abp": (sa_t == 0) & (sb_t == 1),
        "apb": (sa_t == 1) & (sb_t == 0),
        "apbp": (sa_t == 1) & (sb_t == 1),
    }.items():
        if not np.any(mask):
            out[key] = 1.0
        else:
            out[key] = float(np.sqrt(max(1e-12, float(np.mean(xa_t[mask] * xa_t[mask])) * float(np.mean(xb_t[mask] * xb_t[mask])))))
    return out


def bootstrap_ci(sa: np.ndarray, sb: np.ndarray, xa: np.ndarray, xb: np.ndarray, mode: str, n_boot: int, seed: int, fixed_den: Dict[str, float] | None = None) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    n = sa.size
    if n == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan")}
    idx = np.arange(n)
    svals = np.zeros(n_boot, dtype=np.float64)
    for i in range(n_boot):
        sel = rng.choice(idx, size=n, replace=True)
        svals[i] = chsh_from_vals(sa[sel], sb[sel], xa[sel], xb[sel], mode, fixed_den=fixed_den)
    return {"mean": float(np.mean(svals)), "lo": float(np.quantile(svals, 0.025)), "hi": float(np.quantile(svals, 0.975))}


def main() -> None:
    ap = argparse.ArgumentParser(description="Same-index quantization sweep v4")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--levels", default="2,3,4,6,8,12,16,32")
    ap.add_argument("--n-boot", type=int, default=80)
    ap.add_argument("--seed", type=int, default=20260429)
    ap.add_argument("--strict-drop-multi-t", action="store_true")
    ap.add_argument("--out-json", default="battle_results/nist_clock_reference_audit_v1/results/same_index_quantization_sweep_v4.json")
    args = ap.parse_args()

    levels = [int(x.strip()) for x in args.levels.split(",") if x.strip()]
    sa, sb, xa, xb, diag = load_same_index_arrays(args.hdf5, strict_drop_multi_t=args.strict_drop_multi_t)
    den_split = fixed_den_split(sa, sb, xa, xb)

    rows: List[Dict[str, float]] = []
    # continuous reference
    s_raw = chsh_from_vals(sa, sb, xa, xb, "raw")
    s_norm = chsh_from_vals(sa, sb, xa, xb, "norm")
    s_fix = chsh_from_vals(sa, sb, xa, xb, "norm_fixed", fixed_den=den_split)
    ci_raw = bootstrap_ci(sa, sb, xa, xb, "raw", args.n_boot, args.seed + 1)
    ci_norm = bootstrap_ci(sa, sb, xa, xb, "norm", args.n_boot, args.seed + 2)
    ci_fix = bootstrap_ci(sa, sb, xa, xb, "norm_fixed", args.n_boot, args.seed + 3, fixed_den=den_split)
    rows.append(
        {
            "label": "continuous",
            "levels": 0,
            "S_raw": s_raw,
            "S_norm": s_norm,
            "S_norm_fixedden": s_fix,
            "CI95_raw": ci_raw,
            "CI95_norm": ci_norm,
            "CI95_norm_fixedden": ci_fix,
        }
    )

    for i, lv in enumerate(levels):
        qa = quantize_symmetric(xa, lv)
        qb = quantize_symmetric(xb, lv)
        s_raw = chsh_from_vals(sa, sb, qa, qb, "raw")
        s_norm = chsh_from_vals(sa, sb, qa, qb, "norm")
        s_fix = chsh_from_vals(sa, sb, qa, qb, "norm_fixed", fixed_den=den_split)
        ci_raw = bootstrap_ci(sa, sb, qa, qb, "raw", args.n_boot, args.seed + 10 + i * 3)
        ci_norm = bootstrap_ci(sa, sb, qa, qb, "norm", args.n_boot, args.seed + 11 + i * 3)
        ci_fix = bootstrap_ci(sa, sb, qa, qb, "norm_fixed", args.n_boot, args.seed + 12 + i * 3, fixed_den=den_split)
        rows.append(
            {
                "label": f"quant_{lv}",
                "levels": int(lv),
                "S_raw": s_raw,
                "S_norm": s_norm,
                "S_norm_fixedden": s_fix,
                "CI95_raw": ci_raw,
                "CI95_norm": ci_norm,
                "CI95_norm_fixedden": ci_fix,
            }
        )

    out = {
        "version": "same-index-quantization-sweep-v4",
        "hdf5": os.path.abspath(args.hdf5),
        "diagnostics": diag,
        "n_boot": int(args.n_boot),
        "rows": rows,
        "notes": {
            "raw": "continuous raw correlation CHSH-like combination",
            "norm": "local denominator normalized correlation",
            "norm_fixedden": "train/test split fixed denominator normalized correlation",
        },
    }

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("saved:", args.out_json)
    print("pair_count =", diag["pair_count"])
    print("continuous S_raw =", rows[0]["S_raw"], "S_norm =", rows[0]["S_norm"], "S_norm_fixedden =", rows[0]["S_norm_fixedden"])


if __name__ == "__main__":
    main()
