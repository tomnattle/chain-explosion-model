"""
Validation sanity pack for strict 2D E(Delta) evaluation.

Purpose:
1) Compare unconstrained vs constrained LowCos.
2) Report two metrics: CV binomial NLL and CV Brier.
3) Compare LOBO (leave-1-bin-out) and L2O (leave-2-bins-out).
"""

import argparse
import itertools
from pathlib import Path
from typing import Dict, Tuple

import h5py
import numpy as np


def build_slot_lut() -> np.ndarray:
    lut = np.full(65536, -1, dtype=np.int16)
    for k in range(16):
        lut[1 << k] = k
    return lut


def outcome_from_mapping(k: np.ndarray, mode: str) -> np.ndarray:
    if mode == "half_split":
        return np.where(k < 8, 1, -1)
    if mode == "parity":
        return np.where((k % 2) == 0, 1, -1)
    if mode == "quadrant_split":
        return np.where(((k < 4) | ((k >= 8) & (k < 12))), 1, -1)
    raise ValueError(f"unknown mapping: {mode}")


def aggregate_counts(h5_path: Path, chunk_size: int, mapping: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    lut = build_slot_lut()
    cnt = np.zeros(9, dtype=np.int64)
    cnt_plus = np.zeros(9, dtype=np.int64)
    with h5py.File(h5_path, "r") as h5:
        a_clicks = h5["alice/clicks"]
        b_clicks = h5["bob/clicks"]
        n = int(a_clicks.shape[0])
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            ka = lut[a_clicks[start:end]]
            kb = lut[b_clicks[start:end]]
            valid = (ka >= 0) & (kb >= 0)
            if not np.any(valid):
                continue
            ka = ka[valid].astype(np.int16)
            kb = kb[valid].astype(np.int16)
            d = np.abs(ka - kb).astype(np.int16)
            d = np.minimum(d, 16 - d)
            oa = outcome_from_mapping(ka, mapping).astype(np.int8)
            ob = outcome_from_mapping(kb, mapping).astype(np.int8)
            z = oa * ob
            plus = (z == 1).astype(np.int8)
            cnt += np.bincount(d, minlength=9).astype(np.int64)
            cnt_plus += np.bincount(d, weights=plus, minlength=9).astype(np.int64)
    good = cnt > 0
    d_idx = np.arange(9)[good]
    delta = d_idx.astype(np.float64) * 22.5
    total = cnt[good].astype(np.int64)
    plus = cnt_plus[good].astype(np.int64)
    return delta, total, plus


def bell_polyline(delta_deg: np.ndarray) -> np.ndarray:
    x = np.asarray(delta_deg, dtype=np.float64)
    y = np.empty_like(x)
    left = x <= 90.0
    y[left] = 1.0 - (4.0 / 180.0) * x[left]
    y[~left] = -3.0 + (4.0 / 180.0) * x[~left]
    return y


def fit_low(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> Tuple[float, float]:
    x = np.deg2rad(delta_deg)
    X = np.column_stack([np.cos(x), np.ones_like(x)])
    sw = np.sqrt(w.astype(np.float64))
    beta, _, _, _ = np.linalg.lstsq(X * sw[:, None], e_data * sw, rcond=None)
    return float(beta[0]), float(beta[1])


def fit_high_sign(delta_deg: np.ndarray, e_data: np.ndarray, w: np.ndarray) -> float:
    c = np.cos(np.deg2rad(delta_deg))
    score = float(np.sum(w * e_data * c))
    return 1.0 if score >= 0 else -1.0


def e_to_p(e: np.ndarray) -> np.ndarray:
    return np.clip((1.0 + e) * 0.5, 1e-12, 1.0 - 1e-12)


def nll_binom(plus: np.ndarray, total: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return float(-np.sum(plus * np.log(p) + (total - plus) * np.log(1.0 - p)))


def brier_binom(plus: np.ndarray, total: np.ndarray, p: np.ndarray) -> float:
    y = plus.astype(np.float64) / total.astype(np.float64)
    return float(np.sum(total.astype(np.float64) * (y - p) ** 2) / np.sum(total))


def evaluate_split(
    delta: np.ndarray, total: np.ndarray, plus: np.ndarray, test_idx: np.ndarray, constrain_low: bool
) -> Dict[str, float]:
    n = len(delta)
    tr = np.ones(n, dtype=bool)
    tr[test_idx] = False
    te = ~tr

    d_tr = delta[tr]
    w_tr = total[tr]
    y_tr = 2.0 * (plus[tr].astype(np.float64) / w_tr.astype(np.float64)) - 1.0
    d_te = delta[te]
    total_te = total[te]
    plus_te = plus[te]

    a, b = fit_low(d_tr, y_tr, w_tr)
    s = fit_high_sign(d_tr, y_tr, w_tr)

    e_bell = bell_polyline(d_te)
    e_low = a * np.cos(np.deg2rad(d_te)) + b
    if constrain_low:
        e_low = np.clip(e_low, -1.0, 1.0)
    e_high = s * np.cos(np.deg2rad(d_te))

    p_bell = e_to_p(e_bell)
    p_low = e_to_p(e_low)
    p_high = e_to_p(e_high)

    return {
        "nll_bell": nll_binom(plus_te, total_te, p_bell),
        "nll_low": nll_binom(plus_te, total_te, p_low),
        "nll_high": nll_binom(plus_te, total_te, p_high),
        "brier_bell": brier_binom(plus_te, total_te, p_bell),
        "brier_low": brier_binom(plus_te, total_te, p_low),
        "brier_high": brier_binom(plus_te, total_te, p_high),
    }


def run_cv(delta: np.ndarray, total: np.ndarray, plus: np.ndarray, leave_k: int, constrain_low: bool) -> Dict[str, float]:
    n = len(delta)
    combos = list(itertools.combinations(range(n), leave_k))
    agg = {
        "nll_bell": 0.0,
        "nll_low": 0.0,
        "nll_high": 0.0,
        "brier_bell": 0.0,
        "brier_low": 0.0,
        "brier_high": 0.0,
    }
    for c in combos:
        r = evaluate_split(delta, total, plus, np.array(c, dtype=int), constrain_low=constrain_low)
        for k in agg:
            agg[k] += r[k]
    m = float(len(combos))
    for k in agg:
        agg[k] /= m
    return agg


def main() -> None:
    ap = argparse.ArgumentParser(description="Sanity-check strict 2D validation logic")
    ap.add_argument("--hdf5", default="data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5")
    ap.add_argument("--mapping", default="half_split", choices=["half_split", "parity", "quadrant_split"])
    ap.add_argument("--chunk-size", type=int, default=8_000_000)
    ap.add_argument("--out-md", default="artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md")
    args = ap.parse_args()

    h5_path = Path(args.hdf5)
    delta, total, plus = aggregate_counts(h5_path, args.chunk_size, args.mapping)

    l1_raw = run_cv(delta, total, plus, leave_k=1, constrain_low=False)
    l1_clip = run_cv(delta, total, plus, leave_k=1, constrain_low=True)
    l2_raw = run_cv(delta, total, plus, leave_k=2, constrain_low=False)
    l2_clip = run_cv(delta, total, plus, leave_k=2, constrain_low=True)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# NIST 严格2D验证逻辑排查\n\n")
        f.write(f"- 数据: `{h5_path.as_posix()}`\n")
        f.write(f"- 映射: `{args.mapping}`\n")
        f.write("- 目标: 检查“后期变差”是否由验证逻辑本身导致。\n\n")
        f.write("## 结果总表（越小越好）\n\n")
        f.write("| 设置 | NLL Bell | NLL Low(raw) | NLL High | Brier Bell | Brier Low(raw) | Brier High |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        f.write(
            f"| LOBO raw | {l1_raw['nll_bell']:.6f} | {l1_raw['nll_low']:.6f} | {l1_raw['nll_high']:.6f} | "
            f"{l1_raw['brier_bell']:.6f} | {l1_raw['brier_low']:.6f} | {l1_raw['brier_high']:.6f} |\n"
        )
        f.write(
            f"| LOBO low-clipped | {l1_clip['nll_bell']:.6f} | {l1_clip['nll_low']:.6f} | {l1_clip['nll_high']:.6f} | "
            f"{l1_clip['brier_bell']:.6f} | {l1_clip['brier_low']:.6f} | {l1_clip['brier_high']:.6f} |\n"
        )
        f.write(
            f"| L2O raw | {l2_raw['nll_bell']:.6f} | {l2_raw['nll_low']:.6f} | {l2_raw['nll_high']:.6f} | "
            f"{l2_raw['brier_bell']:.6f} | {l2_raw['brier_low']:.6f} | {l2_raw['brier_high']:.6f} |\n"
        )
        f.write(
            f"| L2O low-clipped | {l2_clip['nll_bell']:.6f} | {l2_clip['nll_low']:.6f} | {l2_clip['nll_high']:.6f} | "
            f"{l2_clip['brier_bell']:.6f} | {l2_clip['brier_low']:.6f} | {l2_clip['brier_high']:.6f} |\n"
        )
        f.write("\n")
        f.write("## 排查结论模板\n\n")
        f.write("- 若 `low-clipped` 显著优于 `low-raw`：说明前期LowCos失真有边界问题。\n")
        f.write("- 若 NLL 与 Brier 赢家一致：说明不是单指标偏见。\n")
        f.write("- 若 LOBO 与 L2O 赢家一致：说明不是留一策略过严导致。\n")

    print("wrote", out_md)


if __name__ == "__main__":
    main()
